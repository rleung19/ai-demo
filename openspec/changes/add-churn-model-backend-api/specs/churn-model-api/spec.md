# churn-model-api Specification

## Purpose
Backend REST API capability for serving churn prediction model results to the KPI dashboard. Provides endpoints for KPI #1 (Churn Risk Score) metrics, cohort analysis, and model information.

## ADDED Requirements

### Requirement: Churn Summary Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/summary` that returns summary metrics for churn risk analysis.

The endpoint SHALL return:
- Total at-risk customers count
- Average risk score (percentage)
- Total LTV at risk (dollar amount)
- Model confidence score
- Last model update timestamp

#### Scenario: Fetch churn summary
- **WHEN** frontend requests `GET /api/kpi/churn/summary`
- **THEN** API loads the latest churn model from OML datastore
- **AND** API scores all active customers
- **AND** API aggregates results and returns JSON with summary metrics
- **AND** response includes HTTP 200 status code

#### Scenario: Handle model not found
- **WHEN** no model exists in OML datastore
- **THEN** API returns HTTP 503 with error message
- **AND** frontend falls back to static data

### Requirement: Cohort Breakdown Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/cohorts` that returns churn risk breakdown by customer segment.

The endpoint SHALL return:
- Risk scores per cohort (VIP, Regular, New, Dormant, At-Risk)
- Customer counts per cohort
- Average risk percentage per cohort
- LTV at risk per cohort

#### Scenario: Fetch cohort breakdown
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts`
- **THEN** API scores customers and groups by segment
- **AND** API calculates aggregate metrics per cohort
- **AND** API returns JSON array with cohort data

### Requirement: Model Metrics Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/metrics` that returns model performance and metadata.

The endpoint SHALL return:
- Model type (e.g., "XGBoost Binary Classification")
- Model confidence/AUC score
- Training data description
- Last training timestamp
- Model version identifier

#### Scenario: Fetch model metrics
- **WHEN** frontend requests `GET /api/kpi/churn/metrics`
- **THEN** API retrieves model metadata from OML datastore
- **AND** API returns JSON with model information

### Requirement: Chart Data Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/chart-data` that returns time series data for dashboard charts.

The endpoint SHALL return:
- Risk score trends over time (last 7 weeks)
- Cohort distribution over time
- Historical churn predictions

#### Scenario: Fetch chart data
- **WHEN** frontend requests `GET /api/kpi/churn/chart-data?period=7w`
- **THEN** API queries historical predictions or generates trend data
- **AND** API returns JSON with chart-ready data structure

### Requirement: Database Connection
The system SHALL connect to Oracle Autonomous Database Serverless using wallet-based authentication.

The connection SHALL:
- Use OML4Py for model operations (Python pipeline)
- Use oracledb/cx_Oracle for API server (Node.js)
- Support both ADMIN and OML schemas
- Handle connection errors gracefully

#### Scenario: Establish database connection
- **WHEN** API server starts
- **THEN** connection pool is established to ADB
- **AND** connection uses wallet files from environment variable
- **AND** connection errors are logged and API returns 503 status

### Requirement: Model Loading and Scoring
The system SHALL load churn models from OML datastore and score customer data on-demand.

The scoring process SHALL:
- Load latest model version from OML datastore
- Prepare customer features from database views
- Generate churn probability predictions
- Aggregate results for API responses

#### Scenario: Score customers for API request
- **WHEN** API endpoint requires customer scores
- **THEN** API loads model from OML datastore
- **AND** API queries feature views for current customers
- **AND** API generates predictions using loaded model
- **AND** API caches results for subsequent requests (optional)

### Requirement: Error Handling
The system SHALL handle errors gracefully and provide meaningful error responses.

Error handling SHALL:
- Return appropriate HTTP status codes (200, 400, 500, 503)
- Include error messages in JSON responses
- Log errors for debugging
- Support frontend fallback to static data

#### Scenario: Handle database connection error
- **WHEN** database connection fails
- **THEN** API returns HTTP 503 with error message
- **AND** error is logged with details
- **AND** frontend can fall back to static data
