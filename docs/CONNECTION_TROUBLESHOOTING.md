# Connection Troubleshooting Guide

## Quick Fix: Use TNS Alias

Your wallet contains TNS aliases that are easier to use. Update your `.env` file:

```env
# Instead of the full TNS connection string, use the alias:
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_high
# or
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
# or  
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_low
```

Available aliases in your wallet:
- `hhzj2h81ddjwn1dm_high` - High performance
- `hhzj2h81ddjwn1dm_medium` - Medium performance
- `hhzj2h81ddjwn1dm_low` - Low performance (most available)

## Common Issues

### Issue: "Oracle Instant Client not found"

**Solution**: Install Oracle Instant Client

For Apple Silicon (M1/M2/M3):
```bash
brew install instantclient-basic instantclient-sdk
```

For Intel Mac:
```bash
# Download from Oracle website
# https://www.oracle.com/database/technologies/instant-client/macos-x86-64-downloads.html
```

See [ORACLE_CLIENT_SETUP.md](ORACLE_CLIENT_SETUP.md) for detailed instructions.

### Issue: "Connection reset by peer" or "Listener refused connection"

**Possible causes:**
1. **ADB instance not running** - Check Oracle Cloud Console
2. **Network/firewall blocking** - Verify connectivity
3. **Wrong credentials** - Double-check username/password
4. **Wallet files corrupted** - Re-download wallet from Oracle Cloud Console
5. **Thin mode limitation** - ADB wallets require thick mode (Instant Client)

**Solutions:**
1. Verify ADB is running in Oracle Cloud Console
2. Try using TNS alias instead of full connection string
3. Install Oracle Instant Client for proper wallet support
4. Test connection with SQL Developer or SQL*Plus first

### Issue: "OML4Py not available"

**This is normal!** OML4Py is typically only available in OML Notebooks. For standalone Python:
- Use `oracledb` for database connections
- Run OML model operations via SQL or in OML Notebooks
- The API server will use `oracledb` for database access

### Issue: Environment variables not loading

**Check:**
1. `.env` file exists in project root
2. `python-dotenv` is installed: `pip install python-dotenv`
3. Script is run from project root or scripts directory
4. `.env` file has correct format (no spaces around `=`)

**Test:**
```bash
# Should show environment variables
python scripts/test-python-connection.py
```

## Testing Steps

1. **Verify .env file**:
   ```bash
   cat .env | grep ADB
   ```

2. **Test Python connection**:
   ```bash
   python scripts/test-python-connection.py
   ```

3. **Test Node.js connection**:
   ```bash
   node scripts/test-node-connection.js
   ```

4. **Verify wallet files**:
   ```bash
   ls -la $ADB_WALLET_PATH
   # Should show: tnsnames.ora, sqlnet.ora, cwallet.sso, etc.
   ```

## Still Having Issues?

1. Check [ADB_SETUP.md](ADB_SETUP.md) for complete setup guide
2. Check [ORACLE_CLIENT_SETUP.md](ORACLE_CLIENT_SETUP.md) for Instant Client setup
3. Verify ADB instance status in Oracle Cloud Console
4. Test with Oracle SQL Developer to isolate the issue
