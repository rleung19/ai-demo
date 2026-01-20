# Thin Mode Setup for Next.js API

## Overview

Since thick mode has issues in Next.js development mode (NJS-045 error), we're using **thin mode** with TNS configuration for wallet access.

## Quick Start

### Option 1: Use npm script (Recommended)

```bash
npm run dev:oracle
```

This automatically sets `TNS_ADMIN` from your `.env` file.

### Option 2: Manual setup

```bash
# Set TNS_ADMIN before starting Next.js
export TNS_ADMIN=/path/to/your/wallet
npm run dev
```

Or add to your `.env` file:
```env
TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM
```

## How It Works

1. **Thin mode** is automatically used when thick mode initialization fails (NJS-045)
2. **TNS_ADMIN** environment variable tells thin mode where to find wallet files
3. **TNS alias** in connection string (e.g., `hhzj2h81ddjwn1dm_medium`) is resolved using `tnsnames.ora` from the wallet

## Connection String Format

Use **TNS alias** format in your `.env`:
```env
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
```

**Not** the full connection string - thin mode needs the TNS alias to resolve via `tnsnames.ora`.

## Testing

After starting Next.js with TNS_ADMIN set:

```bash
# Health check
curl http://localhost:3000/api/health

# Should show:
# {
#   "status": "healthy",
#   "services": { "database": "connected" }
# }
```

## Limitations

- Thin mode has **limited wallet support** compared to thick mode
- Some advanced Oracle features may not be available
- For production, consider using thick mode on Linux servers

## Troubleshooting

### Connection still fails?

1. **Verify TNS_ADMIN is set**:
   ```bash
   echo $TNS_ADMIN
   ```

2. **Check wallet files exist**:
   ```bash
   ls $TNS_ADMIN/tnsnames.ora
   ```

3. **Verify TNS alias in tnsnames.ora**:
   ```bash
   grep hhzj2h81ddjwn1dm_medium $TNS_ADMIN/tnsnames.ora
   ```

4. **Test connection with standalone script**:
   ```bash
   node scripts/test-node-connection.js
   ```

### Still having issues?

See `docs/ORACLE_CLIENT_NEXTJS_FIX.md` for more troubleshooting options.

## Production Deployment

For production on Linux:

1. Install Oracle Instant Client
2. Set environment variables:
   ```bash
   export ORACLE_CLIENT_LIB_DIR=/opt/oracle/instantclient_23_3
   export TNS_ADMIN=/path/to/wallet
   ```
3. Start Next.js - thick mode should work on Linux
