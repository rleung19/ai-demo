// OpenAPI 3.0 spec for the Ecommerce ML APIs (Churn + Recommender), used by Swagger UI.

export const churnOpenApiSpec = {
  openapi: '3.0.0',
  info: {
    title: 'Ecommerce ML API',
    version: '1.0.0',
    description:
      'API for churn analytics (risk summary, cohorts, metrics, chart data) and product/basket recommendations powered by OCI Data Science models.',
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
    '/api/recommender/product': {
      get: {
        summary: 'Product recommendations (convenience GET)',
        description: 'Get product recommendations for a user. Accepts user_id as query parameter.',
        parameters: [
          {
            name: 'user_id',
            in: 'query',
            required: true,
            schema: {
              type: 'string',
            },
            description: 'Customer user ID',
            example: '100773',
          },
          {
            name: 'top_k',
            in: 'query',
            schema: {
              type: 'integer',
              default: 5,
            },
            description: 'Number of recommendations to return',
          },
        ],
        responses: {
          '200': {
            description: 'Successful recommendations',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    user_id: { type: 'string', example: '100773' },
                    recommendations: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          product_id: { type: 'integer', example: 2 },
                          score: { type: 'number', example: 0.85 },
                        },
                      },
                    },
                    message: { type: 'string', example: 'Success' },
                  },
                },
              },
            },
          },
          '400': {
            description: 'Missing or invalid parameters',
          },
          '500': {
            description: 'OCI service error',
          },
        },
      },
      post: {
        summary: 'Product recommendations (POST)',
        description: 'Get product recommendations for a user. POST version for programmatic access.',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['user_id'],
                properties: {
                  user_id: {
                    type: 'string',
                    description: 'Customer user ID',
                    example: '100773',
                  },
                  top_k: {
                    type: 'integer',
                    description: 'Number of recommendations to return',
                    default: 5,
                  },
                },
              },
              example: {
                user_id: '100773',
                top_k: 5,
              },
            },
          },
        },
        responses: {
          '200': {
            description: 'Successful recommendations',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    user_id: { type: 'string', example: '100773' },
                    recommendations: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          product_id: { type: 'integer', example: 2 },
                          score: { type: 'number', example: 0.85 },
                        },
                      },
                    },
                    message: { type: 'string', example: 'Success' },
                  },
                },
              },
            },
          },
          '400': {
            description: 'Missing or invalid parameters',
          },
          '500': {
            description: 'OCI service error',
          },
        },
      },
    },
    '/api/recommender/basket': {
      post: {
        summary: 'Basket recommendations',
        description: 'Get product recommendations based on current shopping basket items.',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['basket'],
                properties: {
                  basket: {
                    type: 'array',
                    items: { type: 'integer' },
                    description: 'Array of product IDs currently in basket',
                    example: [46, 41],
                  },
                  top_k: {
                    type: 'integer',
                    description: 'Number of recommendations to return',
                    default: 5,
                  },
                },
              },
              example: {
                basket: [46, 41],
                top_k: 5,
              },
            },
          },
        },
        responses: {
          '200': {
            description: 'Successful recommendations',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    basket: {
                      type: 'array',
                      items: { type: 'integer' },
                      example: [46, 41],
                    },
                    recommendations: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          product_id: { type: 'integer', example: 45 },
                          score: { type: 'number', example: 0.72 },
                        },
                      },
                    },
                    message: { type: 'string', example: 'Success' },
                  },
                },
              },
            },
          },
          '400': {
            description: 'Missing or invalid basket',
          },
          '500': {
            description: 'OCI service error',
          },
        },
      },
    },
  },
};

