# Database Connection Fix

## Issue
API endpoints were failing with `ORA-12162: TNS:net service name is incorrectly specified` even though:
- Connection string (`hhzj2h81ddjwn1dm_medium`) exists in `tnsnames.ora`
- Environment variables are loaded correctly
- Wallet path is set

## Root Cause
The Oracle client initialization order was incorrect. The `test-node-connection.js` script works because it:
1. Sets `TNS_ADMIN` BEFORE calling `initOracleClient()`
2. Uses `configDir: walletPath` in `initOracleClient()`
3. Ensures environment variables are loaded before any Oracle operations

The server code was initializing Oracle client on module load, potentially before environment variables were fully loaded.

## Fix Applied
1. **Removed automatic initialization on module load** - Now initialization happens lazily when `getConnection()` or `getPool()` is called
2. **Set TNS_ADMIN before initOracleClient** - Both `getPool()` and `getConnection()` now set `TNS_ADMIN` before calling `initializeOracleClient()`
3. **Always set TNS_ADMIN** - Changed from conditional (`if (!process.env.TNS_ADMIN)`) to always setting it to ensure consistency

## Changes Made
- `server/lib/db/oracle.ts`:
  - Removed module-level initialization
  - Added `TNS_ADMIN` setting in `getPool()` before initialization
  - Added `TNS_ADMIN` setting in `getConnection()` before initialization
  - Changed `initializeOracleClient()` to always set `TNS_ADMIN` (not conditional)

## Testing
After restarting the server, test with:
```bash
curl http://localhost:3001/api/health
curl http://localhost:3001/api/kpi/churn/summary
```

Expected: Database should connect successfully and endpoints should return real data instead of fallback errors.
