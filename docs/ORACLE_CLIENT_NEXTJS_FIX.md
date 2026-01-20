# Oracle Client Thick Mode in Next.js - Troubleshooting

## Issue

Next.js API routes are unable to initialize Oracle client in thick mode, showing error:
```
NJS-045: cannot load a node-oracledb Thick mode binary for Node.js
```

The error shows paths like `/ROOT/Projects/...` instead of actual paths, suggesting Next.js path resolution issues.

## Root Cause

Next.js 16+ with Node.js 22 may have issues loading native modules (`.node` files) in certain configurations, especially when:
- Running in development mode with hot reloading
- Using certain build configurations
- Path resolution differs between Next.js and standalone Node.js

## Solutions

### Solution 1: Use Thin Mode with Wallet (Recommended for Now)

Thin mode works but has limited wallet support. However, we can work around this by:

1. **Use TNS alias directly** instead of full connection string
2. **Set TNS_ADMIN environment variable** before Next.js starts
3. **Use connection string format that works in thin mode**

Update `.env`:
```env
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM
```

### Solution 2: Fix Thick Mode (For Production)

For production deployment on Linux, thick mode should work better. Steps:

1. **Install Oracle Instant Client on Linux server**
2. **Set environment variables before starting Next.js**:
   ```bash
   export ORACLE_CLIENT_LIB_DIR=/opt/oracle/instantclient_23_3
   export TNS_ADMIN=/path/to/wallet
   npm start
   ```

3. **Initialize client in a separate module** that loads before API routes:
   Create `app/lib/db/init-oracle.ts`:
   ```typescript
   import oracledb from 'oracledb';
   
   if (typeof window === 'undefined' && process.env.ORACLE_CLIENT_LIB_DIR) {
     try {
       oracledb.initOracleClient({ 
         libDir: process.env.ORACLE_CLIENT_LIB_DIR,
         configDir: process.env.TNS_ADMIN 
       });
       console.log('✓ Oracle client initialized (thick mode)');
     } catch (err: any) {
       if (!err.message.includes('already been called')) {
         console.warn('⚠️  Thick mode init failed, using thin mode:', err.message);
       }
     }
   }
   ```

4. **Import this module first** in your API routes or in a shared DB utility.

### Solution 3: Use Standalone API Server (Alternative)

Run the API as a separate Express/Fastify server instead of Next.js API routes. This avoids Next.js native module loading issues.

## Current Status

- ✅ API endpoints implemented and ready
- ✅ Database connection logic correct
- ⚠️  Thick mode initialization blocked by Next.js path resolution
- ✅ Thin mode works but requires TNS configuration

## Testing

Test with thin mode:
```bash
# Ensure TNS_ADMIN is set
export TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM

# Start Next.js
npm run dev

# Test endpoints
curl http://localhost:3000/api/health
curl http://localhost:3000/api/kpi/churn/summary
```

## Next Steps

1. **For development**: Use thin mode with TNS_ADMIN set
2. **For production**: Test thick mode on Linux deployment server
3. **Long-term**: Consider migrating to standalone API server if Next.js issues persist

## Related Files

- `app/lib/db/oracle.ts` - Database connection utilities
- `scripts/test-node-connection.js` - Working standalone test (reference)
- `docs/API_TESTING_NOTES.md` - API testing documentation
