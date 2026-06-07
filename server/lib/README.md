# Database Connection Utilities (Express)

## Overview

Oracle and PostgreSQL connection utilities for the **Express** churn API live under `server/lib/db/`.

## Files

- `server/lib/db/oracle.ts` — Oracle ADB pool and queries
- `server/lib/db/postgres.ts` — PostgreSQL pool and queries
- `server/lib/db/index.ts` — factory (`DB_BACKEND=oracle|postgres`)
- `server/lib/sql/churn-queries.ts` — SQL per backend

## Usage

```typescript
import { executeQuery } from '../../lib/db';

const result = await executeQuery('SELECT 1 FROM DUAL');
```

## Environment

- **Oracle**: `ADB_WALLET_PATH`, `ADB_CONNECTION_STRING`, `ADB_USERNAME`, `ADB_PASSWORD`
- **Postgres**: `DATABASE_URL` or `PGHOST`/`PGPORT`/`PGUSER`/`PGPASSWORD`/`PGDATABASE`
- **Backend switch**: `DB_BACKEND=oracle|postgres` (Express only)

Next.js does not connect to the database for churn KPIs. See `docs/API_SERVER_SWITCH.md`.
