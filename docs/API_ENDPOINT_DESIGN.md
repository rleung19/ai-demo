# API Endpoint Design and Data Contracts
## Tasks 1.2 & 1.6: API Structure and Documentation

## Overview

This document defines the REST API endpoints for the Churn Model Backend API, including request/response schemas, error handling, and data contracts.

## Base URL

All endpoints are prefixed with `/api/kpi/churn/`

## Endpoints

### 1. GET /api/kpi/churn/summary

**Purpose**: Returns summary metrics for churn risk analysis

**Request**:
- Method: `GET`
- Path: `/api/kpi/churn/summary`
- Query Parameters: None
- Headers: None required

**Response** (200 OK):
```json
{
  "atRiskCount": 1102,
  "totalCustomers": 4142,
  "atRiskPercentage": 26.61,
  "averageRiskScore": 28.4,
  "totalLTVAtRisk": 2450000.00,
  "modelConfidence": 0.9269,
  "lastUpdate": "2026-01-18T19:23:05Z",
  "modelVersion": "20260118_192250"
}
```

**Response Schema**:
```typescript
interface ChurnSummaryResponse {
  atRiskCount: number;           // Number of customers with churn risk > threshold
  totalCustomers: number;         // Total number of customers analyzed
  atRiskPercentage: number;       // Percentage of at-risk customers (0-100)
  averageRiskScore: number;       // Average churn probability across all customers (0-100)
  totalLTVAtRisk: number;         // Total lifetime value at risk (USD)
  modelConfidence: number;        // Model AUC score (0-1)
  lastUpdate: string;             // ISO 8601 timestamp of last prediction update
  modelVersion: string;           // Model version identifier
}
```

**Error Responses**:
- `503 Service Unavailable`: Database connection failed or model not available
  ```json
  {
    "error": "Service unavailable",
    "message": "Unable to connect to database or load model",
    "fallback": true
  }
  ```

### 2. GET /api/kpi/churn/cohorts

**Purpose**: Returns churn risk breakdown by customer segment/cohort

**Request**:
- Method: `GET`
- Path: `/api/kpi/churn/cohorts`
- Query Parameters: None
- Headers: None required

**Response** (200 OK):
```json
{
  "cohorts": [
    {
      "cohort": "VIP",
      "customerCount": 450,
      "atRiskCount": 45,
      "atRiskPercentage": 10.0,
      "averageRiskScore": 12.5,
      "ltvAtRisk": 125000.00
    },
    {
      "cohort": "Regular",
      "customerCount": 2500,
      "atRiskCount": 625,
      "atRiskPercentage": 25.0,
      "averageRiskScore": 28.3,
      "ltvAtRisk": 1500000.00
    },
    {
      "cohort": "New",
      "customerCount": 892,
      "atRiskCount": 312,
      "atRiskPercentage": 35.0,
      "averageRiskScore": 35.2,
      "ltvAtRisk": 450000.00
    },
    {
      "cohort": "Dormant",
      "customerCount": 300,
      "atRiskCount": 120,
      "atRiskPercentage": 40.0,
      "averageRiskScore": 42.8,
      "ltvAtRisk": 375000.00
    }
  ],
  "lastUpdate": "2026-01-18T19:23:05Z"
}
```

**Response Schema**:
```typescript
interface ChurnCohortsResponse {
  cohorts: CohortData[];
  lastUpdate: string;
}

interface CohortData {
  cohort: string;                 // Cohort name: "VIP", "Regular", "New", "Dormant", "At-Risk"
  customerCount: number;          // Total customers in this cohort
  atRiskCount: number;            // Number of at-risk customers in cohort
  atRiskPercentage: number;       // Percentage of cohort at risk (0-100)
  averageRiskScore: number;       // Average risk score for cohort (0-100)
  ltvAtRisk: number;              // Total LTV at risk for this cohort (USD)
}
```

**Cohort Definitions**:
- **VIP**: Customers with `LIFETIME_VALUE > $5,000` OR `AFFINITY_CARD = 1` (high-value customers or loyalty card holders)
- **Regular**: Active customers with `TOTAL_PURCHASES >= 2`, `DAYS_SINCE_LAST_PURCHASE <= 90`, and `LOGIN_FREQUENCY > 0` (excludes VIP)
- **New**: Customers with `MEMBERSHIP_YEARS < 1` (excludes VIP)
- **Dormant**: Customers with `DAYS_SINCE_LAST_PURCHASE > 90` OR `LOGIN_FREQUENCY = 0` (excludes VIP/New)
- **At-Risk**: Customers with `PREDICTED_CHURN_PROBABILITY > 0.41` (can overlap with other cohorts)

**Data Sources**: All cohort data comes from `OML.USER_PROFILES` (features) joined with `OML.CHURN_PREDICTIONS` (predictions). See `docs/COHORT_DEFINITIONS.md` for detailed SQL queries.

**Error Responses**:
- `503 Service Unavailable`: Database connection failed
  ```json
  {
    "error": "Service unavailable",
    "message": "Unable to load cohort data",
    "fallback": true
  }
  ```

### 3. GET /api/kpi/churn/metrics

**Purpose**: Returns model performance and metadata

**Request**:
- Method: `GET`
- Path: `/api/kpi/churn/metrics`
- Query Parameters: None
- Headers: None required

