# ORA-28759 Solution: Wallet File Access

## Current Status

✅ **ARM64 Oracle Instant Client**: Found and initialized at `/opt/oracle/instantclient_23_3`  
✅ **TNS_ADMIN**: Set correctly to wallet directory  
✅ **Wallet Files**: All present and readable  
❌ **Connection**: Still getting ORA-28759 "failure to open file"

## The Problem

The `sqlnet.ora` file uses:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="?/network/admin")))
```

The `?/network/admin` should resolve to `TNS_ADMIN/network/admin`, but Oracle might not be finding the wallet files there.

## Possible Solutions

### Solution 1: Create network/admin Subdirectory (Try This First)

Oracle might expect the wallet in a subdirectory:

```bash
mkdir -p /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/network/admin
cp /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.ora /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/network/admin/
cp /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.sso /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/network/admin/
cp /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.p12 /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/network/admin/
```

Then test the connection again.

### Solution 2: Use Absolute Path in sqlnet.ora (Not Recommended)

Modify `sqlnet.ora` to use absolute path:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM")))
```

**Warning**: This makes the wallet less portable.

### Solution 3: Check Oracle Instant Client Version

Some versions of Oracle Instant Client have issues with wallet access. Verify you're using a recent version (21c or later).

### Solution 4: Test with sqlplus

If you have `sqlplus` installed, test if it works:
```bash
export TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM
sqlplus OML@hhzj2h81ddjwn1dm_medium
```

If `sqlplus` works, the issue is specific to Python/oracledb.

### Solution 5: Verify Wallet File Integrity

Re-download the wallet from Oracle Cloud Console to ensure files aren't corrupted.

## Next Steps

1. **Try Solution 1 first** - Create the network/admin subdirectory structure
2. **Test connection** - Run the test script again
3. **If still failing** - Try Solution 4 (sqlplus test) to isolate the issue
4. **Check Oracle documentation** - ORA-28759 troubleshooting guide

## Debugging

To verify TNS_ADMIN is being used correctly:
```python
import os
print(f"TNS_ADMIN: {os.getenv('TNS_ADMIN')}")
print(f"Files in TNS_ADMIN: {os.listdir(os.getenv('TNS_ADMIN'))}")
```

The wallet files should be accessible from the path specified in TNS_ADMIN.
