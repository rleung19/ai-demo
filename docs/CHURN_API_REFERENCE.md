# Churn API Reference

This document describes the REST APIs used by the Churn ML demo. The APIs are implemented both as:

- **Next.js App Router API routes** under `app/api/kpi/churn/*`
- **Express routes** in the standalone server under `server/routes/churn/*`

Unless noted otherwise, the request/response shapes are identical across both implementations.

Base URLs:

- Next.js (App): `https://<your-domain>/api/kpi/churn/...`
- Express (Standalone API): `http://<api-host>:3001/api/kpi/churn/...`

---

## Authentication

These demo APIs are **not authenticated**. In a production system you would add:

- An API Gateway or reverse proxy (e.g., OCI API Gateway, Caddy, NGINX)
- JWT or session-based auth on both Next.js and Express servers

---

## 1. `GET /api/kpi/churn/summary`

Returns high-level churn summary metrics.

### Request

- **Method**: `GET`
- **URL (Next.js)**: `/api/kpi/churn/summary`
- **URL (Express)**: `/api/kpi/churn/summary`
- **Query params**: _None_

### Response `200 OK`

```json
{
  "atRiskCount": 247,
  "totalCustomers": 15000,
  "atRiskPercentage": 12.5,
  "averageRiskScore": 35.4,
  "totalLTVAtRisk": 123456.78,
  "modelConfidence": 0.89,
  "lastUpdate": "2026-01-18T12:34:56.000Z",
  "modelVersion": "churn_xgb_v3"
}
```

### Error Responses

- `503 Service Unavailable` – database error or no data available

---

## 2. `GET /api/kpi/churn/cohorts`

Returns churn risk breakdown by customer segment/cohort (e.g. VIP, New, Regular, Dormant).

### Request

- **Method**: `GET`
- **URL**: `/api/kpi/churn/cohorts`
- **Query params**: _None_ (segments are computed server-side)

### Response `200 OK`

```json
{
  "cohorts": [
    {
      "cohort": "VIP",
      "customerCount": 1200,
      "atRiskCount": 150,
      "atRiskPercentage": 12.5,
      "averageRiskScore": 42.1,
      "ltvAtRisk": 75000.0
    }
    // ...
  ]
}
```

### Error Responses

- `503 Service Unavailable` – database or query error

---

## 3. `GET /api/kpi/churn/metrics`

Returns model performance metrics and metadata for the active churn model.

### Request

- **Method**: `GET`
- **URL**: `/api/kpi/churn/metrics`
- **Query params**: _None_

### Response `200 OK`

```json
{
  "modelId": "churn_xgb_20260118",
  "modelName": "Churn XGBoost",
  "modelVersion": "v3",
  "modelType": "XGBOOST",
  "modelConfidence": 0.89,
  "accuracy": 0.92,
  "precision": 0.76,
  "recall": 0.71,
  "f1Score": 0.73,
  "optimalThreshold": 0.37,
  "lastUpdate": "2026-01-18T12:34:56.000Z",
  "trainingStats": {
    "trainSamples": 12000,
    "testSamples": 3000,
    "featureCount": 25
  },
  "status": "ACTIVE"
}
```

### Error Responses

- `404 Not Found` – no active model in `MODEL_REGISTRY`
- `503 Service Unavailable` – database or query error

---

## 4. `GET /api/kpi/churn/chart-data`

Returns binned churn risk distribution data for charting.

### Request

- **Method**: `GET`
- **URL**: `/api/kpi/churn/chart-data`
- **Query params**:
  - `type` (optional, string)
    - `"distribution"` (default) – bucketed risk distribution
    - `"cohort-trend"` – placeholder; currently returns an empty dataset with a message

### Response `200 OK` (type = `distribution`)

```json
{
  "chartType": "distribution",
  "data": [
    {
      "riskRange": "< 10%",
      "customerCount": 5000,
      "atRiskCount": 200
    },
    {
      "riskRange": "10-20%",
      "customerCount": 3000,
      "atRiskCount": 400
    }
    // ...
  ]
}
```

### Response `200 OK` (type = `cohort-trend`)

```json
{
  "chartType": "cohort-trend",
  "message": "Historical trend data not yet available",
  "data": []
}
```

### Error Responses

- `400 Bad Request` – invalid `type` parameter
- `503 Service Unavailable` – database or query error

---

## 5. `GET /api/kpi/churn/risk-factors`

Returns the top churn risk factors with impact scores and affected customer counts.

### Request

- **Method**: `GET`
- **URL**: `/api/kpi/churn/risk-factors`
- **Query params**: _None_ (factors are derived from model outputs and user attributes)

### Response `200 OK`

```json
{
  "riskFactors": [
    {
      "riskFactor": "Email Engagement Decay",
      "impactScore": "68.4%",
      "affectedCustomers": 3200,
      "primarySegment": "Dormant, Regular"
    }
    // ...
  ],
  "lastUpdate": "2026-01-18T12:34:56.000Z"
}
```

### Error Responses

- `503 Service Unavailable` – database or query error

---

## 6. `GET /api/health`

Simple health check endpoint used by monitoring and readiness probes.

### Request

- **Method**: `GET`
- **URL (Next.js)**: `/api/health`
- **URL (Express)**: `/api/health`

### Response `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T12:34:56.000Z",
  "services": {
    "database": "connected"
  },
  "environment": {
    "hasWalletPath": true,
    "hasConnectionString": true,
    "hasUsername": true,
    "hasPassword": true
  }
}
```

### Error Responses

- `503 Service Unavailable` – database connection or configuration failure

---

## Caching Behavior

To reduce load on Oracle ADB and improve response times, the following endpoints are cached in memory on both the Express server and Next.js API routes:

- `GET /api/kpi/churn/summary` – 60s TTL
- `GET /api/kpi/churn/cohorts` – 60s TTL
- `GET /api/kpi/churn/metrics` – 60s TTL
- `GET /api/kpi/churn/chart-data` – 60s TTL per `type`
- `GET /api/kpi/churn/risk-factors` – 5 minutes TTL (expensive aggregation)

Implementation details:

- **Express**: `server/lib/cache.ts` with `getCache` / `setCache`.
- **Next.js**: `app/lib/api/cache.ts` with matching helpers.
- Caches are **per process** and not shared across instances; acceptable for this demo.

