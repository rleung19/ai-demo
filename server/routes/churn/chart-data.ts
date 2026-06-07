/**
 * Churn Chart Data Route
 * GET /api/kpi/churn/chart-data?type=distribution
 */

import express from 'express';
import { executeQuery } from '../../lib/db';
import { validateQueryParams } from '../../lib/api/validation';
import { handleValidationError, handleDatabaseError } from '../../lib/api/express-errors';
import { getCache, setCache } from '../../lib/cache';
import { chartDistributionQuery, isDatabaseError } from '../../lib/sql/churn-queries';

const router = express.Router();

const CACHE_TTL_MILLISECONDS = 60_000;

router.get('/', async (req, res) => {
  try {
    const validation = validateQueryParams(req.query as any, {
      type: {
        type: 'string',
        required: false,
        allowed: ['distribution', 'cohort-trend'],
      },
    });

    if (!validation.valid) {
      return handleValidationError(validation.errors || [], res);
    }

    const chartType = (validation.data?.type as string) || 'distribution';
    const cacheKey = `churn:chart-data:${chartType}`;

    const cached = getCache<any>(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    if (chartType === 'distribution') {
      const result = await executeQuery<{
        RISK_RANGE: string;
        CUSTOMER_COUNT: number;
        AT_RISK_COUNT: number;
      }>(chartDistributionQuery());

      const data = (result.rows || []).map((row) => ({
        riskRange: row.RISK_RANGE,
        customerCount: Number(row.CUSTOMER_COUNT),
        atRiskCount: Number(row.AT_RISK_COUNT),
      }));

      const response = {
        chartType: 'distribution',
        data,
      };

      setCache(cacheKey, response, CACHE_TTL_MILLISECONDS);
      return res.json(response);
    }

    if (chartType === 'cohort-trend') {
      const response = {
        chartType: 'cohort-trend',
        message: 'Historical trend data not yet available',
        data: [],
      };

      setCache(cacheKey, response, CACHE_TTL_MILLISECONDS);
      return res.json(response);
    }

    return handleValidationError(
      [`Chart type '${chartType}' is not supported. Use 'distribution' or 'cohort-trend'.`],
      res
    );
  } catch (error: any) {
    if (isDatabaseError(error.message || '')) {
      return handleDatabaseError(error, res);
    }
    res.status(503).json({
      error: 'Service unavailable',
      message: error.message || 'Unable to fetch chart data',
      fallback: true,
    });
  }
});

export default router;
