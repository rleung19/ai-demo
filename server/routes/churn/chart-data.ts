/**
 * Churn Chart Data Route
 * GET /api/kpi/churn/chart-data?type=distribution
 */

import express from 'express';
import { executeQuery } from '../../lib/db/oracle';
import { validateQueryParams } from '../../lib/api/validation';
import { handleValidationError, handleDatabaseError } from '../../lib/api/express-errors';

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    // Validate query parameters
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

    if (chartType === 'distribution') {
      // Risk distribution chart data
      const distributionQuery = `
        SELECT 
          CASE 
            WHEN PREDICTED_CHURN_PROBABILITY < 0.1 THEN '< 10%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.2 THEN '10-20%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.3 THEN '20-30%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.4 THEN '30-40%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.5 THEN '40-50%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.6 THEN '50-60%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.7 THEN '60-70%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.8 THEN '70-80%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.9 THEN '80-90%'
            ELSE '>= 90%'
          END AS risk_range,
          COUNT(*) AS customer_count,
          SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count
        FROM OML.CHURN_PREDICTIONS
        GROUP BY 
          CASE 
            WHEN PREDICTED_CHURN_PROBABILITY < 0.1 THEN '< 10%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.2 THEN '10-20%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.3 THEN '20-30%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.4 THEN '30-40%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.5 THEN '40-50%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.6 THEN '50-60%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.7 THEN '60-70%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.8 THEN '70-80%'
            WHEN PREDICTED_CHURN_PROBABILITY < 0.9 THEN '80-90%'
            ELSE '>= 90%'
          END
        ORDER BY MIN(PREDICTED_CHURN_PROBABILITY)
      `;

      const result = await executeQuery<{
        RISK_RANGE: string;
        CUSTOMER_COUNT: number;
        AT_RISK_COUNT: number;
      }>(distributionQuery);

      const data = (result.rows || []).map((row: {
        RISK_RANGE: string;
        CUSTOMER_COUNT: number;
        AT_RISK_COUNT: number;
      }) => ({
        riskRange: row.RISK_RANGE,
        customerCount: row.CUSTOMER_COUNT,
        atRiskCount: row.AT_RISK_COUNT,
      }));

      return res.json({
        chartType: 'distribution',
        data,
      });
    } else if (chartType === 'cohort-trend') {
      // Placeholder for future: cohort trends over time
      return res.json({
        chartType: 'cohort-trend',
        message: 'Historical trend data not yet available',
        data: [],
      });
    } else {
      return handleValidationError([`Chart type '${chartType}' is not supported. Use 'distribution' or 'cohort-trend'.`], res);
    }
  } catch (error: any) {
    if (error.message?.includes('ORA-') || error.message?.includes('database')) {
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
