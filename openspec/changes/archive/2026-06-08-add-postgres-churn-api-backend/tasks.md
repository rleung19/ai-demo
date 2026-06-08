# Tasks: Postgres-Backed Churn API

## 0. Prerequisites

- [x] 0.1 Confirm on branch `feature/postgres-backend`
- [x] 0.2 Confirm data migration complete (`validate_parity.py` passes — see `parity_20260607T054124Z.json`)
- [x] 0.3 Postgres tunnel + `DATABASE_URL` / `PG*` in `.env`
- [x] 0.4 Add `DB_BACKEND=postgres` to `.env.example`

## 1. Database layer

- [x] 1.1 Add `pg` and `@types/pg` to `package.json`
- [x] 1.2 Create `server/lib/db/postgres.ts`:
  - [x] 1.2.1 Pool from `DATABASE_URL` or `PG*` vars
  - [x] 1.2.2 `executeQuery(sql, binds)` compatible with route usage
  - [x] 1.2.3 Normalize row keys to UPPERCASE (Oracle parity)
  - [x] 1.2.4 `initializePool`, `closePool`, `testConnection`
- [x] 1.3 Create `server/lib/db/index.ts` — export by `DB_BACKEND` (`oracle` default)
- [x] 1.4 Update `server/index.ts` — init/close active backend pool; log `DB_BACKEND`

## 2. Postgres SQL

- [x] 2.1 Create `server/lib/sql/churn-queries.ts` (dual Oracle/Postgres queries; was `churn-postgres.ts` in plan)
- [x] 2.2 Port summary queries (`churn_predictions`, `user_profiles`, `model_registry`)
- [x] 2.3 Port cohorts CTE (VIP via `affinity_card`, no `ADMIN` join)
- [x] 2.4 Port cohort-detail (filters, sort, `LIMIT`/`OFFSET`)
- [x] 2.5 Port metrics query
- [x] 2.6 Port chart-data distribution query
- [x] 2.7 Port risk-factors (`string_agg` replacing `LISTAGG`)

## 3. Express routes

- [x] 3.1 Switch imports from `../../lib/db/oracle` → `../../lib/db`
- [x] 3.2 Branch SQL: use Postgres queries when `DB_BACKEND=postgres` (via `churn-queries.ts` + `isPostgresBackend()`)
- [x] 3.3 Update `server/routes/health.ts` — report backend + DB status
- [x] 3.4 Smoke-test each endpoint with `curl` against Postgres (`scripts/test-both-backends.sh`, `validate_api_parity.py`)

## 4. Next.js churn API removal (follow-up: `remove-nextjs-churn-api-routes`)

- [x] 4.1 ~~Port Next.js routes~~ — **cancelled**; delete `app/api/kpi/churn/*` instead (done in `remove-nextjs-churn-api-routes`)
- [x] 4.2 See `openspec/changes/remove-nextjs-churn-api-routes/tasks.md` (implemented)

## 5. Dev ergonomics

- [x] 5.1 Add `npm run server:dev:postgres` — sets `DB_BACKEND=postgres`, optional tunnel check
- [x] 5.2 Update `docs/POSTGRES_MIGRATION.md` with API startup section
- [x] 5.3 Update `AGENTS.md` — Postgres API uses `DB_BACKEND=postgres`
- [x] 5.4 Express-only Next.js startup — `instrumentation.ts` removed; no Next.js Oracle pool (`remove-nextjs-churn-api-routes`)

## 6. Validation

- [x] 6.1 Add `scripts/migration/validate_api_parity.py` — hit Express endpoints vs baseline
- [x] 6.2 Manual UI test: dashboard KPIs, cohort modal, risk factors with Postgres backend
- [x] 6.3 Confirm `DB_BACKEND=oracle` still works on same codebase (`scripts/test-both-backends.sh` — both backends pass, `atRiskCount=1341`)

## Definition of Done

- Express churn API fully functional on Postgres with matching JSON contracts
- UI loads real data from Postgres via `:3001`
- Oracle backend remains selectable via `DB_BACKEND=oracle`
- Validation script or documented manual test plan executed
