/**
 * Product Recommender Route
 * POST /api/recommender/product
 * GET  /api/recommender/product?user_id=...&top_k=...
 *
 * Wraps the OCI Data Science product recommender model deployment.
 */

import express from 'express';
import { getCache, setCache } from '../../lib/cache';
import { predictUserRecs } from '../../lib/oci/model-deployment';

const router = express.Router();

const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

function buildCacheKey(userId: string, topK: number): string {
  return `recommender:product:${userId}:${topK}`;
}

function parseTopK(raw: any): number | null {
  if (raw === undefined || raw === null || raw === '') {
    return 10;
  }
  const n = Number(raw);
  if (!Number.isFinite(n) || n < 1 || n > 100) {
    return null;
  }
  return Math.floor(n);
}

/**
 * Core handler used by both POST and GET endpoints.
 */
async function handleProductRecommend(req: express.Request, res: express.Response) {
  try {
    const userId = (req.body?.user_id ?? req.query.user_id) as string | undefined;
    const topK = parseTopK(req.body?.top_k ?? req.query.top_k);

    const errors: string[] = [];
    if (!userId || typeof userId !== 'string' || !userId.trim()) {
      errors.push('user_id is required');
    }
    if (topK === null) {
      errors.push('top_k must be a number between 1 and 100');
    }

    if (errors.length > 0) {
      return res.status(400).json({
        error: 'Validation failed',
        message: 'Invalid request parameters',
        details: { errors },
      });
    }

    const cacheKey = buildCacheKey(userId!, topK!);
    const cached = getCache<any>(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    // Call OCI model deployment
    const result = await predictUserRecs(userId!, topK!);

    // Normalize response shape (defensive): expect { user_id, recommendations, message }
    const response = {
      user_id: (result as any)?.user_id ?? userId,
      recommendations: (result as any)?.recommendations ?? [],
      message: (result as any)?.message ?? 'Success',
    };

    setCache(cacheKey, response, CACHE_TTL_MS);
    return res.json(response);
  } catch (error: any) {
    const message = error?.message || 'Failed to get product recommendations';
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
}

router.post('/', handleProductRecommend);

router.get('/', async (req, res) => {
  // Delegate to the same handler (body vs query parsing handled inside)
  return handleProductRecommend(req, res);
});

export default router;

