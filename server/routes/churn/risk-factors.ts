/**
 * Churn Risk Factors Route
 * GET /api/kpi/churn/risk-factors
 */

import express from 'express';
import { executeQuery } from '../../lib/db';
import { handleDatabaseError } from '../../lib/api/express-errors';
import { getCache, setCache } from '../../lib/cache';
import { isDatabaseError, RISK_FACTOR_QUERIES } from '../../lib/sql/churn-queries';

const router = express.Router();

const CACHE_KEY = 'churn:risk-factors';
const CACHE_TTL_MILLISECONDS = 300_000;

router.get('/', async (req, res) => {
  try {
    const cached = getCache<any>(CACHE_KEY);
    if (cached) {
      return res.json(cached);
    }

    const results = await Promise.all(
      RISK_FACTOR_QUERIES.map(({ query }) =>
        executeQuery<{
          RISK_FACTOR: string;
          AFFECTED_CUSTOMERS: number;
          IMPACT_SCORE: number;
          PRIMARY_SEGMENT: string | null;
        }>(query())
      )
    );

    const riskFactors = results
      .map((result) => result.rows?.[0])
      .filter((row) => row && Number(row.AFFECTED_CUSTOMERS) > 0)
      .map((row) => ({
        riskFactor: row!.RISK_FACTOR,
        impactScore: `${row!.IMPACT_SCORE}%`,
        affectedCustomers: Number(row!.AFFECTED_CUSTOMERS),
        primarySegment: row!.PRIMARY_SEGMENT || 'All segments',
      }))
      .sort((a, b) => {
        const scoreA = parseFloat(a.impactScore.replace('%', ''));
        const scoreB = parseFloat(b.impactScore.replace('%', ''));
        return scoreB - scoreA;
      });

    const response = {
      riskFactors,
      lastUpdate: new Date().toISOString(),
    };

    setCache(CACHE_KEY, response, CACHE_TTL_MILLISECONDS);
    res.json(response);
  } catch (error: any) {
    if (isDatabaseError(error.message || '')) {
      return handleDatabaseError(error, res);
    }
    return res.status(503).json({
      error: 'Service unavailable',
      message: error.message || 'Unable to fetch risk factors',
      fallback: true,
    });
  }
});

export default router;
