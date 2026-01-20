# Oracle Instant Client Setup for Apple Silicon (M1/M2/M3)

If you're seeing architecture mismatch errors when running the connection tests, you need to install the ARM64 version of Oracle Instant Client.

## Quick Fix for Apple Silicon

### Option 1: Using Homebrew (Recommended)

```bash
# Install ARM64 version via Homebrew
brew install instantclient-basic instantclient-sdk

# Verify installation
ls -la /opt/homebrew/lib/libclntsh.dylib
```

### Option 2: Manual Installation

1. **Download ARM64 Instant Client**:
   - Go to: https://www.oracle.com/database/technologies/instant-client/macos-arm64-downloads.html
   - Download "Basic Package" and "SDK Package"
   - Extract to `/opt/oracle/instantclient_21_*` (or your preferred location)

2. **Set Environment Variables**:
   ```bash
   export DYLD_LIBRARY_PATH=/opt/oracle/instantclient_21_*/:$DYLD_LIBRARY_PATH
   export ORACLE_HOME=/opt/oracle/instantclient_21_*
   ```

3. **Add to your shell profile** (`~/.zshrc` or `~/.bash_profile`):
   ```bash
   export DYLD_LIBRARY_PATH=/opt/oracle/instantclient_21_*/:$DYLD_LIBRARY_PATH
   export ORACLE_HOME=/opt/oracle/instantclient_21_*
   ```

### Option 3: Use Docker (Alternative)

If you continue having issues, you can run the Python scripts in a Docker container with Oracle Instant Client pre-installed.

## Verify Installation

After installing, test again:

```bash
python scripts/test-python-connection.py
```

You should see:
- ✓ Oracle client initialized with wallet
- ✓ Successfully connected to ADB

## Troubleshooting

**Error: "mach-o file, but is an incompatible architecture"**
- You have x86_64 version installed
- Install ARM64 version instead
- Remove old x86_64 installation first

**Error: "Cannot locate Oracle Client library"**
- Set `DYLD_LIBRARY_PATH` environment variable
- Point to directory containing `libclntsh.dylib`
- Restart terminal after setting environment variables

**Error: "Listener refused connection"**
- Verify ADB instance is running in Oracle Cloud Console
- Check network connectivity
- Verify wallet files are correct
- Try using TNS alias from `tnsnames.ora` instead of connection string

## Using TNS Alias

If connection string format is causing issues, you can use TNS alias from `tnsnames.ora`:

1. Open `tnsnames.ora` in your wallet directory
2. Find the alias (e.g., `adbname_high`, `adbname_medium`)
3. Use that alias as `ADB_CONNECTION_STRING` in `.env`

Example:
```env
ADB_CONNECTION_STRING=adbname_high
```
