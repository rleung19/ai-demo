# Fix: ORA-28759 with ADB Wallet

## Solution

The ADB wallet's `sqlnet.ora` uses a relative path that doesn't resolve correctly with Oracle Instant Client:

**Original (doesn't work):**
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="?/network/admin")))
```

**Fixed (works):**
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="/Users/rleung/Documents/wallets/Wallet_HHZJ2H81DDJWN1DM")))
```

## Why This Works

The `?/network/admin` relative path doesn't resolve correctly with Oracle Instant Client in thick mode. Using an absolute path ensures Oracle can find the wallet files.

## Trade-off

**Pros:**
- ✅ Connection works
- ✅ No need for network/admin subdirectory

**Cons:**
- ⚠️ Less portable (hardcoded path)
- ⚠️ Need to update if wallet moves

## Alternative Solutions

If you need portability, you could:
1. Create a script that updates `sqlnet.ora` with the current wallet path
2. Use environment variables (though Oracle doesn't support them in sqlnet.ora directly)
3. Create symlinks to a standard location

## Current Status

✅ **Connection working** with absolute path in `sqlnet.ora`
