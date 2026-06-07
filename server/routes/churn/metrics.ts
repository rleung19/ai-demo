/**
 * Churn Model Metrics Route
 * GET /api/kpi/churn/metrics
 */

import express from 'express';
import { executeQuery } from '../../lib/db';
import { getCache, setCache } from '../../lib/cache';
import { handleDatabaseError, handleNotFoundError } from '../../lib/api/express-errors';
import { isDatabaseError, metricsQuery } from '../../lib/sql/churn-queries';

const router = express.Router();

const CACHE_KEY = 'churn:metrics';
const CACHE_TTL_MILLISECONDS = 60_000;

router.get('/', async (req, res) => {
  try {
    const cached = getCache<any>(CACHE_KEY);
    if (cached) {
      return res.json(cached);
    }

    const result = await executeQuery<{
      MODEL_ID: string;
      MODEL_NAME: string;
      MODEL_VERSION: string;
      MODEL_TYPE: string;
      AUC_SCORE: number;
      ACCURACY: number;
      PRECISION_SCORE: number;
      RECALL_SCORE: number;
      F1_SCORE: number;
      OPTIMAL_THRESHOLD: number;
      TRAINING_DATE: Date;
      TRAIN_SAMPLES: number;
      TEST_SAMPLES: number;
      FEATURE_COUNT: number;
      STATUS: string;
    }>(metricsQuery());

    const model = result.rows?.[0];

    if (!model) {
      return handleNotFoundError('Active model', res);
    }

    const response = {
      modelId: model.MODEL_ID,
      modelName: model.MODEL_NAME,
      modelVersion: model.MODEL_VERSION,
      modelType: model.MODEL_TYPE,
      modelConfidence: model.AUC_SCORE,
      accuracy: model.ACCURACY,
      precision: model.PRECISION_SCORE,
      recall: model.RECALL_SCORE,
      f1Score: model.F1_SCORE,
      optimalThreshold: model.OPTIMAL_THRESHOLD,
      lastUpdate: new Date(model.TRAINING_DATE).toISOString(),
      trainingStats: {
        trainSamples: model.TRAIN_SAMPLES,
        testSamples: model.TEST_SAMPLES,
        featureCount: model.FEATURE_COUNT,
      },
      status: model.STATUS,
    };

    setCache(CACHE_KEY, response, CACHE_TTL_MILLISECONDS);
    res.json(response);
  } catch (error: any) {
    if (isDatabaseError(error.message || '')) {
      return handleDatabaseError(error, res);
    }
    return res.status(503).json({
      error: 'Service unavailable',
      message: error.message || 'Unable to fetch model metrics',
      fallback: true,
    });
  }
});

export default router;
