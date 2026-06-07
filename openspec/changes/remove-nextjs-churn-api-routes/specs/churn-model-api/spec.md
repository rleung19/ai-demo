## MODIFIED Requirements

### Requirement: Churn REST API Server
The system SHALL expose all churn KPI REST endpoints exclusively through the **Express standalone API server** (`server/routes/churn/*`), not through Next.js App Router API routes.

The Express server SHALL:
- Serve `/api/kpi/churn/summary`, `/cohorts`, `/cohorts/:name`, `/metrics`, `/chart-data`, `/risk-factors`
- Connect to the database via `DB_BACKEND` (`oracle` | `postgres`)
- Be the only backend the Next.js UI calls for churn data

#### Scenario: UI fetches churn summary
- **WHEN** the dashboard loads churn KPIs
- **THEN** the browser requests `GET {NEXT_PUBLIC_API_URL}/api/kpi/churn/summary` (default `http://localhost:3001`)
- **AND** Express handles the request and returns JSON
- **AND** no Next.js route under `app/api/kpi/churn/` exists

#### Scenario: Next.js dev server startup
- **WHEN** developer runs `npm run dev`
- **THEN** Next.js does not initialize an Oracle connection pool for churn APIs
- **AND** no duplicate churn API routes are registered on port 3000

## REMOVED Requirements

### Requirement: Next.js Churn API Routes
**Reason**: Duplicate of Express backend; removed for single-path architecture.
**Migration**: All clients use Express base URL via `NEXT_PUBLIC_API_URL` (unset → `http://localhost:3001` in local dev).

### Requirement: Database Connection (Next.js)
**Reason**: Next.js no longer connects to Oracle/Postgres for churn KPI endpoints.
**Migration**: Database connection requirements apply to Express only (`server/lib/db/`).
