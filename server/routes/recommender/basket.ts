/**
 * Basket Recommender Route
 * POST /api/recommender/basket
 *
 * Wraps the OCI Data Science basket association model deployment.
 */

import express from 'express';
import { getCache, setCache } from '../../lib/cache';
import { predictBasketRecs } from '../../lib/oci/model-deployment';

const router = express.Router();

const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

function buildCacheKey(basket: string[], topN: number): string {
  const keyBasket = basket.join(',');
  return `recommender:basket:${keyBasket}:${topN}`;
}

function parseTopN(raw: any): number | null {
  if (raw === undefined || raw === null || raw === '') {
    return 3;
  }
  const n = Number(raw);
  if (!Number.isFinite(n) || n < 1 || n > 100) {
    return null;
  }
  return Math.floor(n);
}

router.post('/', async (req, res) => {
  try {
    const basket = req.body?.basket as unknown;
    const topN = parseTopN(req.body?.top_n);

    const errors: string[] = [];
    if (!Array.isArray(basket) || basket.length === 0) {
      errors.push('basket must be a non-empty array of product IDs');
    } else if (!basket.every((p) => typeof p === 'string' && p.trim().length > 0)) {
      errors.push('basket must contain only non-empty string product IDs');
    }

    if (topN === null) {
      errors.push('top_n must be a number between 1 and 100');
    }

    if (errors.length > 0) {
      return res.status(400).json({
        error: 'Validation failed',
        message: 'Invalid request parameters',
        details: { errors },
      });
    }

    const basketIds = (basket as string[]).map((id) => id.trim());
    const cacheKey = buildCacheKey(basketIds, topN!);
    const cached = getCache<any>(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    // Call OCI model deployment
    const result = await predictBasketRecs(basketIds, topN!);

    // The notebook returns { prediction: [[{ products, confidence, lift }, ...]] }
    const prediction = (result as any)?.prediction;
    const flatRecs =
      Array.isArray(prediction) && Array.isArray(prediction[0])
        ? prediction[0]
        : [];

    const recommendations = (flatRecs as any[]).map((r) => ({
      products: Array.isArray(r.products) ? r.products : [],
      confidence: typeof r.confidence === 'number' ? r.confidence : null,
      lift: typeof r.lift === 'number' ? r.lift : null,
    }));

    const response = {
      basket: basketIds,
      recommendations,
      message: 'Success',
    };

    setCache(cacheKey, response, CACHE_TTL_MS);
    return res.json(response);
  } catch (error: any) {
    const message = error?.message || 'Failed to get basket recommendations';
    const isAuthError =
      message.toLowerCase().includes('auth') ||
      message.toLowerCase().includes('sign') ||
      message.toLowerCase().includes('config');

    const status = isAuthError ? 503 : 500;
    return res.status(status).json({
      error: isAuthError ? 'OCI service error' : 'Internal server error',
      message,
      fallback: true,
    });
  }
});

export default router;

