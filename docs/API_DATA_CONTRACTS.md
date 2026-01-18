# API Data Contracts
## Task 1.6: Request/Response Schema Documentation

This document provides detailed TypeScript type definitions and JSON schemas for all API endpoints.

## Type Definitions

### Summary Endpoint

```typescript
// GET /api/kpi/churn/summary

interface ChurnSummaryResponse {
  atRiskCount: number;           // Customers with churn probability > threshold
  totalCustomers: number;         // Total customers analyzed
  atRiskPercentage: number;       // (atRiskCount / totalCustomers) * 100
  averageRiskScore: number;       // Average churn probability (0-100)
  totalLTVAtRisk: number;         // Sum of LIFETIME_VALUE for at-risk customers
  modelConfidence: number;        // Model AUC score (0-1)
  lastUpdate: string;             // ISO 8601 timestamp
  modelVersion: string;           // Model version ID from MODEL_REGISTRY
}
```

**Example Response**:
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

### Cohorts Endpoint

```typescript
// GET /api/kpi/churn/cohorts

interface ChurnCohortsResponse {
  cohorts: CohortData[];
  lastUpdate: string;
}

interface CohortData {
  cohort: string;                 // "VIP" | "Regular" | "New" | "Dormant" | "At-Risk"
  customerCount: number;          // Total customers in cohort
  atRiskCount: number;            // At-risk customers in cohort
  atRiskPercentage: number;       // (atRiskCount / customerCount) * 100
  averageRiskScore: number;       // Average risk score for cohort (0-100)
  ltvAtRisk: number;              // Total LTV at risk for cohort (USD)
}
```

**Example Response**:
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
    }
  ],
  "lastUpdate": "2026-01-18T19:23:05Z"
}
```

### Metrics Endpoint

```typescript
// GET /api/kpi/churn/metrics

interface ChurnMetricsResponse {
  modelType: string;              // "XGBoost Binary Classification"
  modelVersion: string;            // Model version ID
  aucScore: number;                // Area Under Curve (0-1)
  accuracy: number;                // Accuracy (0-1)
  precision: number;               // Precision (0-1)
  recall: number;                  // Recall (0-1)
  f1Score: number;                 // F1 score (0-1)
  optimalThreshold: number;        // Optimal threshold (0-1)
  trainingDate: string;            // ISO 8601 timestamp
  trainingSamples: number;         // Training dataset size
  testSamples: number;             // Test dataset size
  featureCount: number;            // Number of features
  status: string;                  // "ACTIVE" | "DEPRECATED" | "ARCHIVED"
  isProduction: boolean;           // Production flag
}
```

**Example Response**:
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

### Chart Data Endpoint

```typescript
// GET /api/kpi/churn/chart-data?period=7w

interface ChurnChartDataResponse {
  riskScoreTrend: RiskTrendPoint[];
  cohortDistribution: CohortDistributionPoint[];
  period: string;                  // Requested period
  lastUpdate: string;              // ISO 8601 timestamp
}

interface RiskTrendPoint {
  date: string;                     // YYYY-MM-DD format
  averageRiskScore: number;        // Average risk (0-100)
  atRiskCount: number;             // At-risk customers
  totalCustomers: number;           // Total customers
}

interface CohortDistributionPoint {
  date: string;                     // YYYY-MM-DD format
  cohorts: Record<string, number>; // Cohort name -> count
}
```

**Example Response**:
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
    }
  ],
  "period": "7w",
  "lastUpdate": "2026-01-18T19:23:05Z"
}
```

### Error Response

```typescript
interface ErrorResponse {
  error: string;                   // Error type
  message: string;                 // Human-readable message
  fallback?: boolean;              // Use fallback data?
  details?: string;                // Detailed error (dev only)
}
```

**Example Error Responses**:

400 Bad Request:
```json
{
  "error": "Bad request",
  "message": "Invalid period parameter. Use: 7d, 30d, 7w, 12w, 6m, 1y"
}
```

503 Service Unavailable:
```json
{
  "error": "Service unavailable",
  "message": "Unable to connect to database or load model",
  "fallback": true
}
```

500 Internal Server Error:
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "details": "Database query failed: ORA-00942"
}
```

## Database Query Mappings

### Summary Endpoint Queries

```sql
-- At-risk count and percentage
SELECT 
  COUNT(*) AS total_customers,
  SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score
FROM OML.CHURN_PREDICTIONS;

-- Total LTV at risk
SELECT SUM(up.LIFETIME_VALUE) AS total_ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
WHERE cp.PREDICTED_CHURN_LABEL = 1;

