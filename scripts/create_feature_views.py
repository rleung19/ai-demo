#!/usr/bin/env python3
"""
Create Feature Engineering Views
Task 2.7: Create feature engineering views in OML schema

Usage:
    python scripts/create_feature_views.py

Creates views:
    - CHURN_TRAINING_FEATURES - Features for training (excludes target)
    - CHURN_TRAINING_DATA - Features + target for training
    - CHURN_USER_FEATURES - Features for scoring actual users
"""

import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'
sql_file = project_root / 'sql' / 'create_feature_views.sql'

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

def execute_sql_file(connection, sql_file):
    """Execute SQL file"""
    if not sql_file.exists():
        print(f"❌ ERROR: SQL file not found: {sql_file}")
        sys.exit(1)
    
    print(f"\nReading SQL file: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Better SQL parsing
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        if '--' in line:
            comment_pos = line.find('--')
            if comment_pos >= 0:
                line = line[:comment_pos].rstrip()
        cleaned_lines.append(line)
    
    full_text = '\n'.join(cleaned_lines)
    raw_statements = [s.strip() + ';' for s in full_text.split(';') if s.strip()]
    
    statements = []
    for stmt in raw_statements:
        stmt = stmt.strip()
        if stmt.endswith(';'):
            stmt = stmt[:-1].strip()
        if not stmt or stmt.startswith('--'):
            continue
        if stmt.strip().upper().startswith('SELECT'):
            continue
        statements.append(stmt)
    
    print(f"✓ Found {len(statements)} SQL statements to execute")
    
    cursor = connection.cursor()
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        try:
            cursor.execute(statement)
            success_count += 1
            if 'CREATE' in statement.upper() and 'VIEW' in statement.upper():
                # Extract view name
                parts = statement.upper().split('VIEW')
                if len(parts) > 1:
                    view_part = parts[1].split()[0]
                    print(f"  ✓ Statement {i}: Created view {view_part}")
                else:
                    print(f"  ✓ Statement {i}: Executed successfully")
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            if 'ORA-00955' in error_msg or 'already exists' in error_msg.lower():
                print(f"  ⚠️  Statement {i}: View already exists (skipping)")
                success_count += 1
                error_count -= 1
            else:
                print(f"  ❌ Statement {i}: Error - {error_msg}")
                lines = statement.split('\n')[:3]
                print(f"     Statement: {lines[0][:80]}...")
    
    connection.commit()
    cursor.close()
    
    print(f"\n✓ Executed {success_count} statements successfully")
    if error_count > 0:
        print(f"⚠️  {error_count} statements had errors (see above)")
    
    return error_count == 0

def verify_views(connection):
    """Verify views were created"""
    print("\n" + "=" * 60)
    print("Verifying Views")
    print("=" * 60)
    
    expected_views = [
        'CHURN_TRAINING_FEATURES',
        'CHURN_TRAINING_DATA',
        'CHURN_USER_FEATURES'
    ]
    
    cursor = connection.cursor()
    all_exist = True
    
    for view_name in expected_views:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM OML.{view_name}")
            count = cursor.fetchone()[0]
            print(f"✓ {view_name}: EXISTS ({count:,} rows)")
        except Exception as e:
            print(f"❌ {view_name}: DOES NOT EXIST - {e}")
            all_exist = False
    
    cursor.close()
    return all_exist

def main():
    """Main function"""
    print("=" * 60)
    print("Create Feature Engineering Views")
    print("=" * 60)
    
    if not sql_file.exists():
        print(f"❌ ERROR: SQL file not found: {sql_file}")
        sys.exit(1)
    
    connection = get_connection()
    
    try:
        success = execute_sql_file(connection, sql_file)
        
        if success:
            views_exist = verify_views(connection)
            
            if views_exist:
                print("\n" + "=" * 60)
                print("✓ All views created successfully!")
                print("=" * 60)
                print("\nViews created:")
                print("  1. CHURN_TRAINING_FEATURES - Features for training")
                print("  2. CHURN_TRAINING_DATA - Features + target for training")
                print("  3. CHURN_USER_FEATURES - Features for scoring users")
                print("\nNext steps:")
                print("  1. Validate model performance (Task 2.8)")
                print("  2. Train model (Task 3.x)")
            else:
                print("\n⚠️  Some views may not have been created. Check errors above.")
                sys.exit(1)
        else:
            print("\n⚠️  Some SQL statements failed. Check errors above.")
            sys.exit(1)
    
    finally:
        connection.close()
        print(f"\n✓ Connection closed")

if __name__ == '__main__':
    main()
