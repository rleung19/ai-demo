# Quick Fix: Update Connection String Format

## The Issue

You're currently using the full TNS description string in your `.env` file:
```env
ADB_CONNECTION_STRING=(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=gc810609a5803e6_hhzj2h81ddjwn1dm_tpurgent.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))
```

This format doesn't work well with thin mode (which you're using since Instant Client has architecture issues).

## The Solution

Update your `.env` file to use the simple TNS alias format:

```env
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_high
```

## Available TNS Aliases

From your `tnsnames.ora`, you have these options:
- `hhzj2h81ddjwn1dm_high` - High performance (recommended)
- `hhzj2h81ddjwn1dm_medium` - Medium performance
- `hhzj2h81ddjwn1dm_low` - Low performance (most available)
- `hhzj2h81ddjwn1dm_tpurgent` - TP Urgent (what you're currently using)

## Steps to Fix

1. **Edit your `.env` file**:
   ```bash
   # Change this line:
   ADB_CONNECTION_STRING=(description= ...)
   
   # To this:
   ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_high
   ```

2. **Test the connection**:
   ```bash
   python scripts/test-python-connection.py
   ```

The script will now:
- ✅ Use the TNS alias directly (simpler)
- ✅ Work better with thin mode
- ✅ Automatically use wallet configuration from `tnsnames.ora`

## Why This Works Better

- **TNS alias** is the standard Oracle format
- Works with both thin and thick mode
- Simpler and easier to debug
- Automatically uses all SSL/wallet settings from `tnsnames.ora`
- No need to parse complex description strings

## After Updating

Run the test script again - it should now:
1. Detect you're using a TNS alias
2. Use it directly
3. Connect successfully (assuming ADB is running and credentials are correct)
