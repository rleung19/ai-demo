/**
 * Churn Cohort Detail Route
 * GET /api/kpi/churn/cohorts/:name
 */

import express from 'express';
import { executeQuery } from '../../lib/db/oracle';
import { getCache, setCache } from '../../lib/cache';
import { handleDatabaseError, handleNotFoundError, handleValidationError } from '../../lib/api/express-errors';

const router = express.Router();

const CACHE_TTL_MILLISECONDS = 60_000; // 60 seconds

// Valid cohort names (case-insensitive)
const VALID_COHORTS = ['VIP', 'REGULAR', 'NEW', 'DORMANT', 'OTHER'];

// Cohort definitions
const COHORT_DEFINITIONS: Record<string, string> = {
  'VIP': 'LIFETIME_VALUE > 5000 OR AFFINITY_CARD = 1',
  'REGULAR': 'TOTAL_PURCHASES >= 2 AND DAYS_SINCE_LAST_PURCHASE <= 90 AND LOGIN_FREQUENCY > 0 (excludes VIP/New)',
  'NEW': 'MEMBERSHIP_YEARS < 1 (excludes VIP)',
  'DORMANT': 'DAYS_SINCE_LAST_PURCHASE > 90 OR LOGIN_FREQUENCY = 0 (excludes VIP/New)',
  'OTHER': 'Does not match any other cohort criteria',
};

router.get('/:name', async (req, res) => {
  try {
    // Validate and normalize cohort name
    const cohortName = req.params.name.toUpperCase();
    if (!VALID_COHORTS.includes(cohortName)) {
      return handleNotFoundError(
        `Cohort '${req.params.name}' not found. Valid cohorts: ${VALID_COHORTS.join(', ')}`,
        res
      );
    }

    // Validate and parse query parameters
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

    // Validate atRiskOnly (optional boolean, default: true)
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

    // Validate LTV filters (optional numbers, >= 0, and maxLtv >= minLtv when both provided)
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

    // Check cache
    const cacheKey = `churn:cohort-detail:${cohortName}:${limit}:${offset}:${sortParam}:${atRiskOnly ? '1' : '0'}:${minLtv ?? 'null'}:${maxLtv ?? 'null'}`;
    const cached = getCache<any>(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    // Build SQL query - reuse cohort_assignments CTE from cohorts.ts
    const cohortAssignmentsCTE = `
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
    `;

    // Query 1: Get summary statistics
    const summaryQuery = `
      ${cohortAssignmentsCTE}
      SELECT 
        COUNT(*) AS customer_count,
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
        ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
      FROM cohort_assignments
      WHERE UPPER(cohort) = :cohortName
    `;

    const summaryResult = await executeQuery<{
      CUSTOMER_COUNT: number;
      AT_RISK_COUNT: number;
      AVG_RISK_SCORE: number;
      LTV_AT_RISK: number;
    }>(summaryQuery, { cohortName });

    if (!summaryResult.rows || summaryResult.rows.length === 0) {
      return handleNotFoundError(
        `Cohort '${req.params.name}' not found or has no users`,
        res
      );
    }

    const summary = summaryResult.rows[0];
    const totalUsers = summary.CUSTOMER_COUNT;

    // Query 2: Get users list with pagination and sorting
    const orderBy = sortParam === 'ltv' 
      ? 'ORDER BY LIFETIME_VALUE DESC'
      : 'ORDER BY PREDICTED_CHURN_PROBABILITY DESC';

    const whereClauses: string[] = ['UPPER(cohort) = :cohortName'];
    const usersParams: {
      cohortName: string;
      offset?: number;
      limit?: number;
      minLtv?: number;
      maxLtv?: number;
    } = {
      cohortName,
    };

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

    let usersQuery = `
      ${cohortAssignmentsCTE}
      SELECT 
        USER_ID,
        PREDICTED_CHURN_PROBABILITY,
        LIFETIME_VALUE,
        COUNT(*) OVER() AS total_count
      FROM cohort_assignments
      WHERE ${whereClauses.join('\n        AND ')}
      ${orderBy}
    `;

    // Add pagination only if limit != -1
    if (limit !== -1) {
      usersQuery += ` OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY`;
      usersParams.offset = offset;
      usersParams.limit = limit;
    }

    const usersResult = await executeQuery<{
      USER_ID: string;
      PREDICTED_CHURN_PROBABILITY: number;
      LIFETIME_VALUE: number;
      TOTAL_COUNT: number;
    }>(usersQuery, usersParams);

    // Format response
    const users = (usersResult.rows || []).map((row: {
      USER_ID: string;
      PREDICTED_CHURN_PROBABILITY: number;
      LIFETIME_VALUE: number;
    }) => ({
      userId: row.USER_ID,
      churnProbability: Math.round(row.PREDICTED_CHURN_PROBABILITY * 10000) / 10000, // Keep 4 decimals
      ltv: Math.round(row.LIFETIME_VALUE * 100) / 100, // 2 decimals
    }));

    const response = {
      cohort: cohortName,
      definition: COHORT_DEFINITIONS[cohortName],
      summary: {
        customerCount: summary.CUSTOMER_COUNT,
        atRiskCount: summary.AT_RISK_COUNT,
        atRiskPercentage: summary.CUSTOMER_COUNT > 0
          ? Math.round((summary.AT_RISK_COUNT / summary.CUSTOMER_COUNT) * 10000) / 100
          : 0,
        averageRiskScore: summary.AVG_RISK_SCORE,
        ltvAtRisk: Math.round(summary.LTV_AT_RISK * 100) / 100,
      },
      users,
      pagination: {
        total: totalUsers,
        limit,
        offset: limit === -1 ? 0 : offset,
      },
    };

    // Cache response
    setCache(cacheKey, response, CACHE_TTL_MILLISECONDS);
    res.json(response);
  } catch (error: any) {
    if (error.message?.includes('ORA-') || error.message?.includes('database')) {
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
