# Oracle ADB Serverless Setup Guide

This guide walks you through setting up Oracle Autonomous Database Serverless for the churn model backend API.

## Prerequisites

1. **Oracle Cloud Account** with access to Oracle Autonomous Database
2. **ADB Instance** created and running
3. **OML Enabled** on your ADB instance
4. **Administrative Access** to download wallet and create schemas

## Step 1: Download ADB Wallet

1. Log into [Oracle Cloud Console](https://cloud.oracle.com)
2. Navigate to **Autonomous Database** → Your ADB instance
3. Click **DB Connection** button
4. Under **Download Wallet**, click **Download**
5. Enter a password for the wallet (save this securely)
6. Save the wallet ZIP file to your local machine

## Step 2: Extract and Configure Wallet

1. Extract the wallet ZIP file to a directory (e.g., `./wallet` or `~/adb-wallet`)
2. The wallet directory should contain:
   - `tnsnames.ora` - Connection strings
   - `sqlnet.ora` - Network configuration
   - `cwallet.sso` - Encrypted wallet
   - `ewallet.p12` - PKCS12 wallet
   - Certificate files (`.pem`)

3. **Important**: Keep the wallet directory secure and never commit it to version control

## Step 3: Find Connection String

1. Open `tnsnames.ora` from the wallet directory
2. Find the connection alias (e.g., `adbname_high`, `adbname_medium`, `adbname_low`)
3. The connection string format is: `hostname:port/service_name`
   - Example: `adb.us-ashburn-1.oraclecloud.com:1522/adbname_high`

## Step 4: Create OML Schema (if needed)

If you don't have an OML schema yet:

1. Connect to ADB using SQL Developer, SQL*Plus, or Oracle Cloud Console SQL Worksheet
2. Connect as ADMIN user
3. Create OML schema:

```sql
-- Create OML user
CREATE USER OML IDENTIFIED BY "YourSecurePassword";

-- Grant necessary privileges
GRANT CONNECT, RESOURCE TO OML;
GRANT CREATE VIEW TO OML;
GRANT CREATE TABLE TO OML;
GRANT CREATE SEQUENCE TO OML;
GRANT UNLIMITED TABLESPACE TO OML;

-- Grant OML-specific privileges (if available)
BEGIN
  DBMS_CLOUD_ADMIN.GRANT_ADMIN_PRIVILEGE(
    grantee => 'OML',
    privilege_type => 'OML'
  );
END;
/
```

4. Note: OML privileges may vary by ADB configuration. Check Oracle documentation for your specific setup.

## Step 5: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set the following:
   ```env
   ADB_WALLET_PATH=/path/to/your/wallet
   ADB_CONNECTION_STRING=hostname:port/service_name
   ADB_USERNAME=OML
   ADB_PASSWORD=YourSecurePassword
   TNS_ADMIN=/path/to/your/wallet
   ```

3. **Security**: Never commit `.env` file to version control

## Step 6: Install Oracle Instant Client

### macOS

```bash
# Using Homebrew
brew install instantclient-basic instantclient-sdk

# Or download from Oracle website
# https://www.oracle.com/database/technologies/instant-client/downloads.html
```

### Linux

```bash
# Download Oracle Instant Client RPMs
# https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html

# Install RPMs
sudo rpm -ivh oracle-instantclient-basic-*.rpm
sudo rpm -ivh oracle-instantclient-sdk-*.rpm
```

### Windows

1. Download Oracle Instant Client from Oracle website
2. Extract to a directory (e.g., `C:\oracle\instantclient_21_3`)
3. Add to PATH environment variable

## Step 7: Install OML4Py (Python)

OML4Py is typically installed as part of Oracle Machine Learning client:

1. Download Oracle Machine Learning client from Oracle website
2. Follow installation instructions for your platform
3. OML4Py is available when connected to ADB via OML Notebooks or when properly configured

**Note**: OML4Py may require specific Oracle client versions. Check Oracle documentation.

## Step 8: Test Connections

### Test Python Connection

```bash
python scripts/test-python-connection.py
```

### Test Node.js Connection

```bash
node scripts/test-node-connection.js
```

Both scripts should show:
- ✓ Wallet path found
- ✓ Connection successful
- ✓ Test query successful

## Troubleshooting

### Connection Errors

**Error: "ORA-12154: TNS:could not resolve the connect identifier"**
- Verify `ADB_CONNECTION_STRING` matches format in `tnsnames.ora`
- Check `TNS_ADMIN` environment variable points to wallet directory
- Ensure wallet files are in the correct location

**Error: "ORA-12541: TNS:no listener"**
- Verify ADB instance is running in Oracle Cloud Console
- Check network connectivity (firewall, VPN)
- Verify connection string uses correct port (usually 1522)

**Error: "ORA-01017: invalid username/password"**
- Double-check `ADB_USERNAME` and `ADB_PASSWORD`
- Ensure password doesn't contain special characters that need escaping
- Try connecting with SQL Developer to verify credentials

**Error: "Oracle Client library not found"**
- Install Oracle Instant Client
- Set `LD_LIBRARY_PATH` (Linux) or `DYLD_LIBRARY_PATH` (macOS)
- On Windows, ensure Instant Client is in PATH

### OML4Py Issues

**Error: "Module 'oml' not found"**
- OML4Py is typically available in OML Notebooks environment
- For standalone Python, ensure Oracle Machine Learning client is installed
- Check Oracle documentation for OML4Py installation outside OML Notebooks

**Error: "OML not connected"**
- This is normal when running outside OML Notebooks
- Connection will be established when needed
- Verify wallet and credentials are correct

### Permission Issues

**Error: "ORA-01031: insufficient privileges"**
- Verify OML user has necessary privileges (see Step 4)
- Check if OML schema exists and is accessible
- Ensure user has CREATE TABLE, CREATE VIEW privileges

## Security Best Practices

1. **Never commit wallet files** to version control
2. **Use strong passwords** for wallet and database users
3. **Restrict wallet file permissions**:
   ```bash
   chmod 600 wallet/*.pem wallet/*.p12
   chmod 700 wallet/
   ```
4. **Rotate passwords** regularly
5. **Use environment variables** for credentials, never hardcode
6. **Limit wallet access** to necessary users only

## Next Steps

After completing setup:

1. ✅ Verify connections work (run test scripts)
2. ✅ Proceed to Dataset Acquisition (Section 2 of tasks)
3. ✅ Set up ML Pipeline (Section 3 of tasks)

## Additional Resources

- [Oracle ADB Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
- [OML4Py Documentation](https://docs.oracle.com/en/database/oracle/machine-learning/oml4py/)
- [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