**Response** (200 OK):
```json
{
  "modelType": "XGBoost Binary Classification",
  "modelVersion": "20260118_192250",
  "aucScore": 0.9269,
  "accuracy": 0.9217,
  "precision": 0.9281,
  "recall": 0.7900,
  "f1Score": 0.8535,
  "optimalThreshold": 0.410,
  "trainingDate": "2026-01-18T19:22:50Z",
  "trainingSamples": 36686,
  "testSamples": 9172,
  "featureCount": 22,
  "status": "ACTIVE",
  "isProduction": true
}
```

**Response Schema**:
```typescript
interface ChurnMetricsResponse {
  modelType: string;              // Model type description
  modelVersion: string;            // Model version identifier
  aucScore: number;                // Area Under Curve (0-1)
  accuracy: number;                // Model accuracy (0-1)
  precision: number;               // Precision score (0-1)
  recall: number;                  // Recall score (0-1)
  f1Score: number;                 // F1 score (0-1)
  optimalThreshold: number;        // Optimal probability threshold (0-1)
  trainingDate: string;            // ISO 8601 timestamp of training
  trainingSamples: number;         // Number of training samples
  testSamples: number;             // Number of test samples
  featureCount: number;            // Number of features used
  status: string;                  // Model status: "ACTIVE", "DEPRECATED", "ARCHIVED"
  isProduction: boolean;           // Whether this is the production model
}
```

**Error Responses**:
- `503 Service Unavailable`: Model registry unavailable
  ```json
  {
    "error": "Service unavailable",
    "message": "Unable to load model metrics",
    "fallback": true
  }
  ```

### 4. GET /api/kpi/churn/chart-data

**Purpose**: Returns time series data for dashboard charts

**Request**:
- Method: `GET`
- Path: `/api/kpi/churn/chart-data`
- Query Parameters:
  - `period` (optional): Time period for data (default: "7w")
    - Values: "7d", "30d", "7w", "12w", "6m", "1y"
- Headers: None required

**Response** (200 OK):
```json
{
  "riskScoreTrend": [
    {
      "date": "2026-01-11",
      "averageRiskScore": 27.5,
      "atRiskCount": 1080,
      "totalCustomers": 4142
    },
    {
      "date": "2026-01-18",
      "averageRiskScore": 28.4,
      "atRiskCount": 1102,
      "totalCustomers": 4142
    }
  ],
  "cohortDistribution": [
    {
      "date": "2026-01-11",
      "cohorts": {
        "VIP": 450,
        "Regular": 2500,
        "New": 892,
        "Dormant": 300
      }
    },
    {
      "date": "2026-01-18",
      "cohorts": {
        "VIP": 450,
        "Regular": 2500,
        "New": 892,
        "Dormant": 300
      }
    }
  ],
  "period": "7w",
  "lastUpdate": "2026-01-18T19:23:05Z"
}
```

**Response Schema**:
```typescript
interface ChurnChartDataResponse {
  riskScoreTrend: RiskTrendPoint[];
  cohortDistribution: CohortDistributionPoint[];
  period: string;                  // Requested period
  lastUpdate: string;               // ISO 8601 timestamp
}

interface RiskTrendPoint {
  date: string;                     // Date in YYYY-MM-DD format
  averageRiskScore: number;        // Average risk score for this date (0-100)
  atRiskCount: number;              // Number of at-risk customers
  totalCustomers: number;           // Total customers analyzed
}

interface CohortDistributionPoint {
  date: string;                     // Date in YYYY-MM-DD format
  cohorts: Record<string, number>; // Cohort name -> customer count
}
```

**Note**: Currently, historical data is limited. The API will return current snapshot data repeated for each date point until `CHURN_PREDICTIONS_HISTORY` table is implemented.

**Error Responses**:
- `400 Bad Request`: Invalid period parameter
  ```json
  {
    "error": "Bad request",
    "message": "Invalid period parameter. Use: 7d, 30d, 7w, 12w, 6m, 1y"
  }
  ```
- `503 Service Unavailable`: Database connection failed
  ```json
  {
    "error": "Service unavailable",
    "message": "Unable to load chart data",
    "fallback": true
  }
  ```

## Common Error Response Format

All error responses follow this structure:

```typescript
interface ErrorResponse {
  error: string;                   // Error type: "Bad request", "Service unavailable", "Internal server error"
  message: string;                 // Human-readable error message
  fallback?: boolean;              // Whether frontend should use fallback data
  details?: string;                // Optional detailed error information (dev only)
}
```

## HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Unexpected server error
- `503 Service Unavailable`: Database/model unavailable, use fallback data

## Data Sources

All endpoints query data from:
- **Primary**: `OML.CHURN_PREDICTIONS` table (current predictions)
- **Model Info**: `OML.MODEL_REGISTRY` table (model metadata)
- **User Data**: `OML.USER_PROFILES` table (for cohort calculation)
- **Historical**: `OML.CHURN_PREDICTIONS_HISTORY` table (future, for trends)

## Frontend Integration

The frontend should:
1. Attempt to fetch from API endpoints
2. If API returns 200, use API data
3. If API returns 503 or network error, fall back to static data from `app/data/synthetic/kpi1-churn-risk.ts`
4. Display loading states during API calls
5. Show indicator when using fallback data

## Rate Limiting

Currently no rate limiting implemented. Consider adding if needed for production.

## Caching

- Responses may be cached for 5 minutes (optional, Task 4.10)
- Model metrics cached for 1 hour (changes infrequently)
- Chart data cached for 15 minutes

## Next Steps

1. Implement endpoints (Task 4.4-4.7)
2. Add request validation (Task 4.8)
3. Add error handling (Task 4.9)
4. Add response caching (Task 4.10, optional)
5. Create OpenAPI/Swagger documentation (Task 4.11)
