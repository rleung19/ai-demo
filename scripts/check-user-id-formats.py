#!/usr/bin/env python3
"""
Check the different USER_ID formats in the database
"""

import os
import sys
from pathlib import Path
import re

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

def check_user_id_formats():
    """Analyze USER_ID formats"""
    
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
        print("USER_ID FORMAT ANALYSIS")
        print("=" * 80)
        
        # Get sample of all distinct user IDs
        cursor.execute("""
            SELECT DISTINCT USER_ID
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
            ORDER BY USER_ID
        """)
        
        all_user_ids = [row[0] for row in cursor.fetchall()]
        total_users = len(all_user_ids)
        
        print(f"\nTotal distinct users: {total_users:,}\n")
        
        # Categorize user IDs by format
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        numeric_pattern = re.compile(r'^\d+$')
        
        uuid_users = []
        numeric_users = []
        other_users = []
        
        for user_id in all_user_ids:
            user_id_str = str(user_id)
            if uuid_pattern.match(user_id_str):
                uuid_users.append(user_id_str)
            elif numeric_pattern.match(user_id_str):
                numeric_users.append(user_id_str)
            else:
                other_users.append(user_id_str)
        
        print("-" * 80)
        print("USER_ID FORMAT BREAKDOWN")
        print("-" * 80)
        print(f"Numeric IDs (e.g., 100362, 103092):  {len(numeric_users):,} users ({len(numeric_users)/total_users*100:.1f}%)")
        print(f"UUID format (e.g., 431bb991-...):    {len(uuid_users):,} users ({len(uuid_users)/total_users*100:.1f}%)")
        print(f"Other formats:                        {len(other_users):,} users ({len(other_users)/total_users*100:.1f}%)")
        
        print("\n" + "-" * 80)
        print("SAMPLE USER IDs BY FORMAT")
        print("-" * 80)
        
        if numeric_users:
            print(f"\nNumeric IDs (first 10):")
            for uid in numeric_users[:10]:
                print(f"  {uid}")
        
        if uuid_users:
            print(f"\nUUID format (first 10):")
            for uid in uuid_users[:10]:
                print(f"  {uid}")
        
        if other_users:
            print(f"\nOther formats (first 10):")
            for uid in other_users[:10]:
                print(f"  {uid}")
        
        # Check which format has demographics
        print("\n" + "=" * 80)
        print("DEMOGRAPHICS BY USER_ID FORMAT")
        print("=" * 80)
        
        demographics_fields = [
            'GENDER', 'CUST_YEAR_OF_BIRTH', 'CUST_INCOME_LEVEL', 
            'EDUCATION', 'OCCUPATION'
        ]
        all_fields_condition = " AND ".join([f"{field} IS NOT NULL" for field in demographics_fields])
        
        # Sample numeric users with/without demographics
        if numeric_users:
            sample_numeric = numeric_users[:5]
            print(f"\n{'-'*80}")
            print(f"NUMERIC USER IDs - Demographics Status")
            print(f"{'-'*80}")
            
            for uid in sample_numeric:
                cursor.execute("""
                    SELECT DISTINCT USER_ID, GENDER, CUST_YEAR_OF_BIRTH, CUST_INCOME_LEVEL, EDUCATION
                    FROM ADMIN.ORDERS_PROFILE_V
                    WHERE USER_ID = :user_id
                    AND ROWNUM = 1
                """, user_id=uid)
                row = cursor.fetchone()
                if row:
                    has_demo = all([row[1], row[2], row[3], row[4]])
                    status = "✓ HAS" if has_demo else "❌ MISSING"
                    print(f"{status} demographics - User {row[0]}: Gender={row[1]}, Born={row[2]}, Income={row[3]}, Edu={row[4]}")
        
        # Sample UUID users with/without demographics
        if uuid_users:
            sample_uuid = uuid_users[:5]
            print(f"\n{'-'*80}")
            print(f"UUID USER IDs - Demographics Status")
            print(f"{'-'*80}")
            
            for uid in sample_uuid:
                cursor.execute("""
                    SELECT DISTINCT USER_ID, GENDER, CUST_YEAR_OF_BIRTH, CUST_INCOME_LEVEL, EDUCATION
                    FROM ADMIN.ORDERS_PROFILE_V
                    WHERE USER_ID = :user_id
                    AND ROWNUM = 1
                """, user_id=uid)
                row = cursor.fetchone()
                if row:
                    has_demo = all([row[1], row[2], row[3], row[4]])
                    status = "✓ HAS" if has_demo else "❌ MISSING"
                    print(f"{status} demographics - User {row[0][:36]}: Gender={row[1]}, Born={row[2]}, Income={row[3]}, Edu={row[4]}")
        
        # Count demographics by format
        print("\n" + "=" * 80)
        print("SUMMARY: DEMOGRAPHICS COMPLETENESS BY FORMAT")
        print("=" * 80)
        
        if numeric_users:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT USER_ID)
                FROM ADMIN.ORDERS_PROFILE_V
                WHERE USER_ID IN ({','.join([f"'{u}'" for u in numeric_users[:1000]])})
                AND {all_fields_condition}
            """)
            numeric_with_demo = cursor.fetchone()[0]
            print(f"\nNumeric IDs: {numeric_with_demo:,} / {len(numeric_users):,} have complete demographics ({numeric_with_demo/len(numeric_users)*100:.1f}%)")
        
        if uuid_users:
            # For UUID, check in batches if too many
            if len(uuid_users) <= 1000:
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT USER_ID)
                    FROM ADMIN.ORDERS_PROFILE_V
                    WHERE USER_ID IN ({','.join([f"'{u}'" for u in uuid_users])})
                    AND {all_fields_condition}
                """)
                uuid_with_demo = cursor.fetchone()[0]
            else:
                # Sample check for large sets
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT USER_ID)
                    FROM ADMIN.ORDERS_PROFILE_V
                    WHERE USER_ID LIKE '%-%'
                    AND {all_fields_condition}
                """)
                uuid_with_demo = cursor.fetchone()[0]
            
            print(f"UUID format: {uuid_with_demo:,} / {len(uuid_users):,} have complete demographics ({uuid_with_demo/len(uuid_users)*100:.1f}%)")
        
        print("\n" + "=" * 80)
        print("INTERPRETATION")
        print("=" * 80)
        print("\nLikely explanation:")
        print("• Numeric IDs (100362, 103092, etc.) = Original/legacy users with full profiles")
        print("• UUID format = Newer users or system-generated accounts")
        print("\nThe data suggests a mixed user identity system in your application.")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_user_id_formats()
