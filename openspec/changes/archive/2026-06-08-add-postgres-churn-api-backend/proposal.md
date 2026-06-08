# Change: Postgres-Backed Churn API Server

## Why

Data migration to OCI PostgreSQL (`ecomm` schema) is complete with parity validation on `feature/postgres-backend`. The dashboard UI still calls the Express API on `:3001`, which reads Oracle ADB via `oracledb`. To run the workshop demo entirely on Postgres, the churn API layer must query `ecomm.*` instead of `OML.*` / `ADMIN.USERS`.

## What Changes

- **Postgres database layer** for Express: `pg` connection pool using `DATABASE_URL` / `PG*` from `.env`
- **SQL port** for all churn routes: `OML.*` → `ecomm.*`, VIP logic via `user_profiles.affinity_card` (no `ADMIN` join)
- **Backend selection**: `DB_BACKEND=postgres|oracle` env var (default `oracle` on `main`, `postgres` on `feature/postgres-backend`)
- **Shared query module**: Postgres SQL versions of cohort, summary, risk-factor, and detail queries
- **Express routes** updated to use database abstraction (same JSON contracts — no UI changes)
- **Express-only churn API** — Next.js duplicate routes removed in follow-up change `remove-nextjs-churn-api-routes` (delete, not deprecate)
- **Health endpoint** reports active backend and connectivity
- **Documentation**: dev startup for Postgres backend, SQL mapping notes
- **Next.js instrumentation**: no Oracle pool (Express-only; see `remove-nextjs-churn-api-routes`)

**Out of scope for this change** (see `remove-nextjs-churn-api-routes`):

- Deleting `app/api/kpi/churn/*` and `app/lib/db/oracle.ts`

**Out of scope:**

- Recommender routes (`/api/recommender/*`) — remain OCI HTTP
- Live ML scoring in API (predictions are pre-loaded in `ecomm.churn_predictions`)
- Removing Oracle code from `main` (dual-backend support until explicitly deprecated)
- Migrating Python ML scripts to Postgres (separate change)

## Impact

- **Affected specs**: `churn-model-api` — MODIFIED database connection; ADDED Postgres backend requirements
- **Affected code** (expected):
  - `server/lib/db/postgres.ts` — new
  - `server/lib/db/index.ts` — factory by `DB_BACKEND`
  - `server/lib/sql/` — Postgres query strings (or inline in routes)
  - `server/routes/churn/*.ts` — use db abstraction
  - `server/index.ts` — pool init for active backend
  - `package.json` — add `pg`, `@types/pg`
  - `docs/POSTGRES_MIGRATION.md` — link to API section
- **Follow-up change**: `remove-nextjs-churn-api-routes` — delete Next.js churn API duplicates
- **Branch**: `feature/postgres-backend`
- **Depends on**: `add-adb-to-postgres-data-migration` (data in `ecommdb` / schema `ecomm`)

## Success Criteria

- With `DB_BACKEND=postgres` and tunnel up, all churn endpoints return same JSON shape as Oracle backend
- Summary, cohorts, cohort-detail, metrics, chart-data, risk-factors match parity fixtures within documented tolerance
- `DB_BACKEND=oracle` on `main` continues to work unchanged
- UI works with `NEXT_PUBLIC_API_URL=http://localhost:3001` against Postgres backend
