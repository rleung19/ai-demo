# Next.js API Routes Review

## Current Situation

The Next.js app currently has duplicate API routes that are **no longer used** by the frontend:

```
app/api/
├── health/route.ts                      # Duplicate of server/routes/health.ts
├── kpi/churn/
│   ├── summary/route.ts                # Duplicate of server/routes/kpi/churn/summary.ts
│   ├── cohorts/route.ts                # Duplicate of server/routes/kpi/churn/cohorts.ts
│   ├── metrics/route.ts                # Duplicate of server/routes/kpi/churn/metrics.ts
│   ├── chart-data/route.ts             # Duplicate of server/routes/kpi/churn/chart-data.ts
│   └── risk-factors/route.ts           # Duplicate of server/routes/kpi/churn/risk-factors.ts
└── debug/oracle/route.ts                # Debug route (may be unique)
```

## Why They Exist

These were the **original implementation** before we separated the Express API server. When everything was in Next.js, these routes served the frontend directly.

## Current Frontend Behavior

The frontend now calls the **Express API server**:

```typescript
// app/lib/api/churn-api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// All API calls go to Express, NOT Next.js API routes
export async function fetchChurnSummary(): Promise<ChurnSummary> {
  const response = await fetch(`${API_BASE_URL}/api/kpi/churn/summary`);
  // ...
}
```

**Local dev**: Calls `http://localhost:3001` (Express)  
**Production**: Calls `https://ecomm-api.40b5c371.nip.io` (Express via Caddy)

**Next.js API routes are never called.**

## Options

### Option 1: Keep Them (Current State)

**Pros:**
- ✅ Backup/fallback if Express fails
- ✅ Can test/debug without running Express
- ✅ No breaking changes
- ✅ Flexibility for future

**Cons:**
- ❌ Maintenance burden (two copies of code)
- ❌ Confusion about which is "source of truth"
- ❌ Increases bundle size slightly
- ❌ Database connections from two servers

### Option 2: Remove Them (Recommended)

**Pros:**
- ✅ Single source of truth (Express)
- ✅ Reduces maintenance
- ✅ Clearer architecture
- ✅ Smaller Next.js bundle
- ✅ Only one server connects to database

**Cons:**
- ❌ No fallback if Express fails
- ❌ Must run Express for local dev (already required)
- ❌ Can't test Next.js API routes independently

### Option 3: Keep Debug Route Only

Remove all churn KPI routes but keep `/api/debug/oracle` for troubleshooting.

**Pros:**
- ✅ Cleanup duplicates
- ✅ Keep debugging capability
- ✅ Minimal maintenance

**Cons:**
- ❌ Still some duplication

## Recommendation

**Remove the Next.js API routes** (Option 2) because:

1. **Frontend exclusively uses Express** - These routes are dead code
2. **Express is required** - Can't run the app without Express (needs recommender APIs)
3. **Single source of truth** - Easier to maintain, less confusion
4. **Production architecture** - Next.js (port 3002) and Express (port 3003) are separate services with distinct responsibilities:
   - Next.js: Frontend UI rendering
   - Express: All API endpoints

## Implementation

If you choose to remove them:

```bash
# Backup first
mkdir -p backup/app-api
cp -r app/api backup/app-api/

# Remove the routes
rm -rf app/api/kpi
rm -rf app/api/health
# Keep debug route if desired: app/api/debug/oracle/route.ts

# Also remove the database utilities from app/lib (if not used elsewhere)
# app/lib/db/oracle.ts (check if debug route uses it)
```

## Decision

**Your choice:**
- [ ] Option 1: Keep everything as-is
- [ ] Option 2: Remove all duplicate routes (recommended)
- [ ] Option 3: Keep only debug route
- [ ] Other: ___________

---

**Note**: This is a cleanup task, not urgent. The current setup works fine, just has some technical debt.
