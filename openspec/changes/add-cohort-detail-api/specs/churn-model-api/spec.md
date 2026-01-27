## ADDED Requirements

### Requirement: Cohort Detail Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/cohorts/:name` that returns detailed information for a specific cohort, including cohort-level summary statistics and a paginated list of users in that cohort.

The endpoint SHALL accept:
- Path parameter `name` - Cohort name (VIP, Regular, New, Dormant, or Other), case-insensitive
- Query parameter `limit` (optional, default: 50, max: 500) - Number of users per page
- Query parameter `offset` (optional, default: 0) - Pagination offset
- Query parameter `sort` (optional, default: `churn`) - Sort order:
  - `churn` = Sort by churn probability descending (highest risk first)
  - `ltv` = Sort by lifetime value descending (highest value first)
- Special value `limit=-1` = Return all users in cohort (ignore `offset`)

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
- `pagination` - Pagination metadata:
  - `total` - Total number of users in cohort
  - `limit` - Requested limit (or -1 if all users requested)
  - `offset` - Requested offset

#### Scenario: Fetch VIP cohort details with pagination
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=50&offset=0&sort=churn`
- **THEN** API queries database for VIP cohort users
- **AND** API filters users where `(LIFETIME_VALUE > 5000 OR AFFINITY_CARD = 1)`
- **AND** API orders users by churn probability descending
- **AND** API returns first 50 users with summary statistics
- **AND** response includes HTTP 200 status code
- **AND** response includes pagination metadata with total count

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
