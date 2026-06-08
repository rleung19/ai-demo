# Design: Postgres-Backed Churn API

## Context

- **UI**: Next.js dashboard → Express `:3001` via `NEXT_PUBLIC_API_URL`
- **Oracle path (today)**: `server/lib/db/oracle.ts` → `OML.*` + `JOIN ADMIN.USERS`
- **Postgres path (data ready)**: `ecommdb`, schema `ecomm`, `affinity_card` on `user_profiles`
- **Branch**: `feature/postgres-backend`; `main` keeps Oracle default

## Goals / Non-Goals

### Goals

- Same REST paths and JSON response contracts as today
- Select backend via `DB_BACKEND` without code forks in route handlers
- Port all 6 churn Express routes + health DB check
- Validate against `scripts/migration/fixtures/adb_baseline.json` aggregates

### Non-Goals

- Oracle removal from repo
- Next.js API as primary server (Express remains primary; Next routes optional parity)
- Recommender DB or model retraining

## Architecture

```
┌─────────────┐     HTTP      ┌──────────────────┐
│  Next.js UI │ ────────────► │ Express :3001    │
│  (port 3000)│               │ server/routes/   │
└─────────────┘               └────────┬─────────┘
                                       │
                              server/lib/db/index.ts
                              (DB_BACKEND selector)
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
                 server/lib/db/oracle.ts      server/lib/db/postgres.ts
                         │                           │
                         ▼                           ▼
                    Oracle ADB                   OCI Postgres
                    OML + ADMIN                  ecomm schema
```

## Decision: DB factory + shared `executeQuery` interface

Export from `server/lib/db/index.ts`:

```typescript
export { executeQuery, initializePool, closePool, testConnection } from './...';
```

- `DB_BACKEND=oracle` (default) → existing `oracle.ts`
- `DB_BACKEND=postgres` → new `postgres.ts` using `pg.Pool`

Route files import from `../../lib/db` (not `oracle` directly).

**Row shape**: Postgres driver returns lowercase keys by default. Route handlers today expect `UPPER_CASE` Oracle keys. Options:

| Option | Pros | Cons |
|--------|------|------|
| **A. Normalize to uppercase in postgres.ts** | Minimal route changes | Adapter logic |
| **B. Update routes to lowercase keys** | Idiomatic PG | Large diff, two backends differ |

**Recommendation**: **Option A** — map `result.rows` keys to uppercase in `postgres.ts` `executeQuery` so route mapping code stays identical.

## SQL port mapping

### Schema / table names

| Oracle | Postgres |
|--------|----------|
| `OML.CHURN_PREDICTIONS` | `ecomm.churn_predictions` |
| `OML.USER_PROFILES` | `ecomm.user_profiles` |
| `OML.MODEL_REGISTRY` | `ecomm.model_registry` |
| `ADMIN.USERS au` + `au.AFFINITY_CARD` | `up.affinity_card` (no join) |

### Syntax conversions

| Oracle | Postgres |
|--------|----------|
| `FETCH FIRST 1 ROW ONLY` | `LIMIT 1` |
| `OFFSET :n ROWS FETCH NEXT :m ROWS ONLY` | `LIMIT :m OFFSET :n` |
| `LISTAGG(x, ', ') WITHIN GROUP (ORDER BY y DESC)` | `(SELECT string_agg(cohort, ', ' ORDER BY cnt DESC) FROM (SELECT ... LIMIT 2) s)` |
| `SELECT 1 FROM DUAL` | `SELECT 1` |
| Bind `:name` | `$1` / named via `pg` config — use positional `$1,$2` in PG queries with ordered binds array |

### VIP cohort rule (unchanged logic)

```sql
WHEN up.lifetime_value > 5000 OR up.affinity_card = 1 THEN 'VIP'
```

### Query organization

**Recommendation**: `server/lib/sql/churn/` with paired files:

- `cohorts.oracle.sql` / `cohorts.postgres.sql` — or single TS module exporting `getCohortsQuery(backend)`

For maintainability, start with **`server/lib/sql/churn-postgres.ts`** exporting query string constants; Oracle SQL stays inline until a later refactor.

## Endpoints to port

| Route | File | Oracle-specific notes |
|-------|------|----------------------|
| `GET /summary` | `summary.ts` | 3 queries, `FETCH FIRST 1` on registry |
| `GET /cohorts` | `cohorts.ts` | Cohort CTE, remove ADMIN join |
| `GET /cohorts/:name` | `cohort-detail.ts` | Pagination `OFFSET/FETCH` |
| `GET /metrics` | `metrics.ts` | `MODEL_REGISTRY`, `FETCH FIRST 1` |
| `GET /chart-data` | `chart-data.ts` | Distribution from predictions (no history table) |
| `GET /risk-factors` | `risk-factors.ts` | 5 factors, `LISTAGG` → `string_agg` |

## Next.js churn API — removed (see `remove-nextjs-churn-api-routes`)

Next.js App Router routes under `app/api/kpi/churn/*` are **deleted**, not ported. The UI always calls Express.

| Option | Decision |
|--------|----------|
| Port Next routes to Postgres | **Rejected** — duplicate maintenance |
| Deprecate with 410/redirect | **Rejected** — dead code remains |
| **Delete** | **Accepted** — Express is the only churn API |

`NEXT_PUBLIC_API_URL` means Express API base URL only (local `:3001` or production domain). No empty-string “use Next.js routes” mode.

## Environment variables

```env
DB_BACKEND=postgres          # oracle | postgres

# Postgres (existing)
DATABASE_URL=postgresql://...
# or PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

# Oracle (unchanged when DB_BACKEND=oracle)
ADB_WALLET_PATH=...
```

## Caching & errors

- Keep existing in-memory cache keys/TTL in route files
- `handleDatabaseError` unchanged — 503 on connection failure
- Health route: add `database.backend` and `database.connected`

## Validation strategy

1. **Automated**: extend `scripts/migration/validate_parity.py` or add `scripts/migration/validate_api_parity.sh` hitting localhost endpoints vs baseline JSON
2. **Manual**: run UI with `DB_BACKEND=postgres`, compare dashboard to Oracle screenshot/baseline
3. **Contract**: existing OpenAPI `/openapi.json` unchanged paths

## Risks

| Risk | Mitigation |
|------|------------|
| LISTAGG port errors in risk-factors | Unit-test subquery; compare factor counts to Oracle |
| Bind parameter differences | Use `pg` named params or ordered arrays consistently |
| Tunnel not running | Health check fails fast; document in runbook |
| Case sensitivity on column names | Uppercase normalization in postgres adapter |

## Open Questions

- Collapse Next.js churn API routes entirely on Postgres branch? **Resolved → delete** (`remove-nextjs-churn-api-routes`)
- Single `npm run server:dev:postgres` script? (Recommend: yes)

## Resolved

- **Schema**: `ecomm` (from data migration change)
- **ADMIN join**: use `user_profiles.affinity_card`
- **Scoring**: read pre-materialized `churn_predictions` — no ONNX/pkl in API
