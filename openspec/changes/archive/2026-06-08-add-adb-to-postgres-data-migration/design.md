# Design: ADB → PostgreSQL Data Migration

## Context

- **Source**: Oracle ADB, schema **OML** (app churn data) + **ADMIN.USERS** (VIP `AFFINITY_CARD` join)
- **Target**: OCI PostgreSQL on private network `10.0.1.239:5432`
- **Access**: Developers reach Postgres via SSH tunnel through jump host `40b5c371.nip.io` → local `127.0.0.1:15432`
- **Backends today**: Express (`server/`) and Next.js API routes query ADB directly; UI uses Express on `:3001`
- **Branch strategy**: Migration work on `feature/postgres-backend`; `main` Oracle demo frozen

## Goals / Non-Goals

### Goals

- Migrate all tables required for **dashboard parity** and **ML pipeline parity**
- Preserve data types, constraints, and join keys (`USER_ID` / `ID`)
- Provide automated export/import/validate scripts
- Document Oracle → Postgres type mapping and view recreation

### Non-Goals

- Rewriting churn API routes to use `pg` (separate change)
- Migrating recommender model data (OCI HTTP only)
- Migrating full `ADMIN` schema (only what churn APIs need)
- One-click production cutover (workshop/dev migration first)

## Source Table Inventory

### Tier 1 — Required for running backends (API parity)

| ADB object | ~Rows | Used by |
|------------|-------|---------|
| `OML.CHURN_PREDICTIONS` | 4,142 | summary, cohorts, cohort-detail, chart-data, risk-factors |
| `OML.USER_PROFILES` | 4,142 | summary (LTV), cohorts, cohort-detail, risk-factors |
| `OML.MODEL_REGISTRY` | small | summary, metrics |
| `ADMIN.USERS` | 4,142+ | cohorts, cohort-detail, risk-factors (`ID`, `AFFINITY_CARD`) |

### Tier 2 — Required for ML train/score on Postgres

| ADB object | ~Rows | Used by |
|------------|-------|---------|
| `OML.CHURN_DATASET_TRAINING` | 45,858 | `train_churn_model_local.py`, ingest scripts |
| `OML.CHURN_TRAINING_DATA` | view | training query |
| `OML.CHURN_USER_FEATURES` | view | scoring query |
| `OML.CHURN_TRAINING_FEATURES` | view | optional training features |

### Tier 3 — Defer

| ADB object | Notes |
|------------|-------|
| `OML.CHURN_PREDICTIONS_HISTORY` | Not queried by current API; chart `cohort-trend` is placeholder |
| `ADMIN.ORDERS_PROFILE_V` | Data-prep only; not runtime API |

## Target Postgres Layout

### Decision: single database, single user, single schema

Unlike ADB (objects split across **OML** and **ADMIN** schemas), Postgres will use:

| Layer | ADB (source) | Postgres (target) |
|-------|--------------|-------------------|
| Database | One ADB instance | **One** Postgres database (name/credentials in `.env` only — not in spec) |
| Login | `OML` user (+ read on `ADMIN.USERS`) | **One** application login user with full access to all migrated objects |
| Namespace | `OML.*`, `ADMIN.USERS` | **One** application schema (recommended: `ecomm`) — do **not** recreate `oml` / `admin` schema boundaries |

All migrated tables, views, and indexes live under that single schema and are owned by the same Postgres user used for migration and (later) the API.

### Table mapping (consolidated)

```
ecomm.user_profiles          ← OML.USER_PROFILES + AFFINITY_CARD from ADMIN.USERS
ecomm.churn_predictions      ← OML.CHURN_PREDICTIONS
ecomm.model_registry         ← OML.MODEL_REGISTRY
ecomm.churn_dataset_training ← OML.CHURN_DATASET_TRAINING
ecomm.churn_training_data    ← view (from OML.CHURN_TRAINING_DATA)
ecomm.churn_user_features    ← view (from OML.CHURN_USER_FEATURES)
ecomm.churn_training_features← view (from OML.CHURN_TRAINING_FEATURES)
```

### Decision: denormalize `ADMIN.USERS` at migration time

ADB cohort logic joins `OML.USER_PROFILES` to `ADMIN.USERS` for VIP (`AFFINITY_CARD`). On Postgres:

- Add **`affinity_card`** column to `ecomm.user_profiles`
- ETL joins ADB `ADMIN.USERS` on export and writes the value into `user_profiles` — no separate `users` table and no `admin` schema
- Future Postgres API routes query one schema only (`ecomm.user_profiles.affinity_card`)

This keeps one database, one user, and one schema while preserving VIP cohort parity with ADB.

## Oracle → PostgreSQL Type Mapping

| Oracle (ADB) | PostgreSQL |
|--------------|------------|
| `VARCHAR2(n)` | `VARCHAR(n)` or `TEXT` |
| `NUMBER(p,s)` | `NUMERIC(p,s)` or `DOUBLE PRECISION` for features |
| `NUMBER(1)` (0/1 flags) | `SMALLINT` or `BOOLEAN` |
| `TIMESTAMP` | `TIMESTAMP` or `TIMESTAMPTZ` |
| `CLOB` | `TEXT` |
| `DATE` | `DATE` |

