# Health Check Timeout Fix

## Issue

The `/api/health` endpoint was hanging indefinitely when called, causing requests to timeout.

## Root Cause

The health check endpoint calls `testConnection()` which attempts to connect to the database. Due to thin mode limitations, the connection attempt hangs indefinitely instead of failing quickly.

## Solution

Added a 3-second timeout to the database connection test in the health check endpoint:

```typescript
// Set a 3-second timeout for database connection test
const timeoutPromise = new Promise<boolean>((_, reject) => {
  setTimeout(() => reject(new Error('Database connection timeout')), 3000);
});

dbConnected = await Promise.race([
  testConnection(),
  timeoutPromise,
]) as boolean;
```

## Result

- **Before**: Health check hangs indefinitely, curl times out
- **After**: Health check returns in < 3 seconds with "degraded" status

## Response Format

When database connection times out:
```json
{
  "status": "degraded",
  "timestamp": "2026-01-18T15:00:44.778Z",
  "services": {
    "database": "disconnected"
  },
  "environment": {
    "hasWalletPath": true,
    "hasConnectionString": true,
    "hasUsername": true,
    "hasPassword": true
  },
  "databaseError": "Database connection timeout"
}
```

## Testing

```bash
# Should return quickly (< 3 seconds)
curl http://localhost:3000/api/health
curl http://localhost:3001/api/health
```

Both endpoints now respond quickly even when database connection fails.
