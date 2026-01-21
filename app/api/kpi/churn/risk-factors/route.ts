/**
 * Churn Risk Factors Endpoint
 * Task: GET /api/kpi/churn/risk-factors
 * 
 * Returns top churn risk factors with impact scores, affected customers, and primary segments
 */

import { NextResponse } from 'next/server';
import { executeQuery } from '@/app/lib/db/oracle';
import { handleDatabaseError } from '@/app/lib/api/errors';
import { logRequest } from '@/app/lib/api/request-logger';
import { getCache, setCache } from '@/app/lib/api/cache';

export async function GET() {
  const startTime = Date.now();
  const path = '/api/kpi/churn/risk-factors';
  const cacheKey = 'churn:risk-factors';
  const CACHE_TTL_MS = 300_000; // 5 minutes – expensive aggregation
  
  try {
    const cached = getCache<any>(cacheKey);
    if (cached) {
      logRequest('GET', path, 200, startTime);
      return NextResponse.json(cached);
    }
    // Common cohort assignment CTE
    const cohortCTE = `
      WITH cohort_assignments AS (
        SELECT 
          up.USER_ID,
          cp.PREDICTED_CHURN_PROBABILITY,
          cp.PREDICTED_CHURN_LABEL,
          up.EMAIL_OPEN_RATE,
          up.DAYS_SINCE_LAST_PURCHASE,
          up.CART_ABANDONMENT_RATE,
          up.RETURNS_RATE,
          up.CUSTOMER_SERVICE_CALLS,
          up.LIFETIME_VALUE,
          up.MEMBERSHIP_YEARS,
          up.TOTAL_PURCHASES,
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
        FROM OML.USER_PROFILES up
        JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
        JOIN ADMIN.USERS au ON up.USER_ID = au.ID
      )
    `;

    // Risk Factor 1: Email Engagement Decay
    const emailEngagementQuery = `
      ${cohortCTE}
      , affected_email AS (
        SELECT 
          COUNT(*) as affected_customers,
          ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score
        FROM cohort_assignments
        WHERE EMAIL_OPEN_RATE < 20 AND cohort != 'Other'
      ),
      email_segments AS (
        SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY cnt DESC) as primary_segment
        FROM (
          SELECT cohort, COUNT(*) as cnt
          FROM cohort_assignments
          WHERE EMAIL_OPEN_RATE < 20 AND cohort != 'Other'
          GROUP BY cohort
          ORDER BY cnt DESC
          FETCH FIRST 2 ROWS ONLY
        )
      )
      SELECT 
        'Email Engagement Decay' as risk_factor,
        ae.affected_customers,
        ae.impact_score,
        COALESCE(es.primary_segment, 'All segments') as primary_segment
      FROM affected_email ae
      CROSS JOIN email_segments es
    `;

    // Risk Factor 2: No Purchase in 45+ Days
    const noPurchaseQuery = `
      ${cohortCTE}
      , affected_no_purchase AS (
        SELECT 
          COUNT(*) as affected_customers,
          ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score
        FROM cohort_assignments
        WHERE DAYS_SINCE_LAST_PURCHASE > 45 AND cohort != 'Other'
      ),
      no_purchase_segments AS (
        SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY cnt DESC) as primary_segment
        FROM (
          SELECT cohort, COUNT(*) as cnt
          FROM cohort_assignments
          WHERE DAYS_SINCE_LAST_PURCHASE > 45 AND cohort != 'Other'
          GROUP BY cohort
          ORDER BY cnt DESC
          FETCH FIRST 2 ROWS ONLY
        )
      )
      SELECT 
        'No Purchase in 45+ Days' as risk_factor,
        anp.affected_customers,
        anp.impact_score,
        COALESCE(nps.primary_segment, 'All segments') as primary_segment
      FROM affected_no_purchase anp
      CROSS JOIN no_purchase_segments nps
    `;

    // Risk Factor 3: Price Sensitivity (Cart Abandons)
    const cartAbandonQuery = `
      ${cohortCTE}
      , affected_cart AS (
        SELECT 
          COUNT(*) as affected_customers,
          ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score
        FROM cohort_assignments
        WHERE CART_ABANDONMENT_RATE > 50 AND cohort != 'Other'
      ),
      cart_segments AS (
        SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY cnt DESC) as primary_segment
        FROM (
          SELECT cohort, COUNT(*) as cnt
          FROM cohort_assignments
          WHERE CART_ABANDONMENT_RATE > 50 AND cohort != 'Other'
          GROUP BY cohort
          ORDER BY cnt DESC
          FETCH FIRST 2 ROWS ONLY
        )
      )
      SELECT 
        'Price Sensitivity (cart abandons)' as risk_factor,
        ac.affected_customers,
        ac.impact_score,
        COALESCE(cs.primary_segment, 'All segments') as primary_segment
      FROM affected_cart ac
      CROSS JOIN cart_segments cs
    `;

    // Risk Factor 4: Size/Fit Issues (High Returns)
    const returnsQuery = `
      ${cohortCTE}
      , affected_returns AS (
        SELECT 
          COUNT(*) as affected_customers,
          ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score
        FROM cohort_assignments
        WHERE RETURNS_RATE > 20 AND cohort != 'Other'
      ),
      returns_segments AS (
        SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY cnt DESC) as primary_segment
        FROM (
          SELECT cohort, COUNT(*) as cnt
          FROM cohort_assignments
          WHERE RETURNS_RATE > 20 AND cohort != 'Other'
          GROUP BY cohort
          ORDER BY cnt DESC
          FETCH FIRST 2 ROWS ONLY
        )
      )
      SELECT 
        'Size/Fit Issues (2+ returns)' as risk_factor,
        ar.affected_customers,
        ar.impact_score,
        COALESCE(rs.primary_segment, 'All segments') as primary_segment
      FROM affected_returns ar
      CROSS JOIN returns_segments rs
    `;

    // Risk Factor 5: Negative Review Sentiment (Proxy: High Support Calls)
    const supportCallsQuery = `
      ${cohortCTE}
      , affected_support AS (
        SELECT 
          COUNT(*) as affected_customers,
          ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score
        FROM cohort_assignments
        WHERE CUSTOMER_SERVICE_CALLS > 2 AND cohort != 'Other'
      ),
      support_segments AS (
        SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY cnt DESC) as primary_segment
        FROM (
          SELECT cohort, COUNT(*) as cnt
          FROM cohort_assignments
          WHERE CUSTOMER_SERVICE_CALLS > 2 AND cohort != 'Other'
          GROUP BY cohort
          ORDER BY cnt DESC
          FETCH FIRST 2 ROWS ONLY
        )
      )
      SELECT 
        'Negative Review Sentiment' as risk_factor,
        asup.affected_customers,
        asup.impact_score,
        COALESCE(ss.primary_segment, 'All segments') as primary_segment
      FROM affected_support asup
      CROSS JOIN support_segments ss
    `;

    // Execute all queries in parallel
    const [
      emailResult,
      noPurchaseResult,
      cartAbandonResult,
      returnsResult,
      supportCallsResult,
    ] = await Promise.all([
      executeQuery<{
        RISK_FACTOR: string;
        AFFECTED_CUSTOMERS: number;
        IMPACT_SCORE: number;
        PRIMARY_SEGMENT: string | null;
      }>(emailEngagementQuery),
      executeQuery<{
        RISK_FACTOR: string;
        AFFECTED_CUSTOMERS: number;
        IMPACT_SCORE: number;
        PRIMARY_SEGMENT: string | null;
      }>(noPurchaseQuery),
      executeQuery<{
        RISK_FACTOR: string;
        AFFECTED_CUSTOMERS: number;
        IMPACT_SCORE: number;
        PRIMARY_SEGMENT: string | null;
      }>(cartAbandonQuery),
      executeQuery<{
        RISK_FACTOR: string;
        AFFECTED_CUSTOMERS: number;
        IMPACT_SCORE: number;
        PRIMARY_SEGMENT: string | null;
      }>(returnsQuery),
      executeQuery<{
        RISK_FACTOR: string;
        AFFECTED_CUSTOMERS: number;
        IMPACT_SCORE: number;
        PRIMARY_SEGMENT: string | null;
      }>(supportCallsQuery),
    ]);

    // Transform results
    const riskFactors = [
      emailResult.rows?.[0],
      noPurchaseResult.rows?.[0],
      cartAbandonResult.rows?.[0],
      returnsResult.rows?.[0],
      supportCallsResult.rows?.[0],
    ]
      .filter((row) => row && row.AFFECTED_CUSTOMERS > 0) // Only include factors with affected customers
      .map((row) => ({
        riskFactor: row!.RISK_FACTOR,
        impactScore: `${row!.IMPACT_SCORE}%`,
        affectedCustomers: row!.AFFECTED_CUSTOMERS,
        primarySegment: row!.PRIMARY_SEGMENT || 'All segments',
      }))
      .sort((a, b) => {
        // Sort by impact score (highest first)
        const scoreA = parseFloat(a.impactScore.replace('%', ''));
        const scoreB = parseFloat(b.impactScore.replace('%', ''));
        return scoreB - scoreA;
      });

    const response = {
      riskFactors,
      lastUpdate: new Date().toISOString(),
    };

    setCache(cacheKey, response, CACHE_TTL_MS);
    logRequest('GET', path, 200, startTime);
    return NextResponse.json(response);
  } catch (error: any) {
    if (error.message?.includes('ORA-') || error.message?.includes('database')) {
      return handleDatabaseError(error);
    }
    return NextResponse.json(
      {
        error: 'Service unavailable',
        message: error.message || 'Unable to fetch risk factors',
        fallback: true,
      },
      { status: 503 }
    );
  }
}
