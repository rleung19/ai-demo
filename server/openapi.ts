// OpenAPI 3.0 spec for the Ecommerce ML APIs (Churn + Recommender), used by Swagger UI.
// All examples are based on real API responses from production.

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
        description: 'Check API and database connectivity status',
        responses: {
          '200': {
            description: 'Service is healthy',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    status: { type: 'string', example: 'healthy' },
                    timestamp: { type: 'string', format: 'date-time', example: '2026-01-24T04:56:08.645Z' },
                    services: {
                      type: 'object',
                      properties: {
                        database: { type: 'string', example: 'connected' },
                      },
                    },
                    environment: {
                      type: 'object',
                      properties: {
                        hasWalletPath: { type: 'boolean', example: true },
                        hasConnectionString: { type: 'boolean', example: true },
                        hasUsername: { type: 'boolean', example: true },
                        hasPassword: { type: 'boolean', example: true },
                        tnsAdmin: { type: 'string', example: '/opt/oracle/wallet' },
                      },
                    },
                  },
                },
                example: {
                  status: 'healthy',
                  timestamp: '2026-01-24T04:56:08.645Z',
                  services: {
                    database: 'connected',
                  },
                  environment: {
                    hasWalletPath: true,
                    hasConnectionString: true,
                    hasUsername: true,
                    hasPassword: true,
                    tnsAdmin: '/opt/oracle/wallet',
                  },
                },
              },
            },
          },
          '503': {
            description: 'Service unavailable',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    status: { type: 'string', example: 'unhealthy' },
                    error: { type: 'string', example: 'Database connection failed' },
                  },
                },
              },
            },
          },
        },
      },
    },
    '/api/kpi/churn/summary': {
      get: {
        summary: 'Churn summary metrics',
        description: 'Get overall churn risk summary including at-risk customer count, percentages, and LTV metrics',
        responses: {
          '200': {
            description: 'Summary metrics',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    atRiskCount: { type: 'integer', example: 1341, description: 'Number of customers at risk' },
                    totalCustomers: { type: 'integer', example: 5003, description: 'Total customer count' },
                    atRiskPercentage: { type: 'number', example: 26.8, description: 'Percentage of at-risk customers' },
                    averageRiskScore: { type: 'number', example: 29.16, description: 'Average churn risk score' },
                    totalLTVAtRisk: { type: 'number', example: 1804340.15, description: 'Total lifetime value at risk' },
                    modelConfidence: { type: 'number', example: 0.9285, description: 'ML model confidence score' },
                    lastUpdate: { type: 'string', format: 'date-time', example: '2026-01-20T14:41:51.000Z' },
                    modelVersion: { type: 'string', example: '20260120_224151' },
                  },
                },
                example: {
                  atRiskCount: 1341,
                  totalCustomers: 5003,
                  atRiskPercentage: 26.8,
                  averageRiskScore: 29.16,
                  totalLTVAtRisk: 1804340.15,
                  modelConfidence: 0.9285,
                  lastUpdate: '2026-01-20T14:41:51.000Z',
                  modelVersion: '20260120_224151',
                },
              },
            },
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
        description: 'Get churn risk breakdown by customer cohort (VIP, Regular, New, Dormant)',
        responses: {
          '200': {
            description: 'Cohort metrics',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    cohorts: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          cohort: { type: 'string', example: 'VIP' },
                          customerCount: { type: 'integer', example: 976 },
                          atRiskCount: { type: 'integer', example: 248 },
                          atRiskPercentage: { type: 'number', example: 25.41 },
                          averageRiskScore: { type: 'number', example: 27.78 },
                          ltvAtRisk: { type: 'number', example: 331117.12 },
                        },
                      },
                    },
                  },
                },
                example: {
                  cohorts: [
                    {
                      cohort: 'VIP',
                      customerCount: 976,
                      atRiskCount: 248,
                      atRiskPercentage: 25.41,
                      averageRiskScore: 27.78,
                      ltvAtRisk: 331117.12,
                    },
                    {
                      cohort: 'Regular',
                      customerCount: 3000,
                      atRiskCount: 685,
                      atRiskPercentage: 22.83,
                      averageRiskScore: 26.06,
                      ltvAtRisk: 1053585.44,
                    },
                    {
                      cohort: 'New',
                      customerCount: 595,
                      atRiskCount: 174,
                      atRiskPercentage: 29.24,
                      averageRiskScore: 30.32,
                      ltvAtRisk: 211533.57,
                    },
                    {
                      cohort: 'Dormant',
                      customerCount: 426,
                      atRiskCount: 230,
                      atRiskPercentage: 53.99,
                      averageRiskScore: 52,
                      ltvAtRisk: 207718.38,
                    },
                  ],
                },
              },
            },
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
        description: 'Get ML model performance metrics including accuracy, precision, recall, and F1 score',
        responses: {
          '200': {
            description: 'Model metrics',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    modelId: { type: 'string', example: '20260120_224151' },
                    modelName: { type: 'string', example: 'XGBoost' },
                    modelVersion: { type: 'string', example: '20260120_224151' },
                    modelType: { type: 'string', example: 'XGBoost' },
                    modelConfidence: { type: 'number', example: 0.9285 },
                    accuracy: { type: 'number', example: 0.9227, description: 'Model accuracy' },
                    precision: { type: 'number', example: 0.9182, description: 'Model precision' },
                    recall: { type: 'number', example: 0.8038, description: 'Model recall' },
                    f1Score: { type: 'number', example: 0.8572, description: 'F1 score' },
                    optimalThreshold: { type: 'number', example: 0.42, description: 'Optimal classification threshold' },
                    lastUpdate: { type: 'string', format: 'date-time', example: '2026-01-20T14:41:51.000Z' },
                    trainingStats: {
                      type: 'object',
                      properties: {
                        trainSamples: { type: 'integer', example: 35997 },
                        testSamples: { type: 'integer', example: 9000 },
                        featureCount: { type: 'integer', example: 22 },
                      },
                    },
                    status: { type: 'string', example: 'ACTIVE' },
                  },
                },
                example: {
                  modelId: '20260120_224151',
                  modelName: 'XGBoost',
                  modelVersion: '20260120_224151',
                  modelType: 'XGBoost',
                  modelConfidence: 0.9285,
                  accuracy: 0.9227,
                  precision: 0.9182,
                  recall: 0.8038,
                  f1Score: 0.8572,
                  optimalThreshold: 0.42,
                  lastUpdate: '2026-01-20T14:41:51.000Z',
                  trainingStats: {
                    trainSamples: 35997,
                    testSamples: 9000,
                    featureCount: 22,
                  },
                  status: 'ACTIVE',
                },
              },
            },
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
        description: 'Get chart data for visualization - either risk distribution histogram or cohort trend over time',
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
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    chartType: { type: 'string', example: 'distribution' },
                    data: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          riskRange: { type: 'string', example: '< 10%' },
                          customerCount: { type: 'integer', example: 2943 },
                          atRiskCount: { type: 'integer', example: 0 },
                        },
                      },
                    },
                  },
                },
                example: {
                  chartType: 'distribution',
                  data: [
                    { riskRange: '< 10%', customerCount: 2943, atRiskCount: 0 },
                    { riskRange: '10-20%', customerCount: 440, atRiskCount: 0 },
                    { riskRange: '20-30%', customerCount: 147, atRiskCount: 0 },
                    { riskRange: '30-40%', customerCount: 117, atRiskCount: 0 },
                    { riskRange: '40-50%', customerCount: 90, atRiskCount: 75 },
                    { riskRange: '50-60%', customerCount: 70, atRiskCount: 70 },
                    { riskRange: '60-70%', customerCount: 86, atRiskCount: 86 },
                    { riskRange: '70-80%', customerCount: 119, atRiskCount: 119 },
                    { riskRange: '80-90%', customerCount: 142, atRiskCount: 142 },
                    { riskRange: '>= 90%', customerCount: 849, atRiskCount: 849 },
                  ],
                },
              },
            },
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
        description: 'Get the top risk factors driving customer churn, with impact scores and affected customer counts',
        responses: {
          '200': {
            description: 'Risk factor list',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    riskFactors: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          riskFactor: { type: 'string', example: 'No Purchase in 45+ Days' },
                          impactScore: { type: 'string', example: '40.5%', description: 'Impact on churn probability' },
                          affectedCustomers: { type: 'integer', example: 993, description: 'Number of customers affected' },
                          primarySegment: { type: 'string', example: 'Regular, Dormant', description: 'Primary customer segments' },
                        },
                      },
                    },
                    lastUpdate: { type: 'string', format: 'date-time', example: '2026-01-24T04:56:16.300Z' },
                  },
                },
                example: {
                  riskFactors: [
                    {
                      riskFactor: 'No Purchase in 45+ Days',
                      impactScore: '40.5%',
                      affectedCustomers: 993,
                      primarySegment: 'Regular, Dormant',
                    },
                    {
                      riskFactor: 'Email Engagement Decay',
                      impactScore: '36.7%',
                      affectedCustomers: 2669,
                      primarySegment: 'Regular, VIP',
                    },
                    {
                      riskFactor: 'Size/Fit Issues (2+ returns)',
                      impactScore: '34.7%',
                      affectedCustomers: 66,
                      primarySegment: 'Regular, VIP',
                    },
                    {
                      riskFactor: 'Price Sensitivity (cart abandons)',
                      impactScore: '33.7%',
                      affectedCustomers: 3423,
                      primarySegment: 'Regular, VIP',
                    },
                    {
                      riskFactor: 'Negative Review Sentiment',
                      impactScore: '31.2%',
                      affectedCustomers: 4483,
                      primarySegment: 'Regular, VIP',
                    },
                  ],
                  lastUpdate: '2026-01-24T04:56:16.300Z',
                },
              },
            },
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
              minimum: 1,
              maximum: 100,
            },
            description: 'Number of recommendations to return (1-100)',
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
                          product_id: { type: 'string', example: 'B099DDH2RG', description: 'Product identifier' },
                          rating: { type: 'number', example: 3.845543881667073, description: 'Predicted rating/score' },
                        },
                      },
                    },
                    message: { type: 'string', example: 'Success' },
                  },
                },
                example: {
                  user_id: '100773',
                  recommendations: [
                    { product_id: 'B099DDH2RG', rating: 3.845543881667073 },
                    { product_id: 'B07SN9RS13', rating: 3.8321897411770967 },
                    { product_id: 'B08SC3KCGM', rating: 3.798262404007028 },
                    { product_id: 'B09BF5VNBS', rating: 3.7935598359514113 },
                    { product_id: 'B000K3D982', rating: 3.783557811959144 },
                  ],
                  message: 'Success',
                },
              },
            },
          },
          '400': {
            description: 'Missing or invalid parameters',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    error: { type: 'string', example: 'Validation failed' },
                    message: { type: 'string', example: 'Invalid request parameters' },
                    details: {
                      type: 'object',
                      properties: {
                        errors: {
                          type: 'array',
                          items: { type: 'string' },
                          example: ['user_id is required'],
                        },
                      },
                    },
                  },
                },
              },
            },
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
                    description: 'Number of recommendations to return (1-100)',
                    default: 5,
                    minimum: 1,
                    maximum: 100,
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
                          product_id: { type: 'string', example: 'B099DDH2RG', description: 'Product identifier' },
                          rating: { type: 'number', example: 3.845543881667073, description: 'Predicted rating/score' },
                        },
                      },
                    },
                    message: { type: 'string', example: 'Success' },
                  },
                },
                example: {
                  user_id: '100773',
                  recommendations: [
                    { product_id: 'B099DDH2RG', rating: 3.845543881667073 },
                    { product_id: 'B07SN9RS13', rating: 3.8321897411770967 },
                    { product_id: 'B08SC3KCGM', rating: 3.798262404007028 },
                    { product_id: 'B09BF5VNBS', rating: 3.7935598359514113 },
                    { product_id: 'B000K3D982', rating: 3.783557811959144 },
                  ],
                  message: 'Success',
                },
              },
            },
          },
          '400': {
            description: 'Missing or invalid parameters',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    error: { type: 'string', example: 'Validation failed' },
                    message: { type: 'string', example: 'Invalid request parameters' },
                    details: {
                      type: 'object',
                      properties: {
                        errors: {
                          type: 'array',
                          items: { type: 'string' },
                          example: ['user_id is required'],
                        },
                      },
                    },
                  },
                },
              },
            },
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
        description: 'Get product recommendations based on current shopping basket items using association rules (market basket analysis).',
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
                    items: { type: 'string' },
                    description: 'Array of product IDs currently in basket',
                    example: ['B01CG1J7XG', 'B0BKZHSDGP', 'B094H5S3TY'],
                  },
                  top_n: {
                    type: 'integer',
                    description: 'Number of association rules/recommendations to return (1-100)',
                    default: 3,
                    minimum: 1,
                    maximum: 100,
                  },
                },
              },
              example: {
                basket: ['B01CG1J7XG', 'B0BKZHSDGP', 'B094H5S3TY'],
                top_n: 3,
              },
            },
          },
        },
        responses: {
          '200': {
            description: 'Successful recommendations based on association rules',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    basket: {
                      type: 'array',
                      items: { type: 'string' },
                      description: 'Original basket product IDs',
                      example: ['B01CG1J7XG', 'B0BKZHSDGP', 'B094H5S3TY'],
                    },
                    recommendations: {
                      type: 'array',
                      description: 'Recommended product combinations with association metrics',
                      items: {
                        type: 'object',
                        properties: {
                          products: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'Recommended product ID(s) that go well with basket',
                            example: ['B07KX2N7TM', 'B0BFPXJ2YD'],
                          },
                          confidence: {
                            type: 'number',
                            example: 1.0,
                            description: 'Rule confidence (probability that consequent occurs given antecedent)',
                          },
                          lift: {
                            type: 'number',
                            example: 19.0,
                            description: 'Association strength (lift > 1 means positive correlation)',
                          },
                        },
                      },
                    },
                    message: { type: 'string', example: 'Success' },
                  },
                },
                example: {
                  basket: ['B01CG1J7XG', 'B0BKZHSDGP', 'B094H5S3TY'],
                  recommendations: [
                    {
                      products: ['B01CG1J7XG', 'B07KX2N7TM', 'B0BFPXJ2YD'],
                      confidence: 1.0,
                      lift: 19.0,
                    },
                    {
                      products: ['B07KX2N7TM', 'B094H5S3TY'],
                      confidence: 1.0,
                      lift: 19.0,
                    },
                    {
                      products: ['B0BFPXJ2YD', 'B0BKZHSDGP'],
                      confidence: 1.0,
                      lift: 19.0,
                    },
                  ],
                  message: 'Success',
                },
              },
            },
          },
          '400': {
            description: 'Missing or invalid basket',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    error: { type: 'string', example: 'Validation failed' },
                    message: { type: 'string', example: 'Invalid request parameters' },
                    details: {
                      type: 'object',
                      properties: {
                        errors: {
                          type: 'array',
                          items: { type: 'string' },
                          example: ['basket must be a non-empty array of product IDs'],
                        },
                      },
                    },
                  },
                },
              },
            },
          },
          '500': {
            description: 'OCI service error',
          },
        },
      },
    },
  },
};
