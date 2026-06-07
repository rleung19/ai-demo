# Change: Remove Next.js Churn API Routes (Express-Only)

## Why

The churn dashboard has two parallel API implementations: **Express** (`server/routes/churn/*` on `:3001`) and **duplicate Next.js App Router routes** (`app/api/kpi/churn/*` on `:3000`). Express is the primary, fully featured backend (includes cohort-detail, Postgres support, OpenAPI). The Next.js routes are legacy, Oracle-only, incomplete, and create confusion (instrumentation, wallet init, dual maintenance).

**Decision: Express is the only churn API.** The Next.js app serves UI only and always calls Express via `NEXT_PUBLIC_API_URL`.

## What Changes

- **Delete** `app/api/kpi/churn/*` (5 route files)
- **Delete** `app/lib/db/oracle.ts` and related Next-only DB utilities under `app/lib/db/` (Express uses `server/lib/db/`)
- **Delete or simplify** Next.js paths that only existed for churn Oracle access:
  - `app/api/health/route.ts` (if Oracle-only; Express has `/api/health`)
  - `app/api/debug/oracle/route.ts`
- **Remove** Oracle pool initialization from `instrumentation.ts` entirely (no Next.js churn DB)
- **Simplify** `app/lib/api/churn-api.ts` and `churn-api-backend.ts` — always target Express; `NEXT_PUBLIC_API_URL` is the Express/public API base URL only
- **Update docs** that describe switching to Next.js API routes (`API_SERVER_SWITCH.md`, etc.)

**Not deleted:**

- Express churn API (`server/`)
- Recommender Next.js or Express routes (unchanged)
- `NEXT_PUBLIC_API_URL` for production (points at public Express URL, e.g. `https://ecomm-api.example.com`)

## Why delete (not deprecate)

| Approach | Verdict |
|----------|---------|
| **Delete** | Recommended — removes dead code, no Oracle in Next.js, one clear path, matches workshop goal |
| **Deprecate** (410/redirect stubs) | Adds maintenance for routes nobody should call; still ships Oracle SQL in repo |

Deprecation only makes sense if external clients call `:3000/api/kpi/churn/*` today. This repo’s UI and docs already default to Express; the Next routes were an early pattern before the standalone server.

## Impact

- **Affected specs**: `churn-model-api` — MODIFIED: churn REST API served by Express only; REMOVED Next.js duplicate requirement implications
- **Affected code**: `app/api/kpi/churn/`, `app/lib/db/oracle.ts`, `instrumentation.ts`, docs
- **Branch**: `feature/postgres-backend` (can merge to `main` when ready)
- **Depends on**: Express Postgres backend (`add-postgres-churn-api-backend`)

## Success Criteria

- No `app/api/kpi/churn/*` routes remain
- `npm run dev` starts Next.js without Oracle client/pool logs
- UI loads KPI data exclusively from Express (`:3001` local, public URL in prod)
- `npm run server:build` and `npm run build` succeed
