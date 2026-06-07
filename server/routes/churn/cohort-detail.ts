/**
 * Churn Cohort Detail Route
 * GET /api/kpi/churn/cohorts/:name
 */

import express from 'express';
import { executeQuery } from '../../lib/db';
import { getCache, setCache } from '../../lib/cache';
import { handleDatabaseError, handleNotFoundError, handleValidationError } from '../../lib/api/express-errors';
import {
  cohortDetailSummaryQuery,
  cohortDetailUsersQuery,
  isDatabaseError,
} from '../../lib/sql/churn-queries';

const router = express.Router();

const CACHE_TTL_MILLISECONDS = 60_000;

const VALID_COHORTS = ['VIP', 'REGULAR', 'NEW', 'DORMANT', 'OTHER'];

const COHORT_DEFINITIONS: Record<string, string> = {
  VIP: 'LIFETIME_VALUE > 5000 OR AFFINITY_CARD = 1',
  REGULAR: 'TOTAL_PURCHASES >= 2 AND DAYS_SINCE_LAST_PURCHASE <= 90 AND LOGIN_FREQUENCY > 0 (excludes VIP/New)',
  NEW: 'MEMBERSHIP_YEARS < 1 (excludes VIP)',
  DORMANT: 'DAYS_SINCE_LAST_PURCHASE > 90 OR LOGIN_FREQUENCY = 0 (excludes VIP/New)',
  OTHER: 'Does not match any other cohort criteria',
};

