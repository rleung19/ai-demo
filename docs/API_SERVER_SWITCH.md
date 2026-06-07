# Churn API Configuration

## Overview

The churn dashboard uses a **single API surface**: the **Express** server (`server/`). Next.js (`app/`) serves the UI only and never implements churn KPI routes.

```
Browser (Next.js UI :3000)
    │  fetch(NEXT_PUBLIC_API_URL || http://localhost:3001)
    ▼
Express churn API (:3001)
    │  DB_BACKEND=oracle | postgres
    ▼
Oracle (ADB)  or  PostgreSQL (ecomm)
```

## Local development

Start both servers:

```bash
# Terminal 1: Express API (Oracle or Postgres)
npm run server:dev
# Postgres: npm run server:dev:postgres

# Terminal 2: Next.js UI
npm run dev
```

Open `http://localhost:3000`. The UI calls Express at `http://localhost:3001` by default.

## Configuration

Base URL is resolved in `app/lib/api/churn-api-backend.ts`:

```typescript
export const DEFAULT_EXPRESS_API_URL = 'http://localhost:3001';

export function getChurnApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_EXPRESS_API_URL;
}
```

| `NEXT_PUBLIC_API_URL` | Meaning |
|-----------------------|---------|
| **Unset** | Local dev → `http://localhost:3001` |
| **URL** | Express API base (e.g. `https://ecomm-api.example.com`) |

`DB_BACKEND` is read by **Express only** (`oracle` or `postgres`). Next.js does not connect to the database for churn KPIs.

## API endpoints (Express)

All churn routes live on the Express server:

- `GET /api/health` — health check (includes database status)
- `GET /api/kpi/churn/summary` — summary metrics
- `GET /api/kpi/churn/cohorts` — cohort breakdown
- `GET /api/kpi/churn/cohorts/:name` — cohort detail (Express only)
- `GET /api/kpi/churn/metrics` — model metrics
- `GET /api/kpi/churn/chart-data?type=distribution` — chart data
- `GET /api/kpi/churn/risk-factors` — risk factors

OpenAPI: `http://localhost:3001/api-docs` when the Express server is running.

## Production

Set `NEXT_PUBLIC_API_URL` to your public Express API URL (build-time variable for the Next.js client):

```env
NEXT_PUBLIC_API_URL=https://ecomm-api.example.com
```

Ensure CORS on Express allows the Next.js origin if they are on different domains.

## Troubleshooting

### Express not responding

```bash
lsof -i :3001
curl http://localhost:3001/api/health
```

### UI shows no KPI data

1. Confirm Express is running and healthy.
2. Check browser network tab — requests should go to `:3001` (or your `NEXT_PUBLIC_API_URL`), not `:3000/api/kpi/churn`.
3. For Postgres: tunnel running, `DB_BACKEND=postgres`, `DATABASE_URL` set.

### CORS errors

Express enables CORS for local dev. For production cross-origin setups, configure allowed origins on Express.

## Related docs

- [STARTING_SERVERS.md](STARTING_SERVERS.md) — startup scripts and ports
- [POSTGRES_MIGRATION.md](POSTGRES_MIGRATION.md) — Postgres backend
- [CHURN_API_REFERENCE.md](CHURN_API_REFERENCE.md) — request/response contracts
