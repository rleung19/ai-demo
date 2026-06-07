# Tasks: Postgres-Backed Churn API

## 0. Prerequisites

- [ ] 0.1 Confirm on branch `feature/postgres-backend`
- [ ] 0.2 Confirm data migration complete (`validate_parity.py` passes)
- [ ] 0.3 Postgres tunnel + `DATABASE_URL` / `PG*` in `.env`
- [ ] 0.4 Add `DB_BACKEND=postgres` to `.env.example`

## 1. Database layer

- [ ] 1.1 Add `pg` and `@types/pg` to `package.json`
- [ ] 1.2 Create `server/lib/db/postgres.ts`:
  - [ ] 1.2.1 Pool from `DATABASE_URL` or `PG*` vars
  - [ ] 1.2.2 `executeQuery(sql, binds)` compatible with route usage
  - [ ] 1.2.3 Normalize row keys to UPPERCASE (Oracle parity)
  - [ ] 1.2.4 `initializePool`, `closePool`, `testConnection`
- [ ] 1.3 Create `server/lib/db/index.ts` — export by `DB_BACKEND` (`oracle` default)
- [ ] 1.4 Update `server/index.ts` — init/close active backend pool; log `DB_BACKEND`

## 2. Postgres SQL

- [ ] 2.1 Create `server/lib/sql/churn-postgres.ts` (or per-route query modules)
- [ ] 2.2 Port summary queries (`churn_predictions`, `user_profiles`, `model_registry`)
- [ ] 2.3 Port cohorts CTE (VIP via `affinity_card`, no `ADMIN` join)
- [ ] 2.4 Port cohort-detail (filters, sort, `LIMIT`/`OFFSET`)
- [ ] 2.5 Port metrics query
- [ ] 2.6 Port chart-data distribution query
- [ ] 2.7 Port risk-factors (`string_agg` replacing `LISTAGG`)

## 3. Express routes

- [ ] 3.1 Switch imports from `../../lib/db/oracle` → `../../lib/db`
- [ ] 3.2 Branch SQL: use Postgres queries when `DB_BACKEND=postgres` (factory or conditional)
- [ ] 3.3 Update `server/routes/health.ts` — report backend + DB status
- [ ] 3.4 Smoke-test each endpoint with `curl` against Postgres

## 4. Next.js churn API removal (follow-up: `remove-nextjs-churn-api-routes`)

- [ ] 4.1 ~~Port Next.js routes~~ — **cancelled**; delete `app/api/kpi/churn/*` instead
- [ ] 4.2 See `openspec/changes/remove-nextjs-churn-api-routes/tasks.md`

## 5. Dev ergonomics

- [x] 5.1 Add `npm run server:dev:postgres` — sets `DB_BACKEND=postgres`, optional tunnel check
- [x] 5.2 Update `docs/POSTGRES_MIGRATION.md` with API startup section
- [x] 5.3 Update `AGENTS.md` — Postgres API uses `DB_BACKEND=postgres`
- [x] 5.4 Skip Next.js Oracle pool init in Express-only mode (`instrumentation.ts`, `churn-api-backend.ts`)

## 6. Validation

- [ ] 6.1 Add `scripts/migration/validate_api_parity.py` (or shell) — hit Express endpoints vs baseline
- [ ] 6.2 Manual UI test: dashboard KPIs, cohort modal, risk factors with Postgres backend
- [ ] 6.3 Confirm `DB_BACKEND=oracle` still works on same codebase (regression smoke)

## Definition of Done

- Express churn API fully functional on Postgres with matching JSON contracts
- UI loads real data from Postgres via `:3001`
- Oracle backend remains selectable via `DB_BACKEND=oracle`
- Validation script or documented manual test plan executed