-- Model confidence and version
SELECT AUC_SCORE, MODEL_VERSION, TRAINING_DATE
FROM OML.MODEL_REGISTRY
WHERE IS_PRODUCTION = 1
ORDER BY TRAINING_DATE DESC
FETCH FIRST 1 ROWS ONLY;
```

### Cohorts Endpoint Queries

**Data Sources**:
- `OML.USER_PROFILES` - Customer features (LIFETIME_VALUE, MEMBERSHIP_YEARS, TOTAL_PURCHASES, DAYS_SINCE_LAST_PURCHASE, LOGIN_FREQUENCY)
- `OML.CHURN_PREDICTIONS` - Model predictions (PREDICTED_CHURN_PROBABILITY, PREDICTED_CHURN_LABEL)

**Complete Query** (see `docs/COHORT_DEFINITIONS.md` for details):
```sql
WITH cohort_assignments AS (
  SELECT 
    cp.USER_ID,
    cp.PREDICTED_CHURN_PROBABILITY,
    cp.PREDICTED_CHURN_LABEL,
    up.LIFETIME_VALUE,
    up.MEMBERSHIP_YEARS,
    up.TOTAL_PURCHASES,
    up.DAYS_SINCE_LAST_PURCHASE,
    up.LOGIN_FREQUENCY,
    CASE 
      WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
      WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
      WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
      WHEN up.TOTAL_PURCHASES >= 2 AND up.DAYS_SINCE_LAST_PURCHASE <= 90 AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
      ELSE 'Other'
    END AS cohort
  FROM OML.CHURN_PREDICTIONS cp
  JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
  JOIN ADMIN.USERS au ON up.USER_ID = au.ID
)
SELECT 
  cohort,
  COUNT(*) AS customer_count,
  SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
  SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
FROM cohort_assignments
WHERE cohort != 'Other'
GROUP BY cohort;
```

## Validation Rules

### Summary Response
- `atRiskCount` ≤ `totalCustomers`
- `atRiskPercentage` = (`atRiskCount` / `totalCustomers`) * 100
- `averageRiskScore` ∈ [0, 100]
- `modelConfidence` ∈ [0, 1]
- `totalLTVAtRisk` ≥ 0

### Cohorts Response
- Sum of `cohorts[].customerCount` = `totalCustomers` (from summary)
- `atRiskPercentage` = (`atRiskCount` / `customerCount`) * 100 for each cohort
- `averageRiskScore` ∈ [0, 100] for each cohort

### Metrics Response
- All scores ∈ [0, 1] except `optimalThreshold` which is also [0, 1]
- `trainingSamples` + `testSamples` = total dataset size
- `status` ∈ ["ACTIVE", "DEPRECATED", "ARCHIVED"]

### Chart Data Response
- Dates in ascending order
- `period` matches requested period parameter
- All risk scores ∈ [0, 100]

## Frontend Type Definitions

Create `app/lib/types/churn-api.ts`:

```typescript
export interface ChurnSummaryResponse {
  atRiskCount: number;
  totalCustomers: number;
  atRiskPercentage: number;
  averageRiskScore: number;
  totalLTVAtRisk: number;
  modelConfidence: number;
  lastUpdate: string;
  modelVersion: string;
}

export interface ChurnCohortsResponse {
  cohorts: CohortData[];
  lastUpdate: string;
}

export interface CohortData {
  cohort: string;
  customerCount: number;
  atRiskCount: number;
  atRiskPercentage: number;
  averageRiskScore: number;
  ltvAtRisk: number;
}

export interface ChurnMetricsResponse {
  modelType: string;
  modelVersion: string;
  aucScore: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  optimalThreshold: number;
  trainingDate: string;
  trainingSamples: number;
  testSamples: number;
  featureCount: number;
  status: string;
  isProduction: boolean;
}

export interface ChurnChartDataResponse {
  riskScoreTrend: RiskTrendPoint[];
  cohortDistribution: CohortDistributionPoint[];
  period: string;
  lastUpdate: string;
}

export interface RiskTrendPoint {
  date: string;
  averageRiskScore: number;
  atRiskCount: number;
  totalCustomers: number;
}

export interface CohortDistributionPoint {
  date: string;
  cohorts: Record<string, number>;
}

export interface ErrorResponse {
  error: string;
  message: string;
  fallback?: boolean;
  details?: string;
}
```

## Related Files

- `docs/API_ENDPOINT_DESIGN.md` - Complete endpoint documentation
- `openspec/changes/add-churn-model-backend-api/specs/churn-model-api/spec.md` - OpenSpec requirements
- `app/lib/types/churn-api.ts` - TypeScript types (to be created in Task 5.1)
