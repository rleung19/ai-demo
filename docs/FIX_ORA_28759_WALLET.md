# Fix ORA-28759: Wallet File Access Issue

## Problem

Even with ARM64 Oracle Instant Client installed and initialized, you're getting:
```
ORA-28759: failure to open file
```

This means Oracle can't access the wallet files for SSL/TLS connection.

## Root Cause

The `sqlnet.ora` file uses a relative path:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="?/network/admin")))
```

The `?/network/admin` should resolve to `TNS_ADMIN`, but Oracle might not be finding it correctly.

## Solutions

### Solution 1: Verify TNS_ADMIN is Set Before Client Initialization

The `TNS_ADMIN` environment variable must be set **before** calling `oracledb.init_oracle_client()`.

The script should:
1. Set `TNS_ADMIN` first
2. Then initialize the client with `config_dir` parameter
3. Ensure `TNS_ADMIN` remains set during connection

### Solution 2: Use Absolute Path in sqlnet.ora (Not Recommended)

You could modify `sqlnet.ora` to use absolute path, but this is not recommended as it makes the wallet less portable.

### Solution 3: Check File Permissions

Ensure wallet files are readable:
```bash
chmod 644 /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.ora
chmod 644 /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.sso
```

### Solution 4: Verify Wallet Directory Structure

The wallet directory should contain:
- `sqlnet.ora` ✓
- `tnsnames.ora` ✓
- `cwallet.sso` ✓
- `ewallet.p12` ✓
- Certificate files

### Solution 5: Test with sqlplus (If Available)

If you have `sqlplus` installed, test the connection:
```bash
export TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM
sqlplus OML@hhzj2h81ddjwn1dm_medium
```

If `sqlplus` works, the issue is with Python/oracledb configuration.

## Current Status

From your terminal output:
- ✓ ARM64 Instant Client found: `/opt/oracle/instantclient_23_3`
- ✓ Client initialized successfully
- ✓ TNS_ADMIN set correctly
- ✓ Wallet files exist and have correct permissions
- ❌ Still getting ORA-28759

## Next Steps

1. **Verify TNS_ADMIN is set before initialization** - The script should set it early
2. **Check if config_dir parameter is working** - Try with and without it
3. **Test with sqlplus** - If available, to isolate the issue
4. **Check Oracle Instant Client logs** - May provide more details

## Debugging

Add this to your script to verify TNS_ADMIN:
```python
import os
print(f"TNS_ADMIN before init: {os.getenv('TNS_ADMIN')}")
oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
print(f"TNS_ADMIN after init: {os.getenv('TNS_ADMIN')}")
```

The value should remain the same.
