/**
 * Churn Summary Endpoint
 * Task 4.4: GET /api/kpi/churn/summary
 * 
 * Returns summary metrics for churn risk analysis:
 * - At-risk customer count
 * - Average risk score
 * - Total LTV at risk
 * - Model confidence and version
 */

import { NextResponse } from 'next/server';
import { executeQuery } from '@/app/lib/db/oracle';
import { handleDatabaseError } from '@/app/lib/api/errors';

export async function GET() {
  try {
    // Get summary statistics from CHURN_PREDICTIONS
    const summaryQuery = `
      SELECT 
        COUNT(*) AS total_customers,
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
        AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS average_risk_score,
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS at_risk_percentage
      FROM OML.CHURN_PREDICTIONS
    `;

    const summaryResult = await executeQuery<{
      TOTAL_CUSTOMERS: number;
      AT_RISK_COUNT: number;
      AVERAGE_RISK_SCORE: number;
      AT_RISK_PERCENTAGE: number;
    }>(summaryQuery);

    const summary = summaryResult.rows?.[0];
    if (!summary) {
      throw new Error('No summary data available');
    }

    // Get total LTV at risk
    const ltvQuery = `
      SELECT 
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END) AS total_ltv_at_risk
      FROM OML.CHURN_PREDICTIONS cp
      INNER JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
    `;

    const ltvResult = await executeQuery<{
      TOTAL_LTV_AT_RISK: number;
    }>(ltvQuery);

    const totalLTVAtRisk = ltvResult.rows?.[0]?.TOTAL_LTV_AT_RISK || 0;

    // Get latest model info from MODEL_REGISTRY
    const modelQuery = `
      SELECT 
        MODEL_VERSION,
        AUC_SCORE AS model_confidence,
        TRAINING_DATE AS last_update
      FROM OML.MODEL_REGISTRY
      WHERE STATUS = 'ACTIVE'
      ORDER BY TRAINING_DATE DESC
      FETCH FIRST 1 ROW ONLY
    `;

    const modelResult = await executeQuery<{
      MODEL_VERSION: string;
      MODEL_CONFIDENCE: number;
      LAST_UPDATE: Date;
    }>(modelQuery);

    const modelInfo = modelResult.rows?.[0];

    const response = {
      atRiskCount: summary.AT_RISK_COUNT,
      totalCustomers: summary.TOTAL_CUSTOMERS,
      atRiskPercentage: Math.round(summary.AT_RISK_PERCENTAGE * 100) / 100,
      averageRiskScore: Math.round(summary.AVERAGE_RISK_SCORE * 100) / 100,
      totalLTVAtRisk: Math.round(totalLTVAtRisk * 100) / 100,
      modelConfidence: modelInfo?.MODEL_CONFIDENCE || null,
      lastUpdate: modelInfo?.LAST_UPDATE ? new Date(modelInfo.LAST_UPDATE).toISOString() : null,
      modelVersion: modelInfo?.MODEL_VERSION || null,
    };

    return NextResponse.json(response);
  } catch (error: any) {
    if (error.message?.includes('ORA-') || error.message?.includes('database')) {
      return handleDatabaseError(error);
    }
    return NextResponse.json(
      {
        error: 'Service unavailable',
        message: error.message || 'Unable to fetch churn summary',
        fallback: true,
      },
      { status: 503 }
    );
  }
}
