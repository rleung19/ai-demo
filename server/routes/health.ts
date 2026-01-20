/**
 * Health Check Route
 * GET /api/health
 */

import express from 'express';
import { testConnection } from '../lib/db/oracle';

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const dbConnected = await testConnection();

    const health = {
      status: dbConnected ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      services: {
        database: dbConnected ? 'connected' : 'disconnected',
      },
      environment: {
        hasWalletPath: !!process.env.ADB_WALLET_PATH,
        hasConnectionString: !!process.env.ADB_CONNECTION_STRING,
        hasUsername: !!process.env.ADB_USERNAME,
        hasPassword: !!process.env.ADB_PASSWORD,
        tnsAdmin: process.env.TNS_ADMIN || 'not set',
      },
    };

    res.status(dbConnected ? 200 : 503).json(health);
  } catch (error: any) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
    });
  }
});

export default router;
