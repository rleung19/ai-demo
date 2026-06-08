# Change: Migrate Churn Data from ADB to PostgreSQL

## Why

The project maintains an Oracle ADB workshop track on `main` while developing a PostgreSQL variant on `feature/postgres-backend`. The churn dashboard and ML pipeline today read from **OML** schema tables (and a slice of **ADMIN.USERS**) in ADB. Before building a Postgres-backed API, we need the same data available in the OCI PostgreSQL instance (`10.0.1.239`) with validated row counts, referential integrity, and parity checks against ADB.

## What Changes

- **New migration capability**: Documented, repeatable process to copy churn-related data from ADB → OCI PostgreSQL
- **Postgres DDL**: PostgreSQL schemas/tables/views equivalent to current ADB objects used by backends and ML scripts
- **Migration scripts**: Export from ADB (OML + ADMIN slice), load into Postgres, validate parity
- **Connectivity tooling**: SSH tunnel via jump host (`40b5c371.nip.io`), env vars (`DATABASE_URL`), helper scripts for agent/local dev
- **Documentation**: Table mapping, type conversion notes, rollback and re-run strategy

**Out of scope for this change** (follow-up proposals):

- Switching Express/Next.js backends from `oracledb` to `pg` (separate change)
- Replacing OCI recommender HTTP calls
- Decommissioning ADB or removing Oracle code from `main`

## Impact

- **New capability**: `churn-data-migration` — ADB-to-Postgres data migration requirements
- **Affected specs**: `churn-model-api` — ADDED Postgres data store requirement (data layer only; API still Oracle until follow-up)
- **Affected code** (expected during implementation):
  - `sql/postgres/` — new DDL
  - `scripts/migration/` — export, import, validate scripts
  - `.env.example` — Postgres connection vars
  - `docs/POSTGRES_MIGRATION.md` — runbook
- **Branch**: `feature/postgres-backend` (Oracle `main` unchanged)
- **Source ADB objects**:
  - **OML**: `USER_PROFILES`, `CHURN_PREDICTIONS`, `MODEL_REGISTRY`, `CHURN_DATASET_TRAINING` (+ feature views)
  - **ADMIN**: `USERS` (`ID`, `AFFINITY_CARD` minimum; full table optional for future-proofing)
- **Target**: OCI PostgreSQL private IP `10.0.1.239:5432` via SSH tunnel from dev machine

## Success Criteria

- Postgres contains migrated tables with row counts matching ADB (±0 for core tables)
- Sample API-equivalent queries (summary, cohorts, risk factors) return same aggregates on Postgres as ADB
- Migration is idempotent (safe to re-run with truncate/reload or upsert strategy)
- Runbook documents tunnel, credentials, and validation steps