router.get('/:name', async (req, res) => {
  try {
    const cohortName = req.params.name.toUpperCase();
    if (!VALID_COHORTS.includes(cohortName)) {
      return handleNotFoundError(
        `Cohort '${req.params.name}' not found. Valid cohorts: ${VALID_COHORTS.join(', ')}`,
        res
      );
    }

    const limitParam = req.query.limit as string | undefined;
    const offsetParam = req.query.offset as string | undefined;
    const sortParam = (req.query.sort as string | undefined) || 'churn';
    const atRiskOnlyParam = req.query.atRiskOnly as string | undefined;
    const minLtvParam = req.query.minLtv as string | undefined;
    const maxLtvParam = req.query.maxLtv as string | undefined;

    const validationErrors: string[] = [];

    let limit: number = 3;
    if (limitParam === '-1') {
      limit = -1;
    } else {
      const parsedLimit = parseInt(limitParam || '3', 10);
      if (isNaN(parsedLimit) || parsedLimit < 1 || parsedLimit > 500) {
        validationErrors.push('limit must be between 1 and 500, or -1 for all users');
      } else {
        limit = parsedLimit;
      }
    }

    const offset = parseInt(offsetParam || '0', 10);
    if (isNaN(offset) || offset < 0) {
      validationErrors.push('offset must be a non-negative integer');
    }

    if (sortParam !== 'churn' && sortParam !== 'ltv') {
      validationErrors.push('sort must be either "churn" or "ltv"');
    }

    let atRiskOnly = true;
    if (atRiskOnlyParam !== undefined) {
      if (atRiskOnlyParam === 'true') {
        atRiskOnly = true;
      } else if (atRiskOnlyParam === 'false') {
        atRiskOnly = false;
      } else {
        validationErrors.push('atRiskOnly must be "true" or "false" when provided');
      }
    }

    let minLtv: number | undefined;
    let maxLtv: number | undefined;

    if (minLtvParam !== undefined) {
      const parsedMin = parseFloat(minLtvParam);
      if (isNaN(parsedMin) || parsedMin < 0) {
        validationErrors.push('minLtv must be a non-negative number when provided');
      } else {
        minLtv = parsedMin;
      }
    }

    if (maxLtvParam !== undefined) {
      const parsedMax = parseFloat(maxLtvParam);
      if (isNaN(parsedMax) || parsedMax < 0) {
        validationErrors.push('maxLtv must be a non-negative number when provided');
      } else {
        maxLtv = parsedMax;
      }
    }

    if (minLtv !== undefined && maxLtv !== undefined && maxLtv < minLtv) {
      validationErrors.push('maxLtv must be greater than or equal to minLtv');
    }

    if (validationErrors.length > 0) {
      return handleValidationError(validationErrors, res);
    }

    const cacheKey = `churn:cohort-detail:${cohortName}:${limit}:${offset}:${sortParam}:${atRiskOnly ? '1' : '0'}:${minLtv ?? 'null'}:${maxLtv ?? 'null'}`;
    const cached = getCache<any>(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    const summaryResult = await executeQuery<{
      CUSTOMER_COUNT: number;
      AT_RISK_COUNT: number;
      AVG_RISK_SCORE: number;
      LTV_AT_RISK: number;
    }>(cohortDetailSummaryQuery(), { cohortName });

    if (!summaryResult.rows || summaryResult.rows.length === 0) {
      return handleNotFoundError(
        `Cohort '${req.params.name}' not found or has no users`,
        res
      );
    }

    const summary = summaryResult.rows[0];
    const totalUsers = summary.CUSTOMER_COUNT;

    const orderBy =
      sortParam === 'ltv'
        ? 'ORDER BY LIFETIME_VALUE DESC'
        : 'ORDER BY PREDICTED_CHURN_PROBABILITY DESC';

    const whereClauses: string[] = ['UPPER(cohort) = :cohortName'];
    const usersParams: Record<string, unknown> = { cohortName };

    if (atRiskOnly) {
      whereClauses.push('PREDICTED_CHURN_LABEL = 1');
    }
    if (minLtv !== undefined) {
      whereClauses.push('LIFETIME_VALUE >= :minLtv');
      usersParams.minLtv = minLtv;
    }
    if (maxLtv !== undefined) {
      whereClauses.push('LIFETIME_VALUE <= :maxLtv');
      usersParams.maxLtv = maxLtv;
    }

    const usersQuery = cohortDetailUsersQuery(whereClauses, orderBy, limit !== -1);
    if (limit !== -1) {
      usersParams.offset = offset;
      usersParams.limit = limit;
    }

    const usersResult = await executeQuery<{
      USER_ID: string;
      PREDICTED_CHURN_PROBABILITY: number;
      LIFETIME_VALUE: number;
      TOTAL_COUNT: number;
    }>(usersQuery, usersParams);

    const users = (usersResult.rows || []).map((row) => ({
      userId: row.USER_ID,
      churnProbability: Math.round(Number(row.PREDICTED_CHURN_PROBABILITY) * 10000) / 10000,
      ltv: Math.round(Number(row.LIFETIME_VALUE) * 100) / 100,
    }));

    const response = {
      cohort: cohortName,
      definition: COHORT_DEFINITIONS[cohortName],
      summary: {
        customerCount: Number(summary.CUSTOMER_COUNT),
        atRiskCount: Number(summary.AT_RISK_COUNT),
        atRiskPercentage: summary.CUSTOMER_COUNT > 0
          ? Math.round((Number(summary.AT_RISK_COUNT) / Number(summary.CUSTOMER_COUNT)) * 10000) / 100
          : 0,
        averageRiskScore: Number(summary.AVG_RISK_SCORE),
        ltvAtRisk: Math.round(Number(summary.LTV_AT_RISK) * 100) / 100,
      },
      users,
      pagination: {
        total: Number(totalUsers),
        limit,
        offset: limit === -1 ? 0 : offset,
      },
    };

    setCache(cacheKey, response, CACHE_TTL_MILLISECONDS);
    res.json(response);
  } catch (error: any) {
    if (isDatabaseError(error.message || '')) {
      return handleDatabaseError(error, res);
    }
    return res.status(503).json({
      error: 'Service unavailable',
      message: error.message || 'Unable to fetch cohort detail',
      fallback: true,
    });
  }
});

export default router;
