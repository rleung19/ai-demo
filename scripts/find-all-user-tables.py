#!/usr/bin/env python3
"""
Find all tables/views that contain user data
"""

import os
import sys
from pathlib import Path

# Find project root and load .env
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    print("❌ python-dotenv not installed")
    sys.exit(1)

try:
    import oracledb
except ImportError:
    print("❌ oracledb not installed")
    sys.exit(1)

def find_user_tables():
    """Find all tables with user data"""
    
    # Get connection parameters
    wallet_path = os.getenv('ADB_WALLET_PATH')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    os.environ['TNS_ADMIN'] = wallet_path
    
    try:
        # Initialize client
        import glob
        lib_dir = None
        for pattern in ['/opt/oracle/instantclient_*', '/opt/homebrew/lib']:
            matches = glob.glob(pattern) if '*' in pattern else [pattern]
            for match in matches:
                if os.path.exists(match):
                    for lib_name in ['libclntsh.dylib', 'libclntsh.so']:
                        if os.path.exists(os.path.join(match, lib_name)):
                            lib_dir = match
                            break
                if lib_dir:
                    break
            if lib_dir:
                break
        
        if lib_dir:
            oracledb.init_oracle_client(lib_dir=lib_dir)
        
        # Connect
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        print("✓ Connected to database\n")
        
        cursor = connection.cursor()
        
        print("=" * 80)
        print("FINDING ALL USER-RELATED TABLES/VIEWS IN ADMIN SCHEMA")
        print("=" * 80)
        
        # Find tables/views with USER in the name
        cursor.execute("""
            SELECT TABLE_NAME, 'TABLE' as OBJECT_TYPE
            FROM ALL_TABLES
            WHERE OWNER = 'ADMIN'
            AND (TABLE_NAME LIKE '%USER%' OR TABLE_NAME LIKE '%CUSTOMER%' OR TABLE_NAME LIKE '%CUST%')
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        
        cursor.execute("""
            SELECT VIEW_NAME, 'VIEW' as OBJECT_TYPE
            FROM ALL_VIEWS
            WHERE OWNER = 'ADMIN'
            AND (VIEW_NAME LIKE '%USER%' OR VIEW_NAME LIKE '%CUSTOMER%' OR VIEW_NAME LIKE '%CUST%')
            ORDER BY VIEW_NAME
        """)
        views = cursor.fetchall()
        
        all_objects = tables + views
        
        print(f"\nFound {len(all_objects)} user/customer-related objects:\n")
        
        for obj_name, obj_type in all_objects:
            print(f"\n{'-' * 80}")
            print(f"{obj_name} ({obj_type})")
            print(f"{'-' * 80}")
            
            # Try to get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM ADMIN.{obj_name}")
                row_count = cursor.fetchone()[0]
                print(f"Total rows: {row_count:,}")
                
                # Check for columns with USER or CUSTOMER
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE
                    FROM ALL_TAB_COLUMNS
                    WHERE TABLE_NAME = :table_name
                    AND OWNER = 'ADMIN'
                    AND (COLUMN_NAME LIKE '%USER%' OR COLUMN_NAME LIKE '%CUSTOMER%' OR COLUMN_NAME LIKE '%CUST%')
                    ORDER BY COLUMN_NAME
                """, table_name=obj_name)
                user_cols = cursor.fetchall()
                
                if user_cols:
                    print(f"User-related columns:")
                    for col_name, data_type in user_cols:
                        # Get distinct count
                        try:
                            cursor.execute(f"""
                                SELECT COUNT(DISTINCT {col_name})
                                FROM ADMIN.{obj_name}
                                WHERE {col_name} IS NOT NULL
                            """)
                            distinct_count = cursor.fetchone()[0]
                            print(f"  - {col_name} ({data_type}): {distinct_count:,} distinct values")
                        except Exception as e:
                            print(f"  - {col_name} ({data_type}): [error counting: {e}]")
                
            except Exception as e:
                print(f"Error querying: {e}")
        
        # Now check if there's a base CUSTOMERS or USERS table
        print(f"\n{'=' * 80}")
        print(f"CHECKING FOR BASE USER/CUSTOMER TABLES")
        print(f"{'=' * 80}")
        
        for table_name in ['CUSTOMERS', 'USERS', 'CUSTOMER', 'USER']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM ADMIN.{table_name}")
                count = cursor.fetchone()[0]
                print(f"\n✓ ADMIN.{table_name} exists!")
                print(f"  Total rows: {count:,}")
                
                # Check for ID column
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE
                    FROM ALL_TAB_COLUMNS
                    WHERE TABLE_NAME = :table_name
                    AND OWNER = 'ADMIN'
                    AND (COLUMN_NAME LIKE '%ID' OR COLUMN_NAME = 'USER_ID' OR COLUMN_NAME = 'CUSTOMER_ID')
                    ORDER BY COLUMN_NAME
                """, table_name=table_name)
                id_cols = cursor.fetchall()
                
                if id_cols:
                    print(f"  ID columns:")
                    for col_name, data_type in id_cols:
                        cursor.execute(f"""
                            SELECT COUNT(DISTINCT {col_name})
                            FROM ADMIN.{table_name}
                            WHERE {col_name} IS NOT NULL
                        """)
                        distinct_count = cursor.fetchone()[0]
                        print(f"    - {col_name}: {distinct_count:,} distinct values")
                
            except Exception:
                # Table doesn't exist, skip
                pass
        
        # Check view definition
        print(f"\n{'=' * 80}")
        print(f"CHECKING ORDERS_PROFILE_V DEFINITION")
        print(f"{'=' * 80}")
        
        try:
            cursor.execute("""
                SELECT TEXT
                FROM ALL_VIEWS
                WHERE OWNER = 'ADMIN'
                AND VIEW_NAME = 'ORDERS_PROFILE_V'
            """)
            view_def = cursor.fetchone()
            if view_def:
                print(f"\nView definition (first 2000 chars):")
                print(view_def[0][:2000])
                if len(view_def[0]) > 2000:
                    print("... [truncated]")
        except Exception as e:
            print(f"Could not retrieve view definition: {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    find_user_tables()
