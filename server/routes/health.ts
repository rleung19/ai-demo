/**
 * Health Check Route
 * GET /api/health
 */

import express from 'express';
import { getDbBackend, testConnection } from '../lib/db';

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const backend = getDbBackend();
    const dbConnected = await testConnection();

    const health = {
      status: dbConnected ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      services: {
        database: dbConnected ? 'connected' : 'disconnected',
      },
      database: {
        backend,
        connected: dbConnected,
      },
      environment:
        backend === 'postgres'
          ? {
              hasDatabaseUrl: !!process.env.DATABASE_URL,
              pgHost: process.env.PGHOST || 'not set',
              pgDatabase: process.env.PGDATABASE || 'not set',
            }
          : {
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
