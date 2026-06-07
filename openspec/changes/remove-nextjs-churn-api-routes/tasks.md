# Tasks: Remove Next.js Churn API (Express-Only)

## 1. Remove Next.js churn routes

- [x] 1.1 Delete `app/api/kpi/churn/` directory (all 5 routes)
- [x] 1.2 Delete `app/lib/db/oracle.ts` and update/remove `app/lib/db/README.md`
- [x] 1.3 Delete `app/api/debug/oracle/route.ts`
- [x] 1.4 Delete or repoint `app/api/health/route.ts` if Oracle-only (Express `/api/health` is canonical)

## 2. Simplify Next.js startup

- [x] 2.1 Remove Oracle pool init from `instrumentation.ts` (delete dead code or entire hook if unused)
- [x] 2.2 Simplify `app/lib/api/churn-api-backend.ts` — Express-only helper
- [x] 2.3 Update `app/lib/api/churn-api.ts` comments; no empty-string Next.js mode

## 3. Documentation

- [x] 3.1 Rewrite `docs/API_SERVER_SWITCH.md` → Express-only churn API doc
- [x] 3.2 Update `docs/CHURN_API_REFERENCE.md`, `docs/ARCHITECTURE_DATA_FLOW.md`
- [x] 3.3 Update `docs/POSTGRES_MIGRATION.md`, `.env.example`
- [x] 3.4 Grep for `app/api/kpi/churn` references in docs; fix or remove (active docs updated)

## 4. Validation

- [ ] 4.1 `npm run dev` — no Oracle init logs from Next.js
- [ ] 4.2 `npm run server:dev:postgres` + UI — dashboard loads all KPIs
- [x] 4.3 `npm run build` succeeds
- [x] 4.4 Confirm no imports of `@/app/lib/db/oracle` remain

## Definition of Done

- Single churn API surface: Express on `:3001` (or `NEXT_PUBLIC_API_URL` in prod)
- Next.js is UI-only for churn KPI data path
