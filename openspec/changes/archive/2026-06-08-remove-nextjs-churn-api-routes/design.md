# Design: Express-Only Churn API

## Target architecture

```
Browser (Next.js UI :3000)
    │  fetch(NEXT_PUBLIC_API_URL || http://localhost:3001)
    ▼
Express churn API (:3001)
    │  DB_BACKEND=oracle | postgres
    ▼
ADB (OML)  or  Postgres (ecomm)

Next.js server
    ├── pages / React (app/)
    ├── NO /api/kpi/churn/*
    └── NO Oracle pool at startup
```

## NEXT_PUBLIC_API_URL semantics (updated)

| Value | Meaning |
|-------|---------|
| **Unset** | Local dev → `http://localhost:3001` |
| **URL** | Express API base (local or production, e.g. `https://ecomm-api.40b5c371.nip.io`) |
| ~~Empty string~~ | ~~Use Next.js /api/kpi/churn~~ — **removed** |

## Files to remove

```
app/api/kpi/churn/
  summary/route.ts
  cohorts/route.ts
  metrics/route.ts
  chart-data/route.ts
  risk-factors/route.ts

app/lib/db/oracle.ts          # Next-only; Express uses server/lib/db/
app/lib/db/README.md          # if Oracle-only
app/api/debug/oracle/route.ts
app/api/health/route.ts       # optional; Express /api/health is canonical for churn stack
```

## Files to simplify

- `instrumentation.ts` — remove Oracle init block (or delete file if empty)
- `app/lib/api/churn-api-backend.ts` — remove `usesNextJsChurnApi()`; always Express
- `app/lib/api/churn-api.ts` — update comments; require Express URL
- `docs/API_SERVER_SWITCH.md` — replace "switch to Next.js routes" with Express-only doc

## Express remains dual-DB

`DB_BACKEND` on **Express only** selects Oracle vs Postgres. Next.js never selects a database for churn KPIs.

## Risks

| Risk | Mitigation |
|------|------------|
| Someone relied on `:3000/api/kpi/churn` | Grep repo/docs; no production compose path uses it |
| Docker health via Next `/api/health` | Confirm container healthcheck; point to Express if needed |
| `oracledb` still in package.json for Express | Keep dependency; only remove `app/lib/db/oracle.ts` |

## Resolved

- **Delete vs deprecate**: Delete
- **Cohort detail**: Only on Express today; no Next.js loss
