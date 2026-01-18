# Fix ORA-28759: Failure to Open File

## Error Description

`ORA-28759: failure to open file` occurs when Oracle Instant Client cannot access wallet files for SSL/TLS connections to ADB.

## Common Causes

1. **TNS_ADMIN not set correctly** - Oracle can't find wallet configuration files
2. **Wallet file permissions** - Files not readable
3. **Wallet directory path issues** - Path not accessible or incorrect
4. **sqlnet.ora configuration** - Relative paths not resolving correctly

## Solutions

### Solution 1: Set TNS_ADMIN Explicitly

Add to your `.env` file:

```env
TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM
```

This ensures Oracle knows where to find wallet files.

### Solution 2: Verify Wallet File Permissions

Check that wallet files are readable:

```bash
ls -la /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/
```

All files should be readable (not just by owner). If needed:

```bash
chmod 644 /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.ora
chmod 644 /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.sso
chmod 644 /Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM/*.p12
```

### Solution 3: Check sqlnet.ora Configuration

Your `sqlnet.ora` contains:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="?/network/admin")))
```

The `?/network/admin` is a relative path. With `TNS_ADMIN` set correctly, Oracle should resolve this to your wallet directory.

### Solution 4: Verify Wallet Files Exist

Ensure these files exist in your wallet directory:
- `sqlnet.ora` ✓
- `tnsnames.ora` ✓
- `cwallet.sso` ✓
- `ewallet.p12` ✓
- Certificate files (`.pem`)

### Solution 5: Test TNS_ADMIN Setting

Verify TNS_ADMIN is set correctly:

```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('TNS_ADMIN:', os.getenv('TNS_ADMIN'))
print('Wallet path:', os.getenv('ADB_WALLET_PATH'))
"
```

Both should point to the same directory.

## Quick Fix

1. **Add to `.env`**:
   ```env
   TNS_ADMIN=/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM
   ```

2. **Test connection**:
   ```bash
   python3 scripts/test-python-connection.py
   ```

## Why This Happens

Oracle Instant Client needs to know where to find:
- `sqlnet.ora` - Network configuration
- `tnsnames.ora` - Connection aliases
- Wallet files - SSL certificates

Setting `TNS_ADMIN` tells Oracle where to look for these files.

## Verification

After setting `TNS_ADMIN`, the connection should work. If you still get ORA-28759:

1. Check wallet directory permissions
2. Verify all wallet files exist
3. Try re-downloading wallet from Oracle Cloud Console
4. Check if wallet directory path has special characters or spaces
