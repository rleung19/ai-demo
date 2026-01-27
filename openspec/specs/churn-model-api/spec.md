# churn-model-api Specification

## Purpose
TBD - created by archiving change add-churn-model-backend-api. Update Purpose after archive.
## Requirements
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

### Requirement: Cohort Detail Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/cohorts/:name` that returns detailed information for a specific cohort, including cohort-level summary statistics and a paginated list of users in that cohort.

The endpoint SHALL accept:
- Path parameter `name` - Cohort name (VIP, Regular, New, Dormant, or Other), case-insensitive
- Query parameter `limit` (optional, default: 3, max: 500) - Number of users per page
- Query parameter `offset` (optional, default: 0) - Pagination offset
- Query parameter `sort` (optional, default: `churn`) - Sort order:
  - `churn` = Sort by churn probability descending (highest risk first)
  - `ltv` = Sort by lifetime value descending (highest value first)
- Special value `limit=-1` = Return all users in cohort (ignore `offset`)
- Query parameter `atRiskOnly` (optional, default: `true`) - When `true`, filter the `users` list to only include at-risk customers (`PREDICTED_CHURN_LABEL = 1`)
- Query parameter `minLtv` (optional) - Minimum lifetime value (inclusive) for users in the `users` list; must be a non-negative number when provided
- Query parameter `maxLtv` (optional) - Maximum lifetime value (inclusive) for users in the `users` list; must be a non-negative number when provided, and MUST be greater than or equal to `minLtv` if both are present

The endpoint SHALL return:
- `cohort` - Canonical cohort name (e.g., "VIP")
- `definition` - Human-readable description of cohort criteria
- `summary` - Aggregate statistics matching the cohort entry from the list endpoint:
  - `customerCount` - Total customers in cohort
  - `atRiskCount` - Number of at-risk customers
  - `atRiskPercentage` - Percentage of cohort at risk (0-100)
  - `averageRiskScore` - Average churn probability for cohort (0-100)
  - `ltvAtRisk` - Total lifetime value at risk for cohort (USD)
- `users` - Array of user objects, each containing:
  - `userId` - User UUID (from `USER_PROFILES.USER_ID`)
  - `churnProbability` - Churn probability (0.0-1.0) from `CHURN_PREDICTIONS.PREDICTED_CHURN_PROBABILITY`
  - `ltv` - Lifetime value (USD) from `USER_PROFILES.LIFETIME_VALUE`
- `pagination` - Pagination metadata (always reflects the full cohort, not just filtered users):
  - `total` - Total number of users in cohort
  - `limit` - Requested limit (or -1 if all users requested)
  - `offset` - Requested offset

#### Scenario: Fetch VIP cohort details with pagination
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=3&offset=0&sort=churn`
- **THEN** API queries database for VIP cohort users
- **AND** API filters users where `(LIFETIME_VALUE > 5000 OR AFFINITY_CARD = 1)`
- **AND** API orders users by churn probability descending
- **AND** API returns first 3 users with summary statistics
- **AND** response includes HTTP 200 status code
- **AND** response includes pagination metadata with total count

#### Scenario: Fetch only at-risk VIP users
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=50&offset=0&sort=churn&atRiskOnly=true`
- **THEN** API queries database for VIP cohort users
- **AND** API filters users where `PREDICTED_CHURN_LABEL = 1` (at-risk customers)
- **AND** API orders users by churn probability descending
- **AND** API returns only at-risk VIP users in the `users` array
- **AND** `summary.customerCount` and `pagination.total` still reflect the full VIP cohort size

#### Scenario: Fetch high-LTV at-risk VIP users
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=100&sort=ltv&atRiskOnly=true&minLtv=5000`
- **THEN** API queries database for VIP cohort users
- **AND** API filters users where `PREDICTED_CHURN_LABEL = 1` and `LIFETIME_VALUE >= 5000`
- **AND** API orders users by lifetime value descending
- **AND** API returns only high-LTV, at-risk VIP users in the `users` array
- **AND** `summary.customerCount` and `pagination.total` still reflect the full VIP cohort size

#### Scenario: Fetch all Regular users sorted by LTV
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/Regular?limit=-1&sort=ltv`
- **THEN** API queries database for all Regular cohort users
- **AND** API orders users by lifetime value descending
- **AND** API returns all users (no pagination limit)
- **AND** response includes `pagination.limit = -1` to indicate all users returned

#### Scenario: Handle invalid cohort name
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/InvalidCohort`
- **THEN** API validates cohort name against valid list (VIP, Regular, New, Dormant, Other)
- **AND** API returns HTTP 404 status code
- **AND** response includes error message listing valid cohort names

#### Scenario: Handle invalid query parameters
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=1000&sort=invalid`
- **THEN** API validates `limit` is within range (1-500 or -1)
- **AND** API validates `sort` is either `churn` or `ltv`
- **AND** API validates `atRiskOnly`, if provided, is either `"true"` or `"false"`
- **AND** API validates `minLtv` and `maxLtv`, if provided, are non-negative numbers and `maxLtv >= minLtv` when both are present
- **AND** API returns HTTP 400 status code for invalid parameters
- **AND** response includes error message describing validation failure

#### Scenario: Handle database errors
- **WHEN** database connection fails during cohort detail request
- **THEN** API returns HTTP 503 status code
- **AND** response includes error message
- **AND** error is logged for debugging

#### Scenario: Response caching
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=50&sort=churn`
- **AND** same request was made within the last 60 seconds
- **THEN** API returns cached response
- **AND** response includes same data as original request
- **AND** cache key includes cohort name, limit, offset, and sort parameters

