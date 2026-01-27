# Change: Add Cohort Detail API

## Why
The existing `GET /api/kpi/churn/cohorts` endpoint returns aggregate statistics for all cohorts (VIP, Regular, New, Dormant), but does not provide detailed user-level information for a specific cohort. Users need to drill down into individual cohorts to see which specific customers are at risk, their churn probabilities, and their lifetime values (LTV) to prioritize retention efforts. This endpoint enables cohort-level analysis and customer segmentation workflows.

## What Changes
- **New API Endpoint**: `GET /api/kpi/churn/cohorts/:name` - Returns detailed information for a specific cohort including:
  - Cohort summary statistics (same aggregates as list endpoint)
  - List of users in the cohort with their `userId`, `churnProbability`, and `ltv`
  - Pagination support (`limit`, `offset`) for large cohorts
  - Sorting options (`sort=churn` by risk, `sort=ltv` by value)
  - Special `limit=-1` to return all users in cohort
- **OpenAPI/Swagger Documentation**: Update `server/openapi.ts` with new endpoint schema
- **Route Registration**: Register new route handler in Express server

## Impact
- **Modified Capability**: `churn-model-api` - Adds new endpoint to existing churn API capability
- **New Code**:
  - `server/routes/churn/cohort-detail.ts` - New route handler for cohort detail endpoint
  - Updates to `server/index.ts` - Register cohort detail route
  - Updates to `server/openapi.ts` - Add endpoint documentation
- **No Breaking Changes**: New endpoint, does not modify existing endpoints
- **No New Dependencies**: Uses existing database connection and caching utilities

## Example Requests & Responses

### Request: Get VIP cohort details (paginated)

**Request**

```http
GET /api/kpi/churn/cohorts/VIP?limit=50&offset=0&sort=churn HTTP/1.1
```

**Response**

```json
{
  "cohort": "VIP",
  "definition": "LIFETIME_VALUE > 5000 OR AFFINITY_CARD = 1",
  "summary": {
    "customerCount": 976,
    "atRiskCount": 248,
    "atRiskPercentage": 25.41,
    "averageRiskScore": 27.78,
    "ltvAtRisk": 331117.12
  },
  "users": [
    {
      "userId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "churnProbability": 0.7234,
      "ltv": 8452.50
    },
    {
      "userId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "churnProbability": 0.6891,
      "ltv": 6200.00
    }
  ],
  "pagination": {
    "total": 976,
    "limit": 50,
    "offset": 0
  }
}
```

### Request: Get all Regular users sorted by LTV

**Request**

```http
GET /api/kpi/churn/cohorts/Regular?limit=-1&sort=ltv HTTP/1.1
```

**Response**

```json
{
  "cohort": "Regular",
  "definition": "TOTAL_PURCHASES >= 2 AND DAYS_SINCE_LAST_PURCHASE <= 90 AND LOGIN_FREQUENCY > 0 (excludes VIP/New)",
  "summary": {
    "customerCount": 2500,
    "atRiskCount": 625,
    "atRiskPercentage": 25.0,
    "averageRiskScore": 28.3,
    "ltvAtRisk": 1500000.00
  },
  "users": [
    {
      "userId": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "churnProbability": 0.4523,
      "ltv": 5120.75
    }
  ],
  "pagination": {
    "total": 2500,
    "limit": -1,
    "offset": 0
  }
}
```

### Error Response: Invalid cohort name

**Request**

```http
GET /api/kpi/churn/cohorts/InvalidCohort HTTP/1.1
```

**Response**

```json
{
  "error": "Not Found",
  "message": "Cohort 'InvalidCohort' not found. Valid cohorts: VIP, Regular, New, Dormant, Other"
}
```
