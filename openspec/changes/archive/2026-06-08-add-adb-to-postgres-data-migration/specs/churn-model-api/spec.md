## ADDED Requirements

### Requirement: PostgreSQL Churn Data Store
The project SHALL maintain a PostgreSQL database on OCI (private network) containing churn data migrated from Oracle ADB OML schema, suitable for a future Postgres-backed churn API.

The Postgres data store SHALL include:
- All churn tables in **one database**, under **one application schema** (`ecomm`), accessed by **one application user** (credentials in environment only)
- `user_profiles`, `churn_predictions`, and `model_registry` with data equivalent to ADB Tier 1 objects
- `affinity_card` on `user_profiles` for VIP cohort assignment (merged from ADB `ADMIN.USERS` at migration)
- Optional training data and views (Tier 2) for ML pipeline on Postgres

This requirement covers **data presence and parity** only; Express/Next.js backends MAY continue using Oracle until a separate change switches the database driver.

#### Scenario: Postgres data available for API development
- **WHEN** migration and validation complete on `feature/postgres-backend`
- **THEN** Postgres contains churn tables with row counts matching ADB
- **AND** aggregate queries for summary and cohorts produce equivalent results to ADB

#### Scenario: Oracle backend unchanged on main
- **WHEN** migration is performed on `feature/postgres-backend`
- **THEN** Oracle ADB on `main` remains the production workshop data source
- **AND** no breaking changes are required to existing Oracle API routes until explicitly migrated
