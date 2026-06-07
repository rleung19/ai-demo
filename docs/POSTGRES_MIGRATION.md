# PostgreSQL Migration Runbook (ADB → OCI Postgres)

Migrate churn dashboard data from Oracle ADB (`OML` + `ADMIN.USERS`) to OCI PostgreSQL under schema **`ecomm`**.

**Branch:** `feature/postgres-backend`  
**Oracle on `main` is unchanged** — this is data migration only; API switch to `pg` is a follow-up change.

## Architecture

| ADB (source) | Postgres (target) |
|--------------|-------------------|
| Database: ADB instance | One database (`PGDATABASE` / `DATABASE_URL`) |
| Schemas: `OML`, `ADMIN` | One schema: **`ecomm`** |
| Login: `OML` user | One app user (`PGUSER`) |
| VIP: join `ADMIN.USERS` | `affinity_card` denormalized on `ecomm.user_profiles` |

### Table mapping

| ADB | Postgres |
|-----|----------|
| `OML.USER_PROFILES` + `ADMIN.USERS.AFFINITY_CARD` | `ecomm.user_profiles` |
| `OML.CHURN_PREDICTIONS` | `ecomm.churn_predictions` |
| `OML.MODEL_REGISTRY` | `ecomm.model_registry` |
| `OML.CHURN_DATASET_TRAINING` | `ecomm.churn_dataset_training` |
| Feature views | `ecomm.churn_training_data`, `churn_user_features`, `churn_training_features` |

## Prerequisites

1. **ADB** — wallet and `ADB_*` vars in `.env` (same as Oracle backend)
2. **Postgres** — add `DATABASE_URL` or `PGHOST` / `PGPORT` / `PGUSER` / `PGPASSWORD` / `PGDATABASE` to `.env` (see `.env.example`)
3. **Python** — `pip install -r requirements.txt` (`oracledb`, `psycopg2-binary`, `python-dotenv`)
4. **`psql`** (optional) — Homebrew `libpq` keg: `/opt/homebrew/opt/libpq/bin/psql`

## 1. SSH tunnel

OCI Postgres is on private network `10.0.1.239:5432`. From your Mac:

```bash
# Helper (background tunnel if port 15432 is free)
chmod +x scripts/dev/pg-tunnel.sh scripts/dev/pg-psql.sh
./scripts/dev/pg-tunnel.sh

# Manual (foreground)
ssh -N -L 15432:10.0.1.239:5432 40b5c371.nip.io
```

Verify:

```bash
nc -zv 127.0.0.1 15432
python scripts/migration/test_pg_connection.py
```

## 2. Apply DDL

```bash
./scripts/dev/pg-psql.sh -f sql/postgres/001_create_schema.sql
./scripts/dev/pg-psql.sh -f sql/postgres/002_create_views.sql
```

Or via migration script:

```bash
python scripts/migration/migrate_adb_to_postgres.py --apply-ddl --skip-preflight
# (use --skip-preflight only if you already verified connections)
```

## 3. Capture ADB baseline (optional but recommended)

```bash
python scripts/migration/capture_adb_baseline.py
# → scripts/migration/fixtures/adb_baseline.json
```

## 4. Migrate data

```bash
python scripts/migration/migrate_adb_to_postgres.py --apply-ddl --truncate
```

Options:

| Flag | Purpose |
|------|---------|
| `--truncate` | Clear target tables before reload (idempotent re-run) |
| `--apply-ddl` | Run `sql/postgres/*.sql` first |
| `--tables tier1` | Skip training table (`user_profiles`, `churn_predictions`, `model_registry` only) |
| `--tables all` | Include `churn_dataset_training` (default) |

## 5. Validate parity

```bash
python scripts/migration/validate_parity.py
```

Checks:

- Row counts: ADB `OML.*` vs `ecomm.*`
- Summary aggregates (customers, at-risk, avg risk, LTV at risk)
- Cohort counts (VIP, Regular, New, Dormant)

Reports written to `scripts/migration/reports/parity_*.json`. Exit code `1` on mismatch.

## 6. Spot-check in psql

```bash
./scripts/dev/pg-psql.sh -c "\dt ecomm.*"
./scripts/dev/pg-psql.sh -c "SELECT COUNT(*) FROM ecomm.user_profiles"
./scripts/dev/pg-psql.sh -c "SELECT COUNT(*) FROM ecomm.churn_predictions"
./scripts/dev/pg-psql.sh -c "SELECT affinity_card, COUNT(*) FROM ecomm.user_profiles GROUP BY 1"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Postgres not reachable at 127.0.0.1:15432` | Run `./scripts/dev/pg-tunnel.sh` |
| `Missing Postgres config` | Set `DATABASE_URL` in `.env` |
| `psql: command not found` | Install `libpq` or set `PSQL_PATH` |
| `ADMIN.USERS` export fails | Ensure OML user has `SELECT` on `ADMIN.USERS` |
| SSL errors | Try `?sslmode=disable` on private network if server allows |
| Parity cohort mismatch | Confirm `affinity_card` migrated on `user_profiles` |

## Follow-up (out of scope)

- ~~Switch Express routes from `oracledb` to `pg`~~ — **done** via `DB_BACKEND=postgres`
- ~~Remove Next.js duplicate API routes~~ — **done** (Express-only; see `remove-nextjs-churn-api-routes`)
- Point production deploy at Postgres-backed Express

## 7. Run API on Postgres

```bash
# Terminal 1: tunnel
./scripts/dev/pg-tunnel.sh

# Terminal 2: Express API (port 3001)
npm run server:dev:postgres
# or: DB_BACKEND=postgres npm run server:dev
```

Set in `.env`:

```env
DB_BACKEND=postgres
PGHOST=127.0.0.1
PGPORT=15432
PGUSER=...
PGPASSWORD="..."
PGDATABASE=ecommdb
```

The Node `pg` client uses TLS by default for OCI Postgres (see `PGSSLMODE=disable` in `.env.example` only if your server allows it).

Verify:

```bash
curl http://localhost:3001/api/health
curl http://localhost:3001/api/kpi/churn/summary
python scripts/migration/validate_api_parity.py
```

UI: start Next.js (`npm run dev`) with `NEXT_PUBLIC_API_URL=http://localhost:3001`.

## Related follow-up

- [DATASET_SOURCE_AND_PREP.md](./DATASET_SOURCE_AND_PREP.md) — how ADB tables were populated
- [openspec/changes/add-adb-to-postgres-data-migration/design.md](../openspec/changes/add-adb-to-postgres-data-migration/design.md) — full design
