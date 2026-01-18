# Oracle Instant Client for Apple Silicon (ARM64)

The Homebrew tap may only provide x86_64 versions. For Apple Silicon Macs, you need to download the ARM64 version directly from Oracle.

## Manual Installation for ARM64

1. **Download ARM64 Instant Client**:
   - Go to: https://www.oracle.com/database/technologies/instant-client/macos-arm64-downloads.html
   - Download "Basic Package" (ZIP file)
   - Download "SDK Package" (ZIP file) - optional but recommended

2. **Extract and Install**:
   ```bash
   # Create directory
   sudo mkdir -p /opt/oracle
   cd /opt/oracle
   
   # Extract Basic Package
   unzip instantclient-basic-macos.arm64-*.zip
   
   # Extract SDK Package (if downloaded)
   unzip instantclient-sdk-macos.arm64-*.zip
   
   # The directory should now be something like:
   # /opt/oracle/instantclient_21_*
   ```

3. **Set Environment Variables**:
   Add to your `~/.zshrc` or `~/.bash_profile`:
   ```bash
   export DYLD_LIBRARY_PATH=/opt/oracle/instantclient_21_*/:$DYLD_LIBRARY_PATH
   export ORACLE_HOME=/opt/oracle/instantclient_21_*
   ```

4. **Reload Shell**:
   ```bash
   source ~/.zshrc  # or source ~/.bash_profile
   ```

5. **Create Symlink** (optional, for compatibility):
   ```bash
   sudo ln -s /opt/oracle/instantclient_21_*/libclntsh.dylib.21.1 /opt/homebrew/lib/libclntsh.dylib
   ```

## Alternative: Use Rosetta (Not Recommended)

If you can't get ARM64 version, you can run Python under Rosetta:

```bash
# Install x86_64 Python via Rosetta
arch -x86_64 /usr/local/bin/python3 -m pip install oracledb

# Run scripts with Rosetta
arch -x86_64 python3 scripts/test-python-connection.py
```

**Note**: This is slower and not ideal. Prefer ARM64 native installation.

## Verify Installation

After installation, verify:
```bash
file /opt/oracle/instantclient_*/lib/libclntsh.dylib.*
# Should show: Mach-O 64-bit dynamically linked shared library arm64
```

## Update Test Script

Update the test script to use the manual installation path, or set `ORACLE_HOME` environment variable.
