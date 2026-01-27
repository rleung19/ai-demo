/**
 * Churn Cohorts Route
 * GET /api/kpi/churn/cohorts
 */

import express from 'express';
import { executeQuery } from '../../lib/db/oracle';
import { getCache, setCache } from '../../lib/cache';
import { handleDatabaseError } from '../../lib/api/express-errors';

const router = express.Router();

const CACHE_KEY = 'churn:cohorts';
const CACHE_TTL_MILLISECONDS = 60_000; // 60 seconds

router.get('/', async (req, res) => {
  try {
    const cached = getCache<any>(CACHE_KEY);
    if (cached) {
      return res.json(cached);
    }
    // Query to get cohort breakdown with updated VIP definition
    const cohortsQuery = `
      WITH cohort_assignments AS (
        SELECT 
          cp.USER_ID,
          cp.PREDICTED_CHURN_PROBABILITY,
          cp.PREDICTED_CHURN_LABEL,
          up.LIFETIME_VALUE,
          up.MEMBERSHIP_YEARS,
          up.TOTAL_PURCHASES,
          up.DAYS_SINCE_LAST_PURCHASE,
          up.LOGIN_FREQUENCY,
          au.AFFINITY_CARD,
          CASE 
            WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
            WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
            WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
            WHEN up.TOTAL_PURCHASES >= 2 
                 AND up.DAYS_SINCE_LAST_PURCHASE <= 90 
                 AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
            ELSE 'Other'
          END AS cohort
        FROM OML.CHURN_PREDICTIONS cp
        JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
        JOIN ADMIN.USERS au ON up.USER_ID = au.ID
      )
      SELECT 
        cohort,
        COUNT(*) AS customer_count,
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
        ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
        ROUND(
          AVG(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN PREDICTED_CHURN_PROBABILITY END) * 100,
          2
        ) AS avg_risk_score_at_risk,
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
      FROM cohort_assignments
      WHERE cohort != 'Other'
      GROUP BY cohort
      ORDER BY 
        CASE cohort
          WHEN 'VIP' THEN 1
          WHEN 'Regular' THEN 2
          WHEN 'New' THEN 3
          WHEN 'Dormant' THEN 4
          ELSE 5
        END
    `;

    const result = await executeQuery<{
      COHORT: string;
      CUSTOMER_COUNT: number;
      AT_RISK_COUNT: number;
      AVG_RISK_SCORE: number;
      AVG_RISK_SCORE_AT_RISK: number | null;
      LTV_AT_RISK: number;
    }>(cohortsQuery);

    const cohorts = (result.rows || []).map((row: {
      COHORT: string;
      CUSTOMER_COUNT: number;
      AT_RISK_COUNT: number;
      AVG_RISK_SCORE: number;
      AVG_RISK_SCORE_AT_RISK: number | null;
      LTV_AT_RISK: number;
    }) => ({
      cohort: row.COHORT,
      customerCount: row.CUSTOMER_COUNT,
      atRiskCount: row.AT_RISK_COUNT,
      atRiskPercentage: row.CUSTOMER_COUNT > 0
        ? Math.round((row.AT_RISK_COUNT / row.CUSTOMER_COUNT) * 10000) / 100
        : 0,
      averageRiskScore: row.AVG_RISK_SCORE,
      averageRiskScoreAtRisk: row.AVG_RISK_SCORE_AT_RISK ?? 0,
      ltvAtRisk: Math.round(row.LTV_AT_RISK * 100) / 100,
    }));

    const response = { cohorts };

    setCache(CACHE_KEY, response, CACHE_TTL_MILLISECONDS);
    res.json(response);
  } catch (error: any) {
    if (error.message?.includes('ORA-') || error.message?.includes('database')) {
      return handleDatabaseError(error, res);
    }
    return res.status(503).json({
      error: 'Service unavailable',
      message: error.message || 'Unable to fetch cohort data',
      fallback: true,
    });
  }
});

export default router;