Views (`CHURN_TRAINING_DATA`, etc.): recreate as Postgres `VIEW` with equivalent `CASE` expressions from `sql/create_feature_views.sql`.

## Migration Approach

### Recommended: Python ETL script (oracledb → psycopg2)

1. **Connect to ADB** using existing `.env` (`ADB_*`, wallet)
2. **Connect to Postgres** via `DATABASE_URL` (`127.0.0.1:15432` through tunnel)
3. **Export** each table with `SELECT *` (batched for large tables)
4. **Load** with `COPY` or bulk `INSERT` into Postgres
5. **Validate** row counts and spot-check aggregates

**Why Python**: Project already has `oracledb` in ML scripts; add `psycopg2-binary` for Postgres. Single tool, easy to run in CI/agent mode.

### Alternatives considered

| Approach | Pros | Cons |
|----------|------|------|
| **ora2pg** | Mature DDL conversion | Extra tool; overkill for 4–5 tables |
| **CSV intermediate** | Simple, inspectable | Manual steps; type coercion errors |
| **Oracle GoldenGate / OCI DMS** | Enterprise replication | Overkill for workshop demo |
| **pgloader from Oracle** | One command | Needs direct network Oracle→PG; we have tunnel |

## Connectivity

### Developer / agent workflow

```bash
# Terminal 1: tunnel
ssh -N -L 15432:10.0.1.239:5432 40b5c371.nip.io

# Terminal 2: migration
export DATABASE_URL="postgresql://user:pass@127.0.0.1:15432/dbname?sslmode=require"
python scripts/migration/migrate_adb_to_postgres.py --validate
```

### Environment variables

```env
# Existing (source)
ADB_WALLET_PATH=...
ADB_CONNECTION_STRING=...
ADB_USERNAME=OML
ADB_PASSWORD=...

# New (target)
PGHOST=127.0.0.1
PGPORT=15432
PGUSER=...
PGPASSWORD=...
PGDATABASE=...
DATABASE_URL=postgresql://...
```

## Validation Strategy

### Row-count parity

| Table | ADB count | PG count | Match |
|-------|-----------|----------|-------|

### Aggregate parity (API-equivalent SQL)

Run same logical queries on both DBs:

1. **Summary**: total customers, at-risk count, avg risk, LTV at risk
2. **Cohorts**: counts per VIP/Regular/New/Dormant
3. **Risk factors**: top 5 factors by impact score (after Postgres SQL port)
4. **Model registry**: latest ACTIVE model row

Tolerance: exact match on counts; aggregates within rounding (0.01 for percentages).

## Idempotency & Rollback

- **DDL**: `sql/postgres/001_create_schema.sql` — `CREATE TABLE IF NOT EXISTS` or versioned migrations
- **Load**: `TRUNCATE ... CASCADE` + reload, or `UPSERT` on primary keys (`user_id`)
- **Rollback**: `DROP SCHEMA ecomm CASCADE` and re-run; ADB remains source of truth on `main`

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Tunnel not running during migration | Pre-flight check script; document in runbook |
| `ADMIN.USERS` access from OML user on ADB | Export ADMIN via separate connection or DBA grant; script handles both |
| Boolean vs NUMBER(1) churn labels | Explicit cast on load; document in mapping |
| View logic differs in Postgres | Port views from `create_feature_views.sql`; validate row counts match |
| Secrets in `.env` | Never commit; `.env.example` only placeholders |

## Migration Plan (Phases)

### Phase 0 — Prerequisites

- SSH tunnel verified (`nc -zv 127.0.0.1 15432`)
- `psql` or `psycopg2` connectivity test
- ADB connection test (`scripts/test-node-connection.js`)

### Phase 1 — DDL on Postgres

- Create schema + tables (Tier 1)
- Create indexes matching ADB performance indexes
- Add Tier 2 training table + views

### Phase 2 — Data export/import

- Migrate Tier 1: `user_profiles` (with `affinity_card` from ADB `ADMIN.USERS`) → `churn_predictions`; `model_registry` independent
- Migrate Tier 2 `churn_dataset_training`
- Refresh views (no data copy for views)

### Phase 3 — Validation

- Row counts
- Aggregate queries
- Optional: export validation report JSON

### Phase 4 — Documentation & handoff

- `docs/POSTGRES_MIGRATION.md` runbook
- `.env.example` Postgres section
- Helper scripts: `scripts/dev/pg-tunnel.sh`, `scripts/migration/validate_parity.py`

## Open Questions

- SSL mode required on private OCI Postgres (`sslmode=require` vs `disable`)?

## Resolved

- **Postgres database / login user**: Provided via `.env` (`DATABASE_URL`, `PG*`) — intentionally omitted from spec
- **Schema layout**: Single application schema `ecomm`; no `oml` / `admin` schema split
- **ADMIN.USERS**: Denormalize `affinity_card` into `ecomm.user_profiles` at migration time
