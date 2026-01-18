#!/usr/bin/env python3
"""
Check Affinity Card Count
Quick script to check how many users have AFFINITY_CARD in ADMIN.USERS
"""

import os
import sys
from pathlib import Path
import glob

# Find project root
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

def initialize_oracle_client():
    """Initialize Oracle client"""
    try:
        import oracledb
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        sys.exit(1)
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path or not os.path.exists(wallet_path):
        print("❌ ERROR: ADB_WALLET_PATH not set or invalid")
        sys.exit(1)
    
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    try:
        oracle_opt_paths = [
            '/opt/oracle/instantclient_*/lib',
            '/opt/oracle/instantclient_*',
        ]
        
        lib_dir = None
        for pattern in oracle_opt_paths:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.isdir(match):
                    lib_dir = match
                    break
            if lib_dir:
                break
        
        if lib_dir:
            try:
                oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
            except Exception:
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                except Exception:
                    oracledb.init_oracle_client(config_dir=wallet_path)
        else:
            oracledb.init_oracle_client(config_dir=wallet_path)
    except Exception:
        pass
    
    return oracledb

def get_connection():
    """Get database connection"""
    oracledb = initialize_oracle_client()
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not connection_string or not password:
        print("❌ ERROR: ADB connection credentials not set")
        sys.exit(1)
    
    try:
        return oracledb.connect(user=username, password=password, dsn=connection_string)
    except Exception as e:
        print(f"❌ ERROR: Failed to connect: {e}")
        sys.exit(1)

def check_affinity_card(connection):
    """Check affinity card count"""
    cursor = connection.cursor()
    
    # Check total users
    cursor.execute("SELECT COUNT(*) FROM ADMIN.USERS")
    total_users = cursor.fetchone()[0]
    
    # Check users with affinity card
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ADMIN.USERS 
        WHERE AFFINITY_CARD = 1
    """)
    with_card = cursor.fetchone()[0]
    
    # Check users without affinity card
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ADMIN.USERS 
        WHERE AFFINITY_CARD = 0 OR AFFINITY_CARD IS NULL
    """)
    without_card = cursor.fetchone()[0]
    
    # Check data type and sample values
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT AFFINITY_CARD) AS distinct_values,
            MIN(AFFINITY_CARD) AS min_val,
            MAX(AFFINITY_CARD) AS max_val,
            COUNT(CASE WHEN AFFINITY_CARD IS NULL THEN 1 END) AS null_count
        FROM ADMIN.USERS
    """)
    stats = cursor.fetchone()
    distinct_vals, min_val, max_val, null_count = stats
    
    print(f"Total users in ADMIN.USERS: {total_users:,}")
    print(f"Users with AFFINITY_CARD = 1: {with_card:,} ({with_card/total_users*100:.2f}%)")
    print(f"Users with AFFINITY_CARD = 0 or NULL: {without_card:,}")
    print(f"\nAFFINITY_CARD statistics:")
    print(f"  Distinct values: {distinct_vals}")
    print(f"  Min value: {min_val}")
    print(f"  Max value: {max_val}")
    print(f"  NULL count: {null_count}")
    
    cursor.close()
    
    return with_card

def main():
    """Main function"""
    connection = get_connection()
    
    try:
        count = check_affinity_card(connection)
        print(f"\n✓ Users with affinity card: {count:,}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        connection.close()

if __name__ == '__main__':
    main()
