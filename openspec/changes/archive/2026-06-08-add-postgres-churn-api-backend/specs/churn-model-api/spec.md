## MODIFIED Requirements

### Requirement: Database Connection
The system SHALL connect to the churn data store using a configurable database backend selected by environment variable `DB_BACKEND`.

Supported backends:

- **`oracle`** (default): Oracle Autonomous Database via wallet-based `oracledb` connection to `OML` schema (and `ADMIN.USERS` where required)
- **`postgres`**: OCI PostgreSQL via `pg` connection pool using `DATABASE_URL` or `PG*` environment variables, querying schema **`ecomm`**

The connection layer SHALL:
- Expose a unified `executeQuery` interface for churn route handlers
- Initialize a connection pool at API server startup for the active backend
- Close the pool gracefully on shutdown
- Return HTTP 503 when the active backend is unreachable

#### Scenario: Express starts with Postgres backend
- **WHEN** `DB_BACKEND=postgres` and valid `DATABASE_URL` are set
- **AND** SSH tunnel to Postgres is available (if required)
- **THEN** Express initializes a `pg` pool to the target database
- **AND** health check reports `backend: postgres` and `connected: true`

#### Scenario: Express starts with Oracle backend (default)
- **WHEN** `DB_BACKEND` is unset or `oracle`
- **THEN** Express uses existing `oracledb` pool and wallet configuration
- **AND** churn routes query `OML.*` as today
- **AND** behavior on `main` is unchanged

#### Scenario: Database connection failure
- **WHEN** the active backend cannot be reached
- **THEN** API returns HTTP 503 on churn endpoints
- **AND** error is logged with backend type and connection details (no secrets)

### Requirement: Churn Summary Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/summary` that returns summary metrics for churn risk analysis.

The endpoint SHALL return:
- Total at-risk customers count
- Average risk score (percentage)
- Total LTV at risk (dollar amount)
- Model confidence score
- Last model update timestamp

The endpoint SHALL read pre-computed predictions from the active backend's predictions table (`OML.CHURN_PREDICTIONS` or `ecomm.churn_predictions`).

#### Scenario: Fetch churn summary from Postgres
- **WHEN** frontend requests `GET /api/kpi/churn/summary`
- **AND** `DB_BACKEND=postgres`
- **THEN** API aggregates from `ecomm.churn_predictions` and `ecomm.user_profiles`
- **AND** API returns JSON with the same field names as the Oracle backend
- **AND** response includes HTTP 200 status code

#### Scenario: Handle model not found
- **WHEN** no model exists in the active backend's model registry
- **THEN** API returns HTTP 503 with error message
- **AND** frontend falls back to static data

### Requirement: Cohort Breakdown Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/cohorts` that returns churn risk breakdown by customer segment.

The endpoint SHALL return:
- Risk scores per cohort (VIP, Regular, New, Dormant, At-Risk)
- Customer counts per cohort
- Average risk percentage per cohort
- LTV at risk per cohort

On Postgres, VIP assignment SHALL use `ecomm.user_profiles.affinity_card` and `lifetime_value` (no `ADMIN.USERS` join).

#### Scenario: Fetch cohort breakdown from Postgres
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts`
- **AND** `DB_BACKEND=postgres`
- **THEN** API groups customers using the same cohort rules as Oracle
- **AND** VIP rule uses `affinity_card = 1 OR lifetime_value > 5000`
- **AND** aggregate metrics match migration parity fixtures within documented tolerance

### Requirement: Cohort Detail Endpoint
The system SHALL provide a REST API endpoint `GET /api/kpi/churn/cohorts/:name` that returns detailed information for a specific cohort, including cohort-level summary statistics and a paginated list of users in that cohort.

On Postgres, the endpoint SHALL use `LIMIT`/`OFFSET` pagination and `ecomm.*` tables with equivalent filters and sort orders as the Oracle implementation.

#### Scenario: Fetch VIP cohort details from Postgres
- **WHEN** frontend requests `GET /api/kpi/churn/cohorts/VIP?limit=3&offset=0&sort=churn`
- **AND** `DB_BACKEND=postgres`
- **THEN** API returns VIP users filtered by `lifetime_value > 5000 OR affinity_card = 1`
- **AND** response JSON matches Oracle contract (`cohort`, `definition`, `summary`, `users`, `pagination`)

## ADDED Requirements

### Requirement: Postgres Churn SQL Port
The Postgres backend SHALL implement SQL equivalent to Oracle churn queries against schema `ecomm`, including:

- Summary and LTV aggregates from `churn_predictions` joined to `user_profiles`
- Cohort assignment CTE with denormalized `affinity_card`
- Model metadata from `model_registry`
- Risk factor queries with segment aggregation (Postgres `string_agg` equivalent to Oracle `LISTAGG`)
- Chart distribution from current predictions

Column semantics and API JSON mapping SHALL remain identical to the Oracle backend.

#### Scenario: Risk factors on Postgres
- **WHEN** frontend requests `GET /api/kpi/churn/risk-factors`
- **AND** `DB_BACKEND=postgres`
- **THEN** API returns top risk factors with impact scores and affected customer counts
- **AND** factor ordering and thresholds match the Oracle implementation

#### Scenario: API parity validation
- **WHEN** validation script runs against Express with `DB_BACKEND=postgres`
- **THEN** summary totals and cohort customer counts match `scripts/migration/fixtures/adb_baseline.json`

### Requirement: Dual-Backend Configuration
The project SHALL support running Oracle and Postgres backends from the same codebase without branching logic in route handlers.

Configuration SHALL:
- Use `DB_BACKEND` environment variable (`oracle` | `postgres`)
- Keep Oracle variables (`ADB_*`) and Postgres variables (`DATABASE_URL`, `PG*`) in `.env`
- Default to `oracle` when `DB_BACKEND` is unset

#### Scenario: Switch backend locally
- **WHEN** developer changes `DB_BACKEND` from `oracle` to `postgres` and restarts Express
- **THEN** the same route paths serve data from Postgres without code changes
- **AND** recommender endpoints continue to use OCI HTTP regardless of `DB_BACKEND`

### Requirement: Express-Only Next.js Startup
When the UI uses the Express churn API (always, after `remove-nextjs-churn-api-routes`), Next.js SHALL NOT initialize an Oracle connection pool at startup.

#### Scenario: Express-only dev (default)
- **WHEN** developer runs `npm run dev`
- **AND** the UI fetches churn data from Express on port 3001
- **THEN** Next.js instrumentation does not initialize an Oracle pool
- **AND** startup logs indicate Express-only mode

## MODIFIED Requirements

### Requirement: Model Loading and Scoring
The system SHALL serve churn predictions from pre-materialized rows in the active backend's predictions table.

For API read paths, the system SHALL NOT require live ML scoring in Node.js; predictions are loaded during the ML pipeline into `OML.CHURN_PREDICTIONS` or `ecomm.churn_predictions`.

#### Scenario: Score customers for API request
- **WHEN** API endpoint requires customer scores
- **THEN** API reads existing prediction rows from the active backend
- **AND** API does not invoke OML4Py or local pickle models during the HTTP request
