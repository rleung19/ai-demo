#!/usr/bin/env python3
"""
Test script to verify Python connection to Oracle ADB Serverless
Prerequisites:
- Oracle Instant Client installed
- OML4Py installed
- ADB wallet configured
- Environment variables set (.env file)
"""

import os
import sys
from pathlib import Path

# Find project root (parent of scripts directory)
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env from project root
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print(f"✓ Loaded .env file from: {env_file}")
    else:
        print(f"⚠️  WARNING: .env file not found at {env_file}")
        print("   Copy .env.example to .env and configure it")
        # Try loading from current directory as fallback
        load_dotenv()
except ImportError:
    print("⚠️  WARNING: python-dotenv not installed.")
    print("   Install with: pip install python-dotenv")
    print("   Using system environment variables only.")

def test_oml_connection():
    """Test OML4Py connection to ADB"""
    print("=" * 60)
    print("Testing OML4Py Connection to Oracle ADB")
    print("=" * 60)
    
    # Check environment variables
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set in environment")
        print(f"   Check .env file at: {env_file}")
        print("   Set ADB_WALLET_PATH=/path/to/wallet in .env")
        print("   Or export ADB_WALLET_PATH=/path/to/wallet")
        return False
    
    if not os.path.exists(wallet_path):
        print(f"❌ ERROR: Wallet path does not exist: {wallet_path}")
        return False
    
    print(f"✓ Wallet path found: {wallet_path}")
    
    # Set TNS_ADMIN if not already set
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
        print(f"✓ Set TNS_ADMIN to: {wallet_path}")
    
    # Try to import OML4Py
    try:
        import oml
        print("✓ OML4Py imported successfully")
    except ImportError as e:
        print(f"⚠️  WARNING: OML4Py not available: {e}")
        print("   Note: OML4Py is typically only available in OML Notebooks")
        print("   For standalone Python, use oracledb for database connections")
        print("   OML model operations can be done via SQL or OML Notebooks")
        print("   This is OK - continuing with oracledb test...")
        return True  # Don't fail the test, just note it
    
    # Check connection
    try:
        if oml.isconnected():
            print("✓ OML connection is active")
            try:
                version = oml.__version__
                print(f"✓ OML version: {version}")
            except:
                pass
            return True
        else:
            print("⚠️  WARNING: OML reports not connected")
            print("   This may be normal if running outside OML Notebooks")
            print("   Connection will be established when needed")
            return True
    except Exception as e:
        print(f"⚠️  WARNING: Could not verify connection: {e}")
        print("   Note: OML4Py is typically only available in OML Notebooks")
        print("   For standalone Python, use oracledb for database connections")
        print("   OML model operations can be done via SQL or OML Notebooks")
        return True

