/**
 * Churn Cohorts Route
 * GET /api/kpi/churn/cohorts
 */

import express from 'express';
import { executeQuery } from '../../lib/db';
import { getCache, setCache } from '../../lib/cache';
import { handleDatabaseError } from '../../lib/api/express-errors';
import { cohortsListQuery, isDatabaseError } from '../../lib/sql/churn-queries';

const router = express.Router();

const CACHE_KEY = 'churn:cohorts';
const CACHE_TTL_MILLISECONDS = 60_000;

router.get('/', async (req, res) => {
  try {
    const cached = getCache<any>(CACHE_KEY);
    if (cached) {
      return res.json(cached);
    }

    const result = await executeQuery<{
      COHORT: string;
      CUSTOMER_COUNT: number;
      AT_RISK_COUNT: number;
      AVG_RISK_SCORE: number;
      AVG_RISK_SCORE_AT_RISK: number | null;
      LTV_AT_RISK: number;
    }>(cohortsListQuery());

    const cohorts = (result.rows || []).map((row) => ({
      cohort: row.COHORT,
      customerCount: Number(row.CUSTOMER_COUNT),
      atRiskCount: Number(row.AT_RISK_COUNT),
      atRiskPercentage: row.CUSTOMER_COUNT > 0
        ? Math.round((Number(row.AT_RISK_COUNT) / Number(row.CUSTOMER_COUNT)) * 10000) / 100
        : 0,
      averageRiskScore: Number(row.AVG_RISK_SCORE),
      averageRiskScoreAtRisk: row.AVG_RISK_SCORE_AT_RISK ?? 0,
      ltvAtRisk: Math.round(Number(row.LTV_AT_RISK) * 100) / 100,
    }));

    const response = { cohorts };

    setCache(CACHE_KEY, response, CACHE_TTL_MILLISECONDS);
    res.json(response);
  } catch (error: any) {
    if (isDatabaseError(error.message || '')) {
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
