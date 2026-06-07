# Architecture and Data Flow

## Churn KPI data path (Express-only)

```
┌─────────────┐
│   Browser   │
│  (Client)   │
└──────┬──────┘
       │
       │ HTTP Request
       │ NEXT_PUBLIC_API_URL || http://localhost:3001
       │ /api/kpi/churn/*
       │
       ▼
┌─────────────────────┐
│  Express Server     │
│  Port 3001          │
│  server/routes/     │
└──────┬──────────────┘
       │
       │ DB_BACKEND=oracle | postgres
       │
       ▼
┌─────────────────────┐
│  Oracle (ADB)       │
│  or PostgreSQL      │
└─────────────────────┘

Next.js Server (Port 3000)
└── UI only (React pages, static assets)
    └── Does NOT serve /api/kpi/churn/*
    └── Does NOT connect to the database for churn KPIs
```

**Key points:**

- The browser calls **Express directly** for all churn KPI endpoints.
- Next.js serves HTML/JS/CSS only; there are no duplicate Next.js churn API routes.
- `DB_BACKEND` on Express selects Oracle vs Postgres.

## Configuration

`app/lib/api/churn-api.ts` uses `getChurnApiBaseUrl()` from `churn-api-backend.ts`:

```typescript
// Unset → http://localhost:3001 (local)
// Set   → production Express URL
const API_BASE_URL = getChurnApiBaseUrl();
```

See [API_SERVER_SWITCH.md](API_SERVER_SWITCH.md) for environment variables.

## Data flow summary

```
Browser (Client)
  → fetch('http://localhost:3001/api/kpi/churn/summary')
    → Express Server (Port 3001)
      → server/lib/db (Oracle or Postgres)
        → Response → Browser
```

## Other API surfaces

- **Recommender** routes may exist on Next.js or Express depending on deployment; churn KPIs are Express-only.
- **Agentic flow** webhook is configured via `NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL` (n8n or similar).

## API request retries

Churn API calls in `app/lib/api/churn-api.ts` retry on network errors and 5xx responses (up to 3 retries). Health checks use a single retry.

## Related docs

- [API_SERVER_SWITCH.md](API_SERVER_SWITCH.md)
- [CHURN_API_REFERENCE.md](CHURN_API_REFERENCE.md)
- [POSTGRES_MIGRATION.md](POSTGRES_MIGRATION.md)
- [OCI_DEPLOYMENT_NOTES.md](OCI_DEPLOYMENT_NOTES.md)