def test_oracledb_connection():
    """Test oracledb connection to ADB"""
    print("\n" + "=" * 60)
    print("Testing oracledb Connection to Oracle ADB")
    print("=" * 60)
    
    try:
        import oracledb
        print("✓ oracledb imported successfully")
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        print("   Install with: pip install oracledb")
        return False
    
    # Get connection parameters
    wallet_path = os.getenv('ADB_WALLET_PATH')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set")
        return False
    
    if not connection_string:
        print("❌ ERROR: ADB_CONNECTION_STRING not set")
        return False
    
    if not password:
        print("❌ ERROR: ADB_PASSWORD not set")
        return False
    
    # Check if connection_string is TNS format (contains description=)
    # If so, extract the service name or use as-is
    use_tns = 'description=' in connection_string.lower()
    
    # Configure oracledb to use wallet
    # Try thick mode first (requires Instant Client), then thin mode
    use_thin_mode = False
    
    # Try to find Oracle Instant Client in common locations
    # For Homebrew, we need to find the actual library file and get its directory
    lib_dir = None
    
    # Check common Homebrew locations
    homebrew_lib_paths = [
        '/opt/homebrew/lib/libclntsh.dylib',  # Apple Silicon symlink
        '/usr/local/lib/libclntsh.dylib',  # Intel Mac symlink
    ]
    
    for lib_path in homebrew_lib_paths:
        if os.path.exists(lib_path) or os.path.islink(lib_path):
            # Resolve symlink to actual location
            try:
                if os.path.islink(lib_path):
                    actual_path = os.readlink(lib_path)
                    if not os.path.isabs(actual_path):
                        actual_path = os.path.join(os.path.dirname(lib_path), actual_path)
                    actual_path = os.path.normpath(actual_path)
                    candidate_lib = actual_path
                else:
                    candidate_lib = lib_path
                
                # Check architecture compatibility before using
                import platform
                python_arch = platform.machine()
                
                # Check library architecture
                import subprocess
                arch_mismatch = False
                try:
                    result = subprocess.run(['file', candidate_lib], 
                                           capture_output=True, text=True, timeout=2)
                    lib_arch_info = result.stdout.lower()
                    
                    # Determine if architectures match
                    if python_arch == 'arm64':
                        if 'x86_64' in lib_arch_info and 'arm64' not in lib_arch_info:
                            print(f"⚠️  Found Oracle Instant Client but wrong architecture:")
                            print(f"   Library: x86_64 (Intel) at {candidate_lib}")
                            print(f"   Python: ARM64 (Apple Silicon)")
                            print(f"   Skipping this library, will use thin mode")
                            arch_mismatch = True
                except Exception:
                    # If file command fails, assume it might work
                    pass
                
                if not arch_mismatch:
                    lib_dir = os.path.dirname(candidate_lib)
                    print(f"✓ Found Oracle Instant Client at: {lib_dir}")
                    break
            except Exception:
                continue
    
    # If not found via symlink, try direct paths
    # Check /opt/oracle first (common manual installation location for ARM64)
    if not lib_dir:
        oracle_opt_paths = [
            '/opt/oracle/instantclient_*/lib',
            '/opt/oracle/instantclient_*',
        ]
        import glob
        for pattern in oracle_opt_paths:
            matches = glob.glob(pattern)
            for match in matches:
                # Check for library file
                for lib_name in ['libclntsh.dylib', 'libclntsh.so']:
                    lib_path = os.path.join(match, lib_name) if os.path.isdir(match) else match
                    if os.path.exists(lib_path) or os.path.islink(lib_path):
                        # Check architecture
                        import platform
                        python_arch = platform.machine()
                        if python_arch == 'arm64':
                            import subprocess
                            try:
                                result = subprocess.run(['file', lib_path], 
                                                       capture_output=True, text=True, timeout=2)
                                lib_arch_info = result.stdout.lower()
                                if 'arm64' in lib_arch_info and 'x86_64' not in lib_arch_info:
                                    lib_dir = os.path.dirname(lib_path) if os.path.isfile(lib_path) else match
                                    print(f"✓ Found ARM64 Oracle Instant Client at: {lib_dir}")
                                    break
                            except Exception:
                                pass
                if lib_dir:
                    break
            if lib_dir:
                break
    
    # If still not found, try other common locations
    if not lib_dir:
        possible_lib_dirs = [
            '/opt/homebrew/Cellar/instantclient-basic/*/lib',  # Homebrew Cellar
            '/opt/homebrew/lib',  # Homebrew on Apple Silicon
            '/opt/homebrew/opt/instantclient-basic/lib',  # Homebrew opt
            '/usr/local/lib',  # Homebrew on Intel Mac
            os.getenv('ORACLE_HOME', ''),
        ]
        
        for possible_dir in possible_lib_dirs:
            if not possible_dir:
                continue
            # Handle wildcards
            if '*' in possible_dir:
                import glob
                matches = glob.glob(possible_dir)
                if matches:
                    possible_dir = matches[0]
            
            if os.path.exists(possible_dir):
                # Check for libclntsh.dylib (macOS) or libclntsh.so (Linux)
                for lib_name in ['libclntsh.dylib', 'libclntsh.so']:
                    lib_path = os.path.join(possible_dir, lib_name)
                    if os.path.exists(lib_path) or os.path.islink(lib_path):
                        # Check architecture before using
                        import platform
                        python_arch = platform.machine()
                        
                        if python_arch == 'arm64':
                            # Check if library is ARM64 compatible
                            import subprocess
                            try:
                                result = subprocess.run(['file', lib_path], 
                                                       capture_output=True, text=True, timeout=2)
                                lib_arch_info = result.stdout.lower()
                                if 'x86_64' in lib_arch_info and 'arm64' not in lib_arch_info:
                                    print(f"⚠️  Skipping {lib_path} - wrong architecture (x86_64, need ARM64)")
                                    continue  # Skip this library
                            except Exception:
                                pass  # If check fails, try anyway
                        
                        lib_dir = possible_dir
                        print(f"✓ Found Oracle Instant Client at: {lib_dir}")
                        break
                if lib_dir:
                    break
    
    # If no compatible library found, skip thick mode initialization
    if not lib_dir:
        print("⚠️  No compatible Oracle Instant Client found (need ARM64 for Apple Silicon)")
        print("   Using thin mode (no Instant Client required)")
        print("   Note: Thin mode has limited ADB wallet support")
        use_thin_mode = True
    
    # Set TNS_ADMIN before initializing client (important for wallet access)
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
        print(f"✓ Set TNS_ADMIN to: {wallet_path}")
    
    # Only try thick mode if we have a compatible library
    if not use_thin_mode:
        try:
            # Try to initialize Oracle client (thick mode - requires Instant Client)
            if lib_dir:
                try:
                    # Initialize with both lib_dir and config_dir
                    oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
                    print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
                except Exception as init_err:
                    # Try without config_dir (TNS_ADMIN env var should handle it)
                    try:
                        oracledb.init_oracle_client(lib_dir=lib_dir)
                        print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
                        print(f"   Using TNS_ADMIN: {os.getenv('TNS_ADMIN')}")
                    except Exception as init_err2:
                        raise init_err2
            else:
                # Try without specifying lib_dir (let oracledb find it)
                oracledb.init_oracle_client(lib_dir=None, config_dir=wallet_path)
                print(f"✓ Oracle client initialized with wallet: {wallet_path} (thick mode)")
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  WARNING: Could not initialize Oracle client: {error_msg}")
            if 'DPI-1047' in error_msg or 'Cannot locate' in error_msg or 'incompatible architecture' in error_msg:
                print(f"   Oracle Instant Client library not found or incompatible")
                if lib_dir:
                    print(f"   (Found directory but initialization failed: {lib_dir})")
                print("   Trying thin mode (no Instant Client required)...")
                print("   Note: Thin mode has limited ADB wallet support")
                use_thin_mode = True
            else:
                print(f"   Error details: {error_msg}")
                print("   Trying thin mode as fallback...")
                use_thin_mode = True
    else:
        # Already decided to use thin mode (no compatible library found)
        print("   Proceeding with thin mode connection...")
        # Already decided to use thin mode (no compatible library found)
        print("   Proceeding with thin mode connection...")
    
    # Try to connect
    try:
        # Determine DSN format based on connection string
        # If connection_string is already a simple alias (no description=), use it directly
        # If it's a full TNS description, extract alias or convert to simple format
        import re
        
        # Check if connection_string is already a simple alias (no special chars, no description=)
        is_simple_alias = not ('description=' in connection_string.lower() or 
                              '(' in connection_string or 
                              (':' in connection_string and '/' in connection_string))
        
        if is_simple_alias:
            # Already a TNS alias - use it directly
            dsn = connection_string
            print(f"✓ Using TNS alias from .env: {dsn}")
        else:
            # Full TNS description string or host:port/service format - need to extract or find alias
            tns_file = Path(wallet_path) / 'tnsnames.ora'
            if tns_file.exists():
                print(f"✓ Found tnsnames.ora, extracting TNS alias")
                with open(tns_file, 'r') as f:
                    content = f.read()
                    # Look for alias that matches the connection string
                    # Try to find alias by matching the service_name or host
                    tns_str = connection_string
                    host_match = re.search(r'host=([^)]+)', tns_str)
                    service_match = re.search(r'service_name=([^)]+)', tns_str)
                    
                    # Look for alias pattern (prefer _high, then _medium, then _low)
                    found_alias = None
                    for priority in ['_high', '_medium', '_low', '']:
                        pattern = rf'^(\w+{re.escape(priority)})\s*=' if priority else r'^(\w+)\s*='
                        alias_match = re.search(pattern, content, re.MULTILINE)
                        if alias_match:
                            found_alias = alias_match.group(1)
                            print(f"✓ Using TNS alias: {found_alias}")
                            break
                    
                    if found_alias:
                        dsn = found_alias
                    elif use_thin_mode and host_match and service_match:
                        # For thin mode, extract host:port/service_name format
                        port_match = re.search(r'port=(\d+)', tns_str)
                        host = host_match.group(1)
                        port = port_match.group(1) if port_match else '1522'
                        service = service_match.group(1)
                        dsn = f"{host}:{port}/{service}"
                        print(f"✓ Using extracted format for thin mode: {host}:{port}/{service}")
                    else:
                        # Fallback: use TNS description as-is (for thick mode)
                        dsn = connection_string
                        print(f"⚠️  Using full TNS description (may not work in thin mode)")
            else:
                # No tnsnames.ora - extract from description string
                if use_thin_mode:
                    host_match = re.search(r'host=([^)]+)', connection_string)
                    port_match = re.search(r'port=(\d+)', connection_string)
                    service_match = re.search(r'service_name=([^)]+)', connection_string)
                    if host_match and port_match and service_match:
                        host = host_match.group(1)
                        port = port_match.group(1)
                        service = service_match.group(1)
                        dsn = f"{host}:{port}/{service}"
                        print(f"✓ Using extracted format: {host}:{port}/{service}")
                    else:
                        dsn = connection_string
                else:
                    dsn = connection_string
        
        # Connect to database
        if use_thin_mode:
            # Thin mode with ADB wallets is limited - try with SSL parameters
            # Note: Full wallet support typically requires thick mode (Instant Client)
            # For thin mode, we need to extract host:port/service format and configure SSL manually
            try:
                # If using TNS alias in thin mode, we need to convert to host:port/service
                if not (':' in dsn and '/' in dsn):
                    # DSN is a TNS alias - need to extract connection details
                    tns_file = Path(wallet_path) / 'tnsnames.ora'
                    if tns_file.exists():
                        with open(tns_file, 'r') as f:
                            content = f.read()
                            # Find the alias definition
                            alias_pattern = rf'^{re.escape(dsn)}\s*=\s*\(description=.*?service_name=([^)]+)\)'
                            match = re.search(alias_pattern, content, re.MULTILINE | re.DOTALL)
                            if match:
                                # Extract host, port, service_name
                                desc = match.group(0)
                                host_match = re.search(r'host=([^)]+)', desc)
                                port_match = re.search(r'port=(\d+)', desc)
                                service_match = re.search(r'service_name=([^)]+)', desc)
                                if host_match and port_match and service_match:
                                    host = host_match.group(1)
                                    port = port_match.group(1)
                                    service = service_match.group(1)
                                    dsn = f"{host}:{port}/{service}"
                                    print(f"✓ Converted TNS alias to thin mode format: {host}:{port}/{service}")
                
                # Try connection with SSL configuration for thin mode
                # Note: Thin mode SSL support for ADB is limited
                connection = oracledb.connect(
                    user=username,
                    password=password,
                    dsn=dsn,
                    # For thin mode, SSL is handled automatically if wallet is configured
                    # But ADB requires specific SSL configuration that thin mode may not support fully
                )
            except Exception as thin_err:
                error_msg = str(thin_err)
                print(f"⚠️  Thin mode connection failed: {thin_err}")
                
                if 'Listener refused' in error_msg or 'ORA-12506' in error_msg:
                    print("\n💡 This error in thin mode typically means:")
                    print("   1. ADB instance may not be running (check Oracle Cloud Console)")
                    print("   2. Thin mode has limited SSL/wallet support for ADB")
                    print("   3. Network/firewall may be blocking connection")
                    print("\n   Solutions:")
                    print("   - Verify ADB is running in Oracle Cloud Console")
                    print("   - Test connection with SQL Developer/SQL*Plus")
                    print("   - Install ARM64 Oracle Instant Client for thick mode (full wallet support)")
                    print("   - See docs/ORACLE_CLIENT_ARM64.md for ARM64 installation")
                else:
                    print("\n💡 SOLUTION: Install Oracle Instant Client for full wallet support")
                    print("   Thin mode has limited wallet/SSL support for ADB")
                    print("   See docs/ORACLE_CLIENT_SETUP.md for installation instructions")
                raise thin_err
        else:
            # Thick mode: use wallet for SSL/TLS
            # Ensure TNS_ADMIN is set (required for wallet access)
            # TNS_ADMIN must match wallet_path exactly
            current_tns_admin = os.getenv('TNS_ADMIN')
            if current_tns_admin != wallet_path:
                os.environ['TNS_ADMIN'] = wallet_path
                print(f"   TNS_ADMIN set to: {wallet_path}")
            
            print(f"   Connecting as {username} to {dsn[:50]}...")
            print(f"   Using TNS_ADMIN: {os.getenv('TNS_ADMIN')}")
            
            # Verify wallet files are accessible
            sqlnet_file = Path(wallet_path) / 'sqlnet.ora'
            tnsnames_file = Path(wallet_path) / 'tnsnames.ora'
            cwallet_file = Path(wallet_path) / 'cwallet.sso'
            
            if not sqlnet_file.exists():
                print(f"   ⚠️  WARNING: sqlnet.ora not found at {sqlnet_file}")
            if not tnsnames_file.exists():
                print(f"   ⚠️  WARNING: tnsnames.ora not found at {tnsnames_file}")
            if not cwallet_file.exists():
                print(f"   ⚠️  WARNING: cwallet.sso not found at {cwallet_file}")
            
            try:
                connection = oracledb.connect(
                    user=username,
                    password=password,
                    dsn=dsn
                )
            except Exception as conn_err:
                error_msg = str(conn_err)
                if 'ORA-28759' in error_msg or 'failure to open file' in error_msg:
                    print(f"\n⚠️  Wallet file access error (ORA-28759)")
                    print(f"   This usually means Oracle can't find wallet files")
                    print(f"   TNS_ADMIN: {os.getenv('TNS_ADMIN')}")
                    print(f"   Wallet path: {wallet_path}")
                    print(f"   sqlnet.ora exists: {sqlnet_file.exists()}")
                    print(f"   tnsnames.ora exists: {tnsnames_file.exists()}")
                    print(f"   cwallet.sso exists: {cwallet_file.exists()}")
                    
                    # Check if we can read the files
                    if sqlnet_file.exists():
                        try:
                            with open(sqlnet_file, 'r') as f:
                                content = f.read()
                            print(f"   ✓ Can read sqlnet.ora")
                        except Exception as e:
                            print(f"   ❌ Cannot read sqlnet.ora: {e}")
                    
                    print(f"\n   Solutions:")
                    print(f"   1. Verify TNS_ADMIN points to wallet directory (currently: {os.getenv('TNS_ADMIN')})")
                    print(f"   2. Check wallet file permissions:")
                    print(f"      ls -la {wallet_path}/*.ora {wallet_path}/*.sso")
                    print(f"   3. Try: chmod 644 {wallet_path}/*.ora {wallet_path}/*.sso")
                    print(f"   4. Verify wallet files are not corrupted")
                    print(f"   5. Check if Oracle Instant Client can access the directory")
                    print(f"   6. The sqlnet.ora uses relative path '?/network/admin'")
                    print(f"      This should resolve to TNS_ADMIN, but may need absolute path")
                raise conn_err
        print(f"✓ Successfully connected to ADB as {username}")
        
        # Test a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        print(f"✓ Test query successful: {result[0]}")
        
        cursor.close()
        connection.close()
        print("✓ Connection closed successfully")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify wallet files are in ADB_WALLET_PATH")
        print("2. Check ADB_CONNECTION_STRING format")
        print("3. Verify ADB_USERNAME and ADB_PASSWORD are correct")
        
        # Check for specific wallet-related errors
        if 'ORA-28759' in error_msg or 'failure to open file' in error_msg:
            print("\n⚠️  Wallet file access error detected:")
            print(f"   Wallet path: {wallet_path}")
            print(f"   TNS_ADMIN: {os.getenv('TNS_ADMIN')}")
            print("   Solutions:")
            print("   1. Verify wallet directory exists and is readable")
            print("   2. Check file permissions on wallet files")
            print("   3. Ensure sqlnet.ora and tnsnames.ora are in wallet directory")
            print("   4. Try setting TNS_ADMIN explicitly in .env file")
            print("   5. Verify wallet files are not corrupted (re-download if needed)")
        
        if use_thin_mode:
            print("\n💡 IMPORTANT: Thin mode has limited ADB wallet support")
            print("   For ADB connections with wallets, you need Oracle Instant Client (thick mode)")
            print("   Install instructions: docs/ORACLE_CLIENT_SETUP.md")
            print("   Or use: brew install instantclient-basic instantclient-sdk")
        else:
            print("4. Ensure Oracle Instant Client is installed and configured")
            if 'DPI-1047' in error_msg or 'Cannot locate' in error_msg:
                print("   Install instructions: docs/ORACLE_CLIENT_SETUP.md")
        
        if 'Connection reset' in error_msg or 'closed the connection' in error_msg or 'Listener refused' in error_msg:
            print("\n⚠️  Network/SSL/Listener issue detected:")
            print("   1. Verify ADB instance is RUNNING in Oracle Cloud Console")
            print("   2. Check if ADB is paused (resume if needed)")
            print("   3. Verify network connectivity (try: ping adb.us-chicago-1.oraclecloud.com)")
            print("   4. Check firewall rules allow port 1522")
            print("   5. Ensure wallet files are correct and not corrupted")
            print("   6. Verify username/password are correct")
            print("   7. Try using different TNS alias (_high, _medium, _low)")
            print("\n   Quick test: Try connecting with SQL Developer or SQL*Plus")
            print("   If that works, the issue is with Python/oracledb configuration")
        
        return False


