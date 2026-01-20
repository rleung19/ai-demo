// Minimal OpenAPI 3.0 spec for the Churn ML APIs, used by Swagger UI.
// This is intentionally focused on the main GET endpoints used by the demo.

export const churnOpenApiSpec = {
  openapi: '3.0.0',
  info: {
    title: 'Churn ML API',
    version: '1.0.0',
    description:
      'API for churn risk summary, cohorts, model metrics, chart data, and risk factors used by the AI/ML Executive Dashboard.',
  },
  servers: [
    {
      url: 'http://localhost:3001',
      description: 'Express API Server (local)',
    },
  ],
  paths: {
    '/api/health': {
      get: {
        summary: 'Health check',
        responses: {
          '200': {
            description: 'Service is healthy',
          },
          '503': {
            description: 'Service unavailable',
          },
        },
      },
    },
    '/api/kpi/churn/summary': {
      get: {
        summary: 'Churn summary metrics',
        responses: {
          '200': {
            description: 'Summary metrics',
          },
          '503': {
            description: 'Service unavailable',
          },
        },
      },
    },
    '/api/kpi/churn/cohorts': {
      get: {
        summary: 'Churn cohorts breakdown',
        responses: {
          '200': {
            description: 'Cohort metrics',
          },
          '503': {
            description: 'Service unavailable',
          },
        },
      },
    },
    '/api/kpi/churn/metrics': {
      get: {
        summary: 'Model performance metrics',
        responses: {
          '200': {
            description: 'Model metrics',
          },
          '404': {
            description: 'No active model',
          },
          '503': {
            description: 'Service unavailable',
          },
        },
      },
    },
    '/api/kpi/churn/chart-data': {
      get: {
        summary: 'Churn chart data (distribution or cohort trend)',
        parameters: [
          {
            name: 'type',
            in: 'query',
            schema: {
              type: 'string',
              enum: ['distribution', 'cohort-trend'],
              default: 'distribution',
            },
            description: 'Chart type to return',
          },
        ],
        responses: {
          '200': {
            description: 'Chart data',
          },
          '400': {
            description: 'Invalid query parameters',
          },
          '503': {
            description: 'Service unavailable',
          },
        },
      },
    },
    '/api/kpi/churn/risk-factors': {
      get: {
        summary: 'Top churn risk factors',
        responses: {
          '200': {
            description: 'Risk factor list',
          },
          '503': {
            description: 'Service unavailable',
          },
        },
      },
    },
  },
};

