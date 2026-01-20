# ADB Connection String Format Guide

## Recommended Format: TNS Alias

**Use the TNS alias from `tnsnames.ora`** - This is the simplest and most reliable format.

### Find Your TNS Alias

1. Open `tnsnames.ora` in your wallet directory
2. Look for lines like:
   ```
   hhzj2h81ddjwn1dm_high = (description= ...)
   hhzj2h81ddjwn1dm_medium = (description= ...)
   hhzj2h81ddjwn1dm_low = (description= ...)
   ```
3. The part before the `=` is your TNS alias

### Update .env File

Use the simple alias format:

```env
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_high
```

**NOT** the full description string:
```env
# ❌ DON'T USE THIS FORMAT:
ADB_CONNECTION_STRING=(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=gc810609a5803e6_hhzj2h81ddjwn1dm_tpurgent.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))
```

## Connection String Formats

### Format 1: TNS Alias (Recommended)
```env
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_high
```
- ✅ Works with both thin and thick mode
- ✅ Simplest format
- ✅ Uses wallet configuration automatically

### Format 2: Host:Port/Service (Thin Mode)
```env
ADB_CONNECTION_STRING=adb.us-chicago-1.oraclecloud.com:1522/gc810609a5803e6_hhzj2h81ddjwn1dm_high.adb.oraclecloud.com
```
- ✅ Works with thin mode
- ⚠️ Requires extracting from TNS description
- ⚠️ May need additional SSL configuration

### Format 3: Full TNS Description (Thick Mode Only)
```env
ADB_CONNECTION_STRING=(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=gc810609a5803e6_hhzj2h81ddjwn1dm_tpurgent.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))
```
- ⚠️ Only works with thick mode (Oracle Instant Client)
- ⚠️ Complex format, harder to debug
- ❌ Does NOT work with thin mode

## Which Format to Use?

### For Thin Mode (No Instant Client)
- **Use**: TNS alias (Format 1) ✅
- **Or**: Host:Port/Service (Format 2) ✅
- **Avoid**: Full TNS description (Format 3) ❌

### For Thick Mode (With Instant Client)
- **Use**: TNS alias (Format 1) ✅ (Recommended)
- **Or**: Full TNS description (Format 3) ✅
- **Or**: Host:Port/Service (Format 2) ✅

## Your Current Setup

Based on your `tnsnames.ora`, you have these aliases available:
- `hhzj2h81ddjwn1dm_high` - High performance connection
- `hhzj2h81ddjwn1dm_medium` - Medium performance connection  
- `hhzj2h81ddjwn1dm_low` - Low performance connection (most available)

**Recommended**: Update your `.env` file to:
```env
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_high
```

## Testing

After updating `.env`, test the connection:
```bash
python scripts/test-python-connection.py
```

The script will automatically:
1. Detect if you're using a TNS alias
2. Use it directly if it's a simple alias
3. Extract the alias from `tnsnames.ora` if you're using full description
4. Convert to appropriate format for thin/thick mode
