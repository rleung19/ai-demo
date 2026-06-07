# Tasks: ADB → PostgreSQL Data Migration

## 0. Prerequisites

- [x] 0.1 Confirm working on branch `feature/postgres-backend`
- [x] 0.2 Verify ADB connectivity (`node scripts/test-node-connection.js` as OML user)
- [ ] 0.3 Verify Postgres connectivity via SSH tunnel (`127.0.0.1:15432` → `10.0.1.239:5432`)
- [x] 0.4 Add Postgres vars to `.env.example` (`PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `DATABASE_URL`)
- [x] 0.5 Document tunnel command in runbook (`ssh -N -L 15432:10.0.1.239:5432 40b5c371.nip.io`)
- [x] 0.6 Add `scripts/dev/pg-tunnel.sh` (start tunnel if port 15432 not listening)
- [x] 0.7 Add `scripts/dev/pg-psql.sh` (tunnel check + psql via `DATABASE_URL` or keg-only path)

## 1. Inventory & Baseline (ADB)

- [x] 1.1 Record row counts for Tier 1 tables: `CHURN_PREDICTIONS`, `USER_PROFILES`, `MODEL_REGISTRY`, `ADMIN.USERS`
- [x] 1.2 Record row counts for Tier 2: `CHURN_DATASET_TRAINING`
- [x] 1.3 Export baseline aggregate queries (summary, cohorts, risk-factor top 5) from ADB — save as `scripts/migration/fixtures/adb_baseline.json`
- [x] 1.4 Confirm OML user can `SELECT` from `ADMIN.USERS` (or plan separate ADMIN export credential)
- [x] 1.5 Document any ADB-only columns/constraints not in `sql/create_churn_tables.sql`

## 2. Postgres DDL

- [x] 2.1 Create `sql/postgres/001_create_schema.sql` — single schema `ecomm` (one DB, one app user)
- [x] 2.2 Create `ecomm.user_profiles` from `OML.USER_PROFILES` plus `affinity_card` (from ADB `ADMIN.USERS`)
- [x] 2.3 Create `ecomm.churn_predictions` from `OML.CHURN_PREDICTIONS`
- [x] 2.4 Create `ecomm.model_registry` from `OML.MODEL_REGISTRY`
- [x] 2.5 Create `ecomm.churn_dataset_training` (Tier 2)
- [x] 2.6 Create Postgres views: `churn_training_data`, `churn_user_features`, `churn_training_features` (port `sql/create_feature_views.sql`)
- [x] 2.7 Add indexes (PKs, churn label, risk score, prediction date, model registry status)
- [ ] 2.8 Apply DDL on target Postgres via tunnel (`psql -f sql/postgres/001_create_schema.sql`)

## 3. Migration Scripts

- [x] 3.1 Add `psycopg2-binary` to `requirements.txt` (or document venv install)
- [x] 3.2 Create `scripts/migration/migrate_adb_to_postgres.py`:
  - [x] 3.2.1 Read ADB config from `.env` (oracledb + wallet)
  - [x] 3.2.2 Read Postgres config from `DATABASE_URL`
  - [x] 3.2.3 Pre-flight: tunnel port open, both DBs reachable
  - [x] 3.2.4 Migrate tables in order: `user_profiles` (join ADB `ADMIN.USERS` for `affinity_card`) → `churn_predictions` → `model_registry` → `churn_dataset_training`
  - [x] 3.2.5 Batch insert (e.g. 1000 rows) for large tables
  - [x] 3.2.6 `--truncate` flag for idempotent reload
  - [x] 3.2.7 `--tables` flag to migrate subset (Tier 1 only)
- [x] 3.3 Create `scripts/migration/validate_parity.py`:
  - [x] 3.3.1 Compare row counts ADB vs Postgres per table
  - [x] 3.3.2 Compare summary aggregates (at-risk count, avg risk, LTV at risk)
  - [x] 3.3.3 Compare cohort counts (VIP, Regular, New, Dormant)
  - [x] 3.3.4 Exit non-zero on mismatch; write report to `scripts/migration/reports/`
- [ ] 3.4 Optional: CSV export fallback `scripts/migration/export_adb_tables.py` for manual inspection

## 4. Validation & Sign-off

- [ ] 4.1 Run full migration on `feature/postgres-backend` against OCI Postgres
- [ ] 4.2 Run `validate_parity.py` — all checks pass
- [ ] 4.3 Manual spot-check: `\dt ecomm.*` and sample `SELECT` from each table
- [ ] 4.4 Manual spot-check: VIP cohort user count matches ADB
- [ ] 4.5 Re-run migration with `--truncate` to confirm idempotency

## 5. Documentation

- [x] 5.1 Create `docs/POSTGRES_MIGRATION.md` — prerequisites, tunnel, DDL, migrate, validate, troubleshooting
- [x] 5.2 Update `docs/DATASET_SOURCE_AND_PREP.md` with Postgres target note (or cross-link)
- [x] 5.3 Document table mapping ADB → Postgres in design.md / migration doc
- [x] 5.4 Note follow-up change needed: Postgres-backed API (`server-postgres/` or `pg` driver)

## 6. Agent / Dev Ergonomics (optional)

- [x] 6.1 Cursor rule or AGENTS.md note: Postgres tasks use `DATABASE_URL` + tunnel scripts
- [x] 6.2 `scripts/migration/test_pg_connection.py` — minimal connect + `SELECT 1`

## Definition of Done

- All Tier 1 tables migrated with matching row counts
- Tier 2 training table migrated (if ML on Postgres is in scope for this sprint)
- Validation script passes
- Runbook complete
- No changes to Oracle backend on `main` (migration scripts live on `feature/postgres-backend` only)
