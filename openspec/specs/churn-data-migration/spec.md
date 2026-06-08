# churn-data-migration Specification

## Purpose
TBD - created by archiving change add-adb-to-postgres-data-migration. Update Purpose after archive.
## Requirements
### Requirement: ADB Source Inventory
The migration process SHALL document all Oracle ADB objects copied to PostgreSQL, grouped by tier:

- **Tier 1 (backend parity)**: `OML.CHURN_PREDICTIONS`, `OML.USER_PROFILES`, `OML.MODEL_REGISTRY`, `ADMIN.USERS` (minimum columns `ID`, `AFFINITY_CARD`)
- **Tier 2 (ML pipeline parity)**: `OML.CHURN_DATASET_TRAINING`, views `CHURN_TRAINING_DATA`, `CHURN_USER_FEATURES`, `CHURN_TRAINING_FEATURES`
- **Tier 3 (deferred)**: `OML.CHURN_PREDICTIONS_HISTORY` and other objects not queried by current backends

#### Scenario: Inventory documented before migration
- **WHEN** migration work begins on `feature/postgres-backend`
- **THEN** design document lists every source table, target Postgres table, and tier
- **AND** row-count baselines are captured from ADB before first load

### Requirement: PostgreSQL Target Layout
The system SHALL create PostgreSQL tables equivalent to ADB Tier 1 and Tier 2 objects with preserved primary keys and join columns (`USER_ID` / `ID`).

Unlike ADB (objects in **OML** and **ADMIN** schemas), Postgres SHALL use:
- **One database** and **one application login user** (connection details in environment only, not in spec)
- **One application schema** (`ecomm`) for all migrated tables and views — no separate `oml` / `admin` schemas mirroring Oracle

The Postgres layout SHALL:
- Store churn predictions, user profiles, model registry, and training data under that single schema
- Support VIP cohort logic via `affinity_card` on `user_profiles` (denormalized from ADB `ADMIN.USERS` at migration time)
- Recreate feature views with equivalent column names and encodings as ADB views

#### Scenario: DDL applied on empty Postgres
- **WHEN** administrator runs Postgres DDL script via tunnel
- **THEN** all Tier 1 tables exist with correct columns and constraints
- **AND** Tier 2 training table and views exist
- **AND** indexes are created for query patterns used by churn APIs

### Requirement: Data Export from ADB
The migration tooling SHALL read data from Oracle ADB using the existing OML connection configuration (wallet + `ADB_*` environment variables).

Export SHALL:
- Connect as OML user for OML schema tables
- Export ADMIN.USERS using OML grants or a documented secondary connection
- Support batched reads for tables exceeding 10,000 rows

#### Scenario: Export churn predictions from ADB
- **WHEN** migration script runs with ADB credentials configured
- **THEN** all rows from `OML.CHURN_PREDICTIONS` are read successfully
- **AND** row count matches ADB `COUNT(*)`

### Requirement: Data Load into PostgreSQL
The migration tooling SHALL insert exported rows into PostgreSQL via `DATABASE_URL` (typically `127.0.0.1:15432` through SSH tunnel to `10.0.1.239`).

Load SHALL:
- Connect with the single application Postgres user to the single target database
- Insert tables in dependency order (`user_profiles` with merged `affinity_card` → `churn_predictions` → `model_registry` → training data)
- Support truncate-and-reload for idempotent re-runs
- Map Oracle types to PostgreSQL types without data loss for defined columns

#### Scenario: Idempotent reload
- **WHEN** migration script runs twice with `--truncate` flag
- **THEN** Postgres row counts match ADB after each run
- **AND** no duplicate primary key violations occur

### Requirement: Migration Validation
The system SHALL provide an automated validation step comparing ADB and PostgreSQL after migration.

Validation SHALL compare:
- Row counts per migrated table
- Summary aggregates: total customers, at-risk count, average risk score, total LTV at risk
- Cohort customer counts for VIP, Regular, New, Dormant

Validation SHALL exit with non-zero status when parity checks fail.

#### Scenario: Successful validation
- **WHEN** migration completes and validation script runs
- **THEN** all Tier 1 table row counts match between ADB and Postgres
- **AND** summary and cohort aggregates match within documented tolerance
- **AND** validation report is written for audit

#### Scenario: Failed validation
- **WHEN** Postgres row count differs from ADB for a Tier 1 table
- **THEN** validation script exits with error
- **AND** report identifies table name and expected vs actual counts

### Requirement: Migration Runbook
The project SHALL document the end-to-end migration procedure including SSH tunnel setup, environment variables, DDL application, migration script execution, and validation.

#### Scenario: Developer runs migration from runbook
- **WHEN** developer follows `docs/POSTGRES_MIGRATION.md`
- **THEN** they can establish tunnel, apply DDL, migrate data, and validate without undocumented steps

