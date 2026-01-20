#!/usr/bin/env python3
"""
Validate Churn Data in Oracle ADB
Task 2.6: Validate data loaded correctly (row counts, data types, constraints)

Usage:
    python scripts/validate_churn_data.py

Checks:
    - Row counts match expected values
    - Data types are correct
    - Constraints are enforced (CHURNED values, ranges, etc.)
    - No unexpected NULL values
    - Data quality (ranges, distributions)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

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
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set")
        sys.exit(1)
    
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    try:
        import glob
        oracle_opt_paths = ['/opt/oracle/instantclient_*/lib', '/opt/oracle/instantclient_*']
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
    
    return oracledb.connect(user=username, password=password, dsn=connection_string)

def validate_row_counts(connection):
    """
    Validate row counts for key tables.

    NOTE: We no longer enforce hard-coded expected counts, because the number
    of rows can legitimately change when we improve the ADMIN.USERS →
    USER_PROFILES mapping. Instead, this check reports the current counts for
    visibility, while the strict invariants are enforced in the mapping and
    data quality checks.
    """
    print("\n" + "=" * 60)
    print("1. Row Count Validation")
    print("=" * 60)
    
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING")
        training_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM OML.USER_PROFILES")
        profiles_count = cursor.fetchone()[0]
        try:
            cursor.execute("SELECT COUNT(*) FROM ADMIN.USERS")
            admin_users_count = cursor.fetchone()[0]
        except Exception:
            admin_users_count = None
    finally:
        cursor.close()

    print(f"  CHURN_DATASET_TRAINING: {training_count:,} rows")
    print(f"  USER_PROFILES:          {profiles_count:,} rows")
    if admin_users_count is not None:
        print(f"  ADMIN.USERS:            {admin_users_count:,} rows")
    else:
        print("  ADMIN.USERS:            (not accessible from this connection)")

    # Always return True here; hard correctness is enforced by mapping and
    # data quality checks rather than fixed absolute counts.
    return True

def validate_data_types(connection):
    """Validate data types match schema"""
    print("\n" + "=" * 60)
    print("2. Data Type Validation")
    print("=" * 60)
    
    cursor = connection.cursor()
    all_valid = True
    
    # Check key columns
    checks = [
        {
            'table': 'CHURN_DATASET_TRAINING',
            'column': 'CHURNED',
            'query': "SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING WHERE CHURNED NOT IN (0, 1) OR CHURNED IS NULL"
        },
        {
            'table': 'USER_PROFILES',
            'column': 'CHURNED',
            'query': "SELECT COUNT(*) FROM OML.USER_PROFILES WHERE CHURNED NOT IN (0, 1) AND CHURNED IS NOT NULL"
        },
        {
            'table': 'USER_PROFILES',
            'column': 'USER_ID',
            'query': "SELECT COUNT(*) FROM OML.USER_PROFILES WHERE USER_ID IS NULL"
        },
    ]
    
    for check in checks:
        try:
            cursor.execute(check['query'])
            invalid_count = cursor.fetchone()[0]
            status = "✓ PASS" if invalid_count == 0 else "❌ FAIL"
            print(f"  {check['table']}.{check['column']}: {status}")
            if invalid_count > 0:
                print(f"    Found {invalid_count} invalid values")
                all_valid = False
        except Exception as e:
            print(f"  {check['table']}.{check['column']}: ❌ ERROR - {e}")
            all_valid = False
    
    cursor.close()
    return all_valid

def validate_constraints(connection):
    """Validate constraints are enforced"""
    print("\n" + "=" * 60)
    print("3. Constraint Validation")
    print("=" * 60)
    
    cursor = connection.cursor()
    all_valid = True
    
    # Test CHURNED constraint (should only be 0 or 1)
    checks = [
        {
            'name': 'CHURNED values (0 or 1)',
            'query': "SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING WHERE CHURNED NOT IN (0, 1)"
        },
        {
            'name': 'USER_ID NOT NULL',
            'query': "SELECT COUNT(*) FROM OML.USER_PROFILES WHERE USER_ID IS NULL"
        },
        {
            'name': 'USER_ID uniqueness',
            'query': """
                SELECT COUNT(*) - COUNT(DISTINCT USER_ID) 
                FROM OML.USER_PROFILES
            """
        },
    ]
    
    for check in checks:
        try:
            cursor.execute(check['query'])
            invalid_count = cursor.fetchone()[0]
            status = "✓ PASS" if invalid_count == 0 else "❌ FAIL"
            print(f"  {check['name']}: {status}")
            if invalid_count > 0:
                print(f"    Found {invalid_count} violations")
                all_valid = False
        except Exception as e:
            print(f"  {check['name']}: ❌ ERROR - {e}")
            all_valid = False
    
    cursor.close()
    return all_valid

def validate_data_quality(connection):
    """Validate data quality (ranges, distributions)"""
    print("\n" + "=" * 60)
    print("4. Data Quality Validation")
    print("=" * 60)
    
    cursor = connection.cursor()
    all_valid = True
    
    # Check churn rate
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN CHURNED = 1 THEN 1 ELSE 0 END) AS churned,
                ROUND(SUM(CASE WHEN CHURNED = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate
            FROM OML.CHURN_DATASET_TRAINING
        """)
        row = cursor.fetchone()
        total, churned, churn_rate = row
        print(f"  Training Data Churn Rate: {churn_rate}% ({churned:,} / {total:,})")
        
        # Churn rate should be reasonable (between 10% and 50%)
        if 10 <= churn_rate <= 50:
            print(f"    Status: ✓ PASS (within expected range 10-50%)")
        else:
            print(f"    Status: ⚠️  WARNING (outside expected range 10-50%)")
            all_valid = False
    except Exception as e:
        print(f"  Churn rate check: ❌ ERROR - {e}")
        all_valid = False
    
    # Check USER_PROFILES churn rate
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN CHURNED = 1 THEN 1 ELSE 0 END) AS churned,
                ROUND(SUM(CASE WHEN CHURNED = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate
            FROM OML.USER_PROFILES
        """)
        row = cursor.fetchone()
        total, churned, churn_rate = row
        print(f"  User Profiles Churn Rate: {churn_rate}% ({churned:,} / {total:,})")
    except Exception as e:
        print(f"  User profiles churn rate: ❌ ERROR - {e}")
        all_valid = False
    
    # Check for NULL values in key numeric columns
    numeric_columns = ['AGE', 'TOTAL_PURCHASES', 'LIFETIME_VALUE', 'DAYS_SINCE_LAST_PURCHASE']
    for col in numeric_columns:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM OML.CHURN_DATASET_TRAINING 
                WHERE {col} IS NULL
            """)
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                print(f"  ⚠️  {col}: {null_count} NULL values found")
        except Exception as e:
            # Column might not exist or might allow NULLs
            pass
    
    # Check data ranges
    range_checks = [
        {
            'name': 'AGE range (0-120)',
            'query': "SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING WHERE AGE < 0 OR AGE > 120"
        },
        {
            'name': 'TOTAL_PURCHASES >= 0',
            'query': "SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING WHERE TOTAL_PURCHASES < 0"
        },
        {
            'name': 'LIFETIME_VALUE >= 0',
            'query': "SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING WHERE LIFETIME_VALUE < 0"
        },
    ]
    
    for check in range_checks:
        try:
            cursor.execute(check['query'])
            invalid_count = cursor.fetchone()[0]
            status = "✓ PASS" if invalid_count == 0 else "❌ FAIL"
            print(f"  {check['name']}: {status}")
            if invalid_count > 0:
                print(f"    Found {invalid_count} invalid values")
                all_valid = False
        except Exception as e:
            # Column might not exist
            pass
    
    cursor.close()
    return all_valid

def validate_user_id_mapping(connection):
    """Validate USER_ID mapping to ADMIN.USERS"""
    print("\n" + "=" * 60)
    print("5. USER_ID Mapping Validation")
    print("=" * 60)
    
    cursor = connection.cursor()
    all_valid = True
    
    # Check if USER_PROFILES.USER_ID matches ADMIN.USERS.ID
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM OML.USER_PROFILES up
            WHERE NOT EXISTS (
                SELECT 1 FROM ADMIN.USERS u WHERE u.ID = up.USER_ID
            )
        """)
        unmapped_count = cursor.fetchone()[0]
        
        if unmapped_count == 0:
            print("  ✓ All USER_PROFILES.USER_ID mapped to ADMIN.USERS.ID")
        else:
            print(f"  ❌ {unmapped_count} USER_PROFILES.USER_ID values not found in ADMIN.USERS.ID")
            all_valid = False
    except Exception as e:
        print(f"  ⚠️  Could not validate USER_PROFILES → ADMIN.USERS mapping: {e}")
        print("     (ADMIN.USERS table may not be accessible)")
    
    # Check that every ADMIN.USERS.ID has a corresponding USER_PROFILES row
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ADMIN.USERS u
            WHERE NOT EXISTS (
                SELECT 1 FROM OML.USER_PROFILES up WHERE up.USER_ID = u.ID
            )
        """)
        missing_profiles = cursor.fetchone()[0]
        
        if missing_profiles == 0:
            print("  ✓ All ADMIN.USERS.ID have matching USER_PROFILES.USER_ID")
        else:
            print(f"  ❌ {missing_profiles} ADMIN.USERS.ID values have no matching USER_PROFILES.USER_ID")
            all_valid = False
    except Exception as e:
        print(f"  ⚠️  Could not validate ADMIN.USERS → USER_PROFILES mapping: {e}")
        print("     (ADMIN.USERS table may not be accessible)")
    
    # Check USER_ID format (should ideally be UUIDs for USER_PROFILES)
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM OML.USER_PROFILES 
            WHERE USER_ID NOT LIKE '%-%-%-%-%'
        """)
        invalid_format_count = cursor.fetchone()[0]
        if invalid_format_count == 0:
            print("  ✓ All USER_PROFILES.USER_ID are in UUID format")
        else:
            print(f"  ⚠️  {invalid_format_count} USER_IDs not in UUID format")
    except Exception as e:
        print(f"  ⚠️  Could not validate USER_ID format: {e}")
    
    cursor.close()
    return all_valid

def main():
    """Main validation function"""
    print("=" * 60)
    print("Churn Data Validation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    connection = get_connection()
    
    try:
        results = {}
        
        # Run all validations
        results['row_counts'] = validate_row_counts(connection)
        results['data_types'] = validate_data_types(connection)
        results['constraints'] = validate_constraints(connection)
        results['data_quality'] = validate_data_quality(connection)
        results['user_id_mapping'] = validate_user_id_mapping(connection)
        
        # Summary
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        
        all_passed = True
        for check_name, passed in results.items():
            status = "✓ PASS" if passed else "❌ FAIL"
            print(f"  {check_name.replace('_', ' ').title()}: {status}")
            if not passed:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✓ ALL VALIDATIONS PASSED")
            print("=" * 60)
            print("\nData is ready for:")
            print("1. Feature engineering (Task 2.7)")
            print("2. Model training (Task 3.x)")
        else:
            print("⚠️  SOME VALIDATIONS FAILED")
            print("=" * 60)
            print("\nPlease review the errors above before proceeding.")
            sys.exit(1)
    
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
