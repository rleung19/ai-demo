# API Deduplication Debug Guide

## Current Status

We have implemented multi-layer deduplication to prevent duplicate API calls:

1. **Page Component Level** (`app/page.tsx`):
   - Window-level lock (`window.__pageKPI1FetchLock`)
   - Checks for existing promise (`window.__kpi1FetchPromise`)
   - Component-level refs (`hasFetchedKPI1`, `isFetchingKPI1`)

2. **Data Layer Level** (`app/data/kpis/index.ts`):
   - Global promise check (`window.__kpi1FetchPromise`)
   - Cache check (shared cache + legacy cache)
   - Triple-check before creating new promise
   - Promise stored synchronously before async work

3. **API Client Level** (`app/lib/api/churn-api.ts`):
   - Request-level deduplication (`window.__apiFetchPromises`)
   - Double-check before creating new fetch
   - Promise stored synchronously

## How to Debug

### Browser Console Logs

When the page loads, you should see logs like:

```
[Page] Starting KPI1 data fetch (window-level flag set)
[KPI1:abc123] getKPIData called, forceRefresh=false
[KPI1:abc123] 🔒 Acquiring lock - creating promise placeholder
[KPI1:abc123] ✅ Promise stored in global scope (lock acquired)
[KPI1:abc123] Fetching API data (5 endpoints in parallel)...
[API:/api/kpi/churn/summary] 🔒 Creating new fetch promise
[API:/api/kpi/churn/summary] ✅ Promise stored for deduplication
[API:/api/kpi/churn/cohorts] 🔒 Creating new fetch promise
...
[KPI1:abc123] All 5 API calls completed
```

If you see duplicate calls, look for:
- Multiple `[Page] Starting KPI1 data fetch` messages → Page-level deduplication failing
- Multiple `[KPI1:xxx] getKPIData called` messages → Data-layer deduplication failing
- Multiple `[API:xxx] 🔒 Creating new fetch promise` messages → API-level deduplication failing
- `[API:xxx] ✅ Deduplicating` messages → Deduplication working correctly

### Expected Behavior

**First Load:**
- Should see 5 API calls total (one per endpoint)
- All calls should happen in parallel (same timestamp)
- Should see deduplication logs if React StrictMode causes multiple mounts

**Refresh:**
- Should see 5 API calls OR fewer if cache is used
- Should see `[KPI1] ✅ Returning cached data` if cache is fresh

## Troubleshooting

### Still Seeing Multiple Calls

1. **Check Browser Console:**
   - Look for `[Page]` logs - are there multiple "Starting KPI1 data fetch" messages?
   - Look for `[KPI1]` logs - are there multiple "getKPIData called" messages?
   - Look for `[API]` logs - are there multiple "Creating new fetch promise" messages?

2. **Check Window State:**
   ```javascript
   // In browser console:
   console.log('Lock:', window.__pageKPI1FetchLock);
   console.log('Promise:', window.__kpi1FetchPromise);
   console.log('Fetch Promises:', window.__apiFetchPromises);
   ```

3. **Clear State and Retry:**
   ```javascript
   // In browser console:
   delete window.__pageKPI1FetchLock;
   delete window.__kpi1FetchPromise;
   delete window.__apiFetchPromises;
   // Then refresh the page
   ```

### React StrictMode

React StrictMode in development causes components to mount twice. Our deduplication should handle this, but if you're still seeing issues:

1. Check if the lock is being set before the second mount
2. Verify the promise is stored synchronously
3. Check if the window state persists across remounts

### Hot Module Reload

In development, Next.js hot module reload can reset module-level state but should preserve `window` state. If you see issues after code changes:

1. Hard refresh the browser (Cmd+Shift+R)
2. Check if window state persists
3. Verify the lock/promise are still in window

## Known Issues

1. **First Load Multiple Calls:**
   - React StrictMode can cause 3 mounts very quickly
   - Even with locks, there's a tiny window where multiple calls can slip through
   - The fetch-level deduplication should catch these

2. **Cache Not Working:**
   - Cache TTL is 60 seconds (CACHE_TTL = 60000)
   - If calls happen within 60 seconds, cache should be used
   - Check cache timestamp in logs

## Next Steps

If deduplication still isn't working:

1. Add more aggressive logging
2. Use a more robust locking mechanism (e.g., using `Atomics` or `SharedArrayBuffer` if available)
3. Consider using React Query or SWR for built-in request deduplication
4. Disable React StrictMode in development (not recommended, but can help debug)
