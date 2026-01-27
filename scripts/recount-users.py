#!/usr/bin/env python3
"""
Comprehensive recount of users in the database
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

def recount_users():
    """Do a comprehensive user count"""
    
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
        print("COMPREHENSIVE USER COUNT ANALYSIS")
        print("=" * 80)
        
        # Check total rows in view
        print("\n" + "-" * 80)
        print("1. TOTAL ROWS IN ADMIN.ORDERS_PROFILE_V")
        print("-" * 80)
        cursor.execute("SELECT COUNT(*) FROM ADMIN.ORDERS_PROFILE_V")
        total_rows = cursor.fetchone()[0]
        print(f"Total rows: {total_rows:,}")
        
        # Check rows with NULL USER_ID
        print("\n" + "-" * 80)
        print("2. USER_ID NULL CHECK")
        print("-" * 80)
        cursor.execute("SELECT COUNT(*) FROM ADMIN.ORDERS_PROFILE_V WHERE USER_ID IS NULL")
        null_user_ids = cursor.fetchone()[0]
        print(f"Rows with NULL USER_ID: {null_user_ids:,}")
        
        cursor.execute("SELECT COUNT(*) FROM ADMIN.ORDERS_PROFILE_V WHERE USER_ID IS NOT NULL")
        non_null_user_ids = cursor.fetchone()[0]
        print(f"Rows with non-NULL USER_ID: {non_null_user_ids:,}")
        
        # Count distinct users (excluding NULLs)
        print("\n" + "-" * 80)
        print("3. DISTINCT USER COUNT (excluding NULLs)")
        print("-" * 80)
        cursor.execute("""
            SELECT COUNT(DISTINCT USER_ID) 
            FROM ADMIN.ORDERS_PROFILE_V 
            WHERE USER_ID IS NOT NULL
        """)
        distinct_users_no_null = cursor.fetchone()[0]
        print(f"Distinct users (USER_ID IS NOT NULL): {distinct_users_no_null:,}")
        
        # Count ALL distinct users (including NULLs)
        print("\n" + "-" * 80)
        print("4. DISTINCT USER COUNT (including NULLs as a group)")
        print("-" * 80)
        cursor.execute("SELECT COUNT(DISTINCT USER_ID) FROM ADMIN.ORDERS_PROFILE_V")
        distinct_users_with_null = cursor.fetchone()[0]
        print(f"Distinct users (all): {distinct_users_with_null:,}")
        
        if null_user_ids > 0:
            print(f"\nNote: Oracle counts NULL as one distinct value if present")
            print(f"Actual users: {distinct_users_with_null:,} (includes NULL group)")
            print(f"Users with IDs: {distinct_users_no_null:,}")
        
        # Check for any user-related columns
        print("\n" + "-" * 80)
        print("5. CHECKING FOR OTHER USER-RELATED COLUMNS")
        print("-" * 80)
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM ALL_TAB_COLUMNS 
            WHERE TABLE_NAME = 'ORDERS_PROFILE_V' 
            AND OWNER = 'ADMIN'
            AND COLUMN_NAME LIKE '%USER%'
            ORDER BY COLUMN_NAME
        """)
        user_columns = cursor.fetchall()
        print(f"User-related columns found:")
        for col in user_columns:
            print(f"  - {col[0]}")
            # Get distinct count for each user column
            cursor.execute(f"""
                SELECT COUNT(DISTINCT {col[0]})
                FROM ADMIN.ORDERS_PROFILE_V
                WHERE {col[0]} IS NOT NULL
            """)
            count = cursor.fetchone()[0]
            print(f"    Distinct non-NULL values: {count:,}")
        
        # Sample some USER_IDs to verify
        print("\n" + "-" * 80)
        print("6. SAMPLE USER_IDs (first 20)")
        print("-" * 80)
        cursor.execute("""
            SELECT DISTINCT USER_ID
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
            ORDER BY USER_ID
            FETCH FIRST 20 ROWS ONLY
        """)
        sample_users = cursor.fetchall()
        for i, (uid,) in enumerate(sample_users, 1):
            print(f"{i:2d}. {uid}")
        
        # Final summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"\nTotal distinct users with USER_ID: {distinct_users_no_null:,}")
        if null_user_ids > 0:
            print(f"Rows with NULL USER_ID: {null_user_ids:,} (cannot be used for recommendations)")
        
        if distinct_users_no_null < 5000:
            print(f"\n⚠️  Found {distinct_users_no_null:,} users, less than expected ~5,000")
            print(f"   Possible reasons:")
            print(f"   1. Data was filtered or archived")
            print(f"   2. View has WHERE conditions that exclude some users")
            print(f"   3. Users exist in another table/view")
            print(f"   4. Expected count was approximate")
        else:
            print(f"\n✓ Found {distinct_users_no_null:,} users (close to expected ~5,000)")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    recount_users()
