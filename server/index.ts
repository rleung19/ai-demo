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
import swaggerUi from 'swagger-ui-express';

// Load environment variables
// Use process.cwd() which is always the project root where node was started
dotenv.config({ path: path.join(process.cwd(), '.env') });

// Import API routes
import healthRoutes from './routes/health';
import churnSummaryRoutes from './routes/churn/summary';
import churnCohortsRoutes from './routes/churn/cohorts';
import churnMetricsRoutes from './routes/churn/metrics';
import churnChartDataRoutes from './routes/churn/chart-data';
import churnRiskFactorsRoutes from './routes/churn/risk-factors';
import productRecommenderRoutes from './routes/recommender/product';
import basketRecommenderRoutes from './routes/recommender/basket';
import { generateOpenApiSpec } from './openapi';

// Import database utilities
import { initializePool, closePool } from './lib/db/oracle';

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

// Swagger UI - API documentation (dynamic spec based on request)
app.use('/api-docs', swaggerUi.serve);
app.get('/api-docs', (req, res) => {
  // Generate spec dynamically based on the request
  const spec = generateOpenApiSpec(req);
  const html = swaggerUi.generateHTML(spec);
  res.send(html);
});

// OpenAPI spec endpoint (dynamic based on request)
app.get('/openapi.json', (req, res) => {
  res.json(generateOpenApiSpec(req));
});

// API Routes
app.use('/api/health', healthRoutes);
app.use('/api/kpi/churn/summary', churnSummaryRoutes);
app.use('/api/kpi/churn/cohorts', churnCohortsRoutes);
app.use('/api/kpi/churn/metrics', churnMetricsRoutes);
app.use('/api/kpi/churn/chart-data', churnChartDataRoutes);
app.use('/api/kpi/churn/risk-factors', churnRiskFactorsRoutes);
app.use('/api/recommender/product', productRecommenderRoutes);
app.use('/api/recommender/basket', basketRecommenderRoutes);

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
      riskFactors: '/api/kpi/churn/risk-factors',
      productRecommender: '/api/recommender/product',
      basketRecommender: '/api/recommender/basket',
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
app.listen(PORT, async () => {
  console.log('='.repeat(60));
  console.log('Churn Model API Server');
  console.log('='.repeat(60));
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`TNS_ADMIN: ${process.env.TNS_ADMIN || 'not set'}`);
  console.log(`ADB_WALLET_PATH: ${process.env.ADB_WALLET_PATH || 'not set'}`);
  console.log('='.repeat(60));
  
  // Initialize connection pool at startup (non-blocking)
  initializePool().catch((err) => {
    console.error('Failed to initialize pool at startup:', err.message);
  });
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing connection pool...');
  await closePool();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, closing connection pool...');
  await closePool();
  process.exit(0);
});
