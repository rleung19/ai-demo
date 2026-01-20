#!/usr/bin/env python3
"""
Examine ADMIN.USERS table structure to understand USER_ID mapping
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'
load_dotenv(dotenv_path=env_file)

import oracledb

def examine_users_table():
    """Connect to ADB and examine ADMIN.USERS table"""
    
    print("=" * 60)
    print("Examining ADMIN.USERS Table")
    print("=" * 60)
    
    # Get connection parameters
    wallet_path = os.getenv('ADB_WALLET_PATH')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not all([wallet_path, connection_string, password]):
        print("❌ ERROR: Missing required environment variables")
        print("   Required: ADB_WALLET_PATH, ADB_CONNECTION_STRING, ADB_PASSWORD")
        return False
    
    # Set TNS_ADMIN
    os.environ['TNS_ADMIN'] = wallet_path
    
    # Initialize Oracle client (same logic as test-python-connection.py)
    import platform
    import subprocess
    import glob
    
    python_arch = platform.machine()
    lib_dir = None
    use_thin_mode = False
    
    # Try to find ARM64 Instant Client
    if python_arch == 'arm64':
        oracle_opt_paths = [
            '/opt/oracle/instantclient_*/lib',
            '/opt/oracle/instantclient_*',
        ]
        for pattern in oracle_opt_paths:
            matches = glob.glob(pattern)
            for match in matches:
                for lib_name in ['libclntsh.dylib', 'libclntsh.so']:
                    lib_path = os.path.join(match, lib_name) if os.path.isdir(match) else match
                    if os.path.exists(lib_path) or os.path.islink(lib_path):
                        try:
                            result = subprocess.run(['file', lib_path], 
                                                   capture_output=True, text=True, timeout=2)
                            lib_arch_info = result.stdout.lower()
                            if 'arm64' in lib_arch_info and 'x86_64' not in lib_arch_info:
                                lib_dir = os.path.dirname(lib_path) if os.path.isfile(lib_path) else match
                                break
                        except Exception:
                            pass
                if lib_dir:
                    break
            if lib_dir:
                break
    
    # Set TNS_ADMIN before initializing client
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    # Only try thick mode if we have a compatible library
    if lib_dir and not use_thin_mode:
        try:
            oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
            print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
        except Exception as e:
            print(f"⚠️  WARNING: Could not initialize Oracle client: {e}")
            print("   Trying thin mode...")
            use_thin_mode = True
    else:
        print("⚠️  No compatible Oracle Instant Client found, using thin mode")
        use_thin_mode = True
    
    # Connect to database
    try:
        print(f"\n🔌 Connecting to ADB as {username}...")
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        print(f"✓ Connected successfully")
        
        cursor = connection.cursor()
        
        # Check if we can access ADMIN.USERS
        print(f"\n📊 Checking ADMIN.USERS table access...")
        
        # Get table structure
        print(f"\n📋 Table Structure:")
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                data_length,
                data_precision,
                data_scale,
                nullable
            FROM all_tab_columns
            WHERE owner = 'ADMIN' 
              AND table_name = 'USERS'
            ORDER BY column_id
        """)
        
        columns = cursor.fetchall()
        if not columns:
            print("   ❌ ADMIN.USERS table not found or no access")
            print("   Trying alternative query...")
            
            # Try to get table info another way
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ADMIN.USERS
            """)
            count = cursor.fetchone()[0]
            print(f"   ✓ Can access ADMIN.USERS (found {count:,} rows)")
            
            # Get column names from a sample query
            cursor.execute("SELECT * FROM ADMIN.USERS WHERE ROWNUM <= 1")
            col_names = [desc[0] for desc in cursor.description]
            print(f"\n   Columns found: {', '.join(col_names)}")
        else:
            print(f"   Found {len(columns)} columns:")
            for col in columns:
                col_name, data_type, data_length, data_precision, data_scale, nullable = col
                type_str = data_type
                if data_precision:
                    type_str += f"({data_precision}"
                    if data_scale:
                        type_str += f",{data_scale}"
                    type_str += ")"
                elif data_length:
                    type_str += f"({data_length})"
                
                null_str = "NULL" if nullable == 'Y' else "NOT NULL"
                print(f"      {col_name:30s} | {type_str:20s} | {null_str}")
        
        # Get row count
        print(f"\n📊 Row Count:")
        cursor.execute("SELECT COUNT(*) FROM ADMIN.USERS")
        total_rows = cursor.fetchone()[0]
        print(f"   Total users: {total_rows:,}")
        
        # Get active users count
        try:
            cursor.execute("SELECT COUNT(*) FROM ADMIN.USERS WHERE IS_ACTIVE = 1")
            active_rows = cursor.fetchone()[0]
            print(f"   Active users: {active_rows:,}")
        except Exception:
            print(f"   ⚠️  Could not count active users (IS_ACTIVE column may not exist)")
        
        # Examine USER_ID column
        print(f"\n🔑 USER_ID Column Analysis:")
        try:
            # Check if ID column exists (common name)
            cursor.execute("""
                SELECT 
                    MIN(ID) as min_id,
                    MAX(ID) as max_id,
                    COUNT(DISTINCT ID) as unique_ids,
                    COUNT(*) as total_rows
                FROM ADMIN.USERS
            """)
            id_stats = cursor.fetchone()
            min_id, max_id, unique_ids, total_rows = id_stats
            print(f"   Column name: ID")
            print(f"   Min ID: {min_id}")
            print(f"   Max ID: {max_id}")
            print(f"   Unique IDs: {unique_ids:,}")
            print(f"   Total rows: {total_rows:,}")
            
            if unique_ids == total_rows:
                print(f"   ✅ All IDs are unique")
            else:
                print(f"   ⚠️  WARNING: Duplicate IDs found!")
            
            # Sample some IDs
            cursor.execute("SELECT ID FROM ADMIN.USERS WHERE ROWNUM <= 10 ORDER BY ID")
            sample_ids = [row[0] for row in cursor.fetchall()]
            print(f"   Sample IDs: {sample_ids}")
            
        except Exception as e:
            print(f"   ⚠️  Could not analyze ID column: {e}")
            print(f"   Trying alternative column names...")
            
            # Try common alternative names
            for col_name in ['USER_ID', 'CUSTOMER_ID', 'CUSTOMERID']:
                try:
                    cursor.execute(f"""
                        SELECT 
                            MIN({col_name}) as min_id,
                            MAX({col_name}) as max_id,
                            COUNT(DISTINCT {col_name}) as unique_ids
                        FROM ADMIN.USERS
                    """)
                    stats = cursor.fetchone()
                    if stats and stats[0] is not None:
                        print(f"   Found column: {col_name}")
                        print(f"   Min: {stats[0]}, Max: {stats[1]}, Unique: {stats[2]:,}")
                        break
                except Exception:
                    continue
        
        # Sample data
        print(f"\n📄 Sample Data (first 5 rows):")
        cursor.execute("SELECT * FROM ADMIN.USERS WHERE ROWNUM <= 5")
        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Print header
        print(f"   {' | '.join(col_names[:8])}")  # First 8 columns
        print(f"   {'-' * 80}")
        
        # Print rows
        for row in rows:
            print(f"   {' | '.join(str(val)[:15] if val is not None else 'NULL' for val in row[:8])}")
        
        # Check for other relevant columns
        print(f"\n🔍 Checking for relevant columns:")
        relevant_keywords = ['email', 'name', 'created', 'active', 'status']
        for keyword in relevant_keywords:
            matching_cols = [col[0] for col in columns if keyword.lower() in col[0].lower()]
            if matching_cols:
                print(f"   {keyword}: {', '.join(matching_cols)}")
        
        cursor.close()
        connection.close()
        print(f"\n✓ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = examine_users_table()
    sys.exit(0 if success else 1)