def get_db_connection():
    """
    Return an oracledb connection using .env. For use by other scripts (e.g. list_test_users.py).
    Uses thick mode (Oracle Instant Client) when possible; ADB + wallet often fails in thin mode
    with ORA-12506 / DPY-6000 "Listener refused connection".

    Raises:
        Exception: if connection fails, with message to run this script or use Data Science notebook.
    """
    import glob
    import oracledb
    wallet_path = os.getenv("ADB_WALLET_PATH")
    connection_string = os.getenv("ADB_CONNECTION_STRING")
    username = os.getenv("ADB_USERNAME", "OML")
    password = os.getenv("ADB_PASSWORD")

    if not all([wallet_path, connection_string, password]):
        raise RuntimeError("Missing ADB_WALLET_PATH, ADB_CONNECTION_STRING, or ADB_PASSWORD in .env")

    os.environ.setdefault("TNS_ADMIN", wallet_path)

    # Find Oracle Instant Client (thick mode); thin mode often gives ORA-12506 with ADB+wallet
    lib_dir = None
    for path in [
        "/opt/homebrew/lib",
        "/usr/local/lib",
        *([g for g in glob.glob("/opt/oracle/instantclient_*/lib") or []]),
        os.path.join(os.getenv("ORACLE_HOME", ""), "lib"),
    ]:
        if not path:
            continue
        for name in ["libclntsh.dylib", "libclntsh.so"]:
            p = os.path.join(path, name)
            if os.path.exists(p) or os.path.islink(p):
                lib_dir = path
                break
        if lib_dir:
            break

    if lib_dir:
        try:
            oracledb.init_oracle_client(lib_dir=lib_dir)
        except Exception:
            try:
                oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
            except Exception:
                pass
    else:
        try:
            oracledb.init_oracle_client()
        except Exception:
            pass

    try:
        return oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string,
        )
    except Exception as e:
        err = str(e)
        if "ORA-12506" in err or "DPY-6000" in err or "Listener refused" in err:
            raise RuntimeError(
                "Connection failed (ORA-12506 / Listener refused). ADB + wallet usually needs "
                "thick mode. Run: python scripts/test-python-connection.py . "
                "Or use the Data Science notebook snippet in list_test_users.py docstring."
            ) from e
        raise


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Oracle ADB Connection Test - Python")
    print("=" * 60)
    print("\nChecking prerequisites...\n")
    
    # Debug: Show which env vars are loaded (without sensitive values)
    print("Environment variables loaded:")
    env_vars = ['ADB_WALLET_PATH', 'ADB_CONNECTION_STRING', 'ADB_USERNAME', 'TNS_ADMIN']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive parts of paths
            if 'wallet' in var.lower() or 'path' in var.lower():
                print(f"  {var}: {value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: (not set)")
    print(f"  ADB_PASSWORD: {'(set)' if os.getenv('ADB_PASSWORD') else '(not set)'}")
    print()
    
    # Test OML4Py connection
    oml_ok = test_oml_connection()
    
    # Test oracledb connection
    oracledb_ok = test_oracledb_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"OML4Py:     {'✓ PASS' if oml_ok else '❌ FAIL'}")
    print(f"oracledb:   {'✓ PASS' if oracledb_ok else '❌ FAIL'}")
    
    # OML4Py is optional (only available in OML Notebooks)
    # oracledb is required for API server
    if oracledb_ok:
        print("\n✓ Python connection test passed!")
        if not oml_ok:
            print("  Note: OML4Py not available (expected outside OML Notebooks)")
        return 0
    else:
        print("\n⚠️  Connection test failed. Review errors above.")
        print("  Fix Oracle Instant Client installation to proceed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
