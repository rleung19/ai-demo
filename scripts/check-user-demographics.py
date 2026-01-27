#!/usr/bin/env python3
"""
Check user demographics completeness in the database
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
    else:
        print(f"❌ .env file not found at {env_file}")
        sys.exit(1)
except ImportError:
    print("❌ python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    import oracledb
except ImportError:
    print("❌ oracledb not installed. Run: pip install oracledb")
    sys.exit(1)

def check_demographics():
    """Check demographics data completeness"""
    
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
        print("USER DEMOGRAPHICS ANALYSIS")
        print("=" * 80)
        
        # Total distinct users
        cursor.execute("""
            SELECT COUNT(DISTINCT USER_ID) 
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
        """)
        total_users = cursor.fetchone()[0]
        print(f"\nTotal distinct users: {total_users:,}")
        
        # Demographics fields from the notebook
        demographics_fields = [
            'GENDER',
            'CUST_YEAR_OF_BIRTH',
            'CUST_INCOME_LEVEL',
            'EDUCATION',
            'OCCUPATION',
            'HOUSEHOLD_SIZE',
            'CUST_MARITAL_STATUS',
            'CUST_CITY',
            'CUST_STATE_PROVINCE'
        ]
        
        print("\n" + "-" * 80)
        print("DEMOGRAPHICS FIELD COMPLETENESS")
        print("-" * 80)
        
        for field in demographics_fields:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT USER_ID)
                FROM ADMIN.ORDERS_PROFILE_V
                WHERE USER_ID IS NOT NULL
                AND {field} IS NOT NULL
            """)
            users_with_field = cursor.fetchone()[0]
            percentage = (users_with_field / total_users * 100) if total_users > 0 else 0
            status = "✓" if percentage > 90 else "⚠️" if percentage > 50 else "❌"
            print(f"{status} {field:25s}: {users_with_field:5,} / {total_users:,} users ({percentage:5.1f}%)")
        
        # Check users with ALL demographics fields populated
        print("\n" + "-" * 80)
        print("COMPLETE DEMOGRAPHICS PROFILES")
        print("-" * 80)
        
        all_fields_condition = " AND ".join([f"{field} IS NOT NULL" for field in demographics_fields])
        cursor.execute(f"""
            SELECT COUNT(DISTINCT USER_ID)
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
            AND {all_fields_condition}
        """)
        users_with_all_demographics = cursor.fetchone()[0]
        percentage = (users_with_all_demographics / total_users * 100) if total_users > 0 else 0
        
        print(f"Users with ALL demographics fields: {users_with_all_demographics:,} / {total_users:,} ({percentage:.1f}%)")
        
        if percentage < 100:
            users_without_complete = total_users - users_with_all_demographics
            print(f"\n⚠️  {users_without_complete:,} users ({100-percentage:.1f}%) are missing some demographics")
        else:
            print(f"\n✓ All users have complete demographics!")
        
        # Sample some users with and without demographics
        print("\n" + "-" * 80)
        print("SAMPLE DATA")
        print("-" * 80)
        
        # Users WITH complete demographics
        cursor.execute(f"""
            SELECT DISTINCT USER_ID, GENDER, CUST_YEAR_OF_BIRTH, CUST_INCOME_LEVEL, EDUCATION
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
            AND {all_fields_condition}
            AND ROWNUM <= 5
        """)
        print("\nSample users WITH complete demographics:")
        for row in cursor.fetchall():
            print(f"  User {row[0]}: {row[1]}, born {row[2]}, {row[3]}, {row[4]}")
        
        # Users WITHOUT complete demographics (if any)
        any_null_condition = " OR ".join([f"{field} IS NULL" for field in demographics_fields])
        cursor.execute(f"""
            SELECT DISTINCT USER_ID, GENDER, CUST_YEAR_OF_BIRTH, CUST_INCOME_LEVEL, EDUCATION
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
            AND ({any_null_condition})
            AND ROWNUM <= 5
        """)
        results = cursor.fetchall()
        if results:
            print("\nSample users WITHOUT complete demographics:")
            for row in results:
                print(f"  User {row[0]}: Gender={row[1]}, Born={row[2]}, Income={row[3]}, Education={row[4]}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY FOR RECOMMENDER MODEL")
        print("=" * 80)
        print(f"\nTotal users available: {total_users:,}")
        print(f"Users with complete demographics: {users_with_all_demographics:,} ({percentage:.1f}%)")
        
        if users_with_all_demographics < total_users:
            print(f"\n⚠️  COLD START ISSUE:")
            print(f"   - {users_with_all_demographics:,} users can get collaborative filtering recommendations")
            print(f"   - {total_users - users_with_all_demographics:,} users have incomplete demographics")
            print(f"\n   For users without full demographics, the model will:")
            print(f"   - Return empty recommendations (as currently implemented)")
            print(f"   - OR need a fallback strategy (popularity-based, content-based, etc.)")
        else:
            print(f"\n✓ All users have complete demographics!")
            print(f"   Model can make recommendations for all users after retraining.")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_demographics()
