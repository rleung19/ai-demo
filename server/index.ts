/**
 * Standalone Express API Server for Churn Model Backend
 * 
 * This server provides the same API endpoints as Next.js API routes,
 * but runs as a separate Express server to avoid Next.js native module issues.
 * 
 * Usage:
 *   npm run server:dev    # Development mode with hot reload
 *   npm run server:start  # Production mode
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
const envFile = path.join(__dirname, '..', '.env');
dotenv.config({ path: envFile });

// Import API routes
import healthRoutes from './routes/health';
import churnSummaryRoutes from './routes/churn/summary';
import churnCohortsRoutes from './routes/churn/cohorts';
import churnMetricsRoutes from './routes/churn/metrics';
import churnChartDataRoutes from './routes/churn/chart-data';

const app = express();
// Use API_PORT from env, but default to 3001 to avoid conflict with Next.js (3000)
// If API_PORT=3000 is set, warn and use 3001 instead
let PORT = parseInt(process.env.API_PORT || '3001', 10);
if (PORT === 3000) {
  console.warn('⚠️  WARNING: API_PORT=3000 conflicts with Next.js default port');
  console.warn('   Using port 3001 instead. Set API_PORT=3001 in .env to avoid this warning.');
  PORT = 3001;
}

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
});

// API Routes
app.use('/api/health', healthRoutes);
app.use('/api/kpi/churn/summary', churnSummaryRoutes);
app.use('/api/kpi/churn/cohorts', churnCohortsRoutes);
app.use('/api/kpi/churn/metrics', churnMetricsRoutes);
app.use('/api/kpi/churn/chart-data', churnChartDataRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Churn Model API Server',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      summary: '/api/kpi/churn/summary',
      cohorts: '/api/kpi/churn/cohorts',
      metrics: '/api/kpi/churn/metrics',
      chartData: '/api/kpi/churn/chart-data',
    },
  });
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    fallback: true,
  });
});

// Start server
app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('Churn Model API Server');
  console.log('='.repeat(60));
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`TNS_ADMIN: ${process.env.TNS_ADMIN || 'not set'}`);
  console.log(`ADB_WALLET_PATH: ${process.env.ADB_WALLET_PATH || 'not set'}`);
  console.log('='.repeat(60));
});
