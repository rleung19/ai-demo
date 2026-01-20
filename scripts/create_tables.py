#!/usr/bin/env python3
"""
Create Churn Prediction Tables in Oracle ADB
Executes sql/create_churn_tables.sql to create all required tables

Usage:
    python scripts/create_tables.py

Prerequisites:
    - Oracle Instant Client installed
    - oracledb package installed (pip install oracledb)
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
sql_file = project_root / 'sql' / 'create_churn_tables.sql'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print(f"✓ Loaded .env file from: {env_file}")
    else:
        print(f"⚠️  WARNING: .env file not found at {env_file}")
        load_dotenv()
except ImportError:
    print("⚠️  WARNING: python-dotenv not installed.")
    print("   Install with: pip install python-dotenv")
    print("   Using system environment variables only.")

def initialize_oracle_client():
    """Initialize Oracle client with wallet support"""
    try:
        import oracledb
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        print("   Install with: pip install oracledb")
        sys.exit(1)
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set in environment")
        print(f"   Check .env file at: {env_file}")
        sys.exit(1)
    
    if not os.path.exists(wallet_path):
        print(f"❌ ERROR: Wallet path does not exist: {wallet_path}")
        sys.exit(1)
    
    # Set TNS_ADMIN if not already set
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    # Try to initialize Oracle client (thick mode)
    try:
        import glob
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
                print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
            except Exception:
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                    print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
                except Exception:
                    oracledb.init_oracle_client(config_dir=wallet_path)
                    print(f"✓ Oracle client initialized (thick mode)")
        else:
            oracledb.init_oracle_client(config_dir=wallet_path)
            print(f"✓ Oracle client initialized (thick mode)")
    except Exception as e:
        print(f"⚠️  WARNING: Could not initialize Oracle client: {e}")
        print("   Attempting thin mode (limited wallet support)...")
    
    return oracledb

def get_connection():
    """Get database connection"""
    oracledb = initialize_oracle_client()
    
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not connection_string:
        print("❌ ERROR: ADB_CONNECTION_STRING not set in environment")
        sys.exit(1)
    
    if not password:
        print("❌ ERROR: ADB_PASSWORD not set in environment")
        sys.exit(1)
    
    try:
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        print(f"✓ Connected to ADB as {username}")
        return connection
    except Exception as e:
        print(f"❌ ERROR: Could not connect to database: {e}")
        print("\nTroubleshooting:")
        print("1. Verify ADB instance is running in Oracle Cloud Console")
        print("2. Check ADB_CONNECTION_STRING format in .env")
        print("3. Verify ADB_USERNAME and ADB_PASSWORD are correct")
        print("4. Ensure wallet files are accessible")
        sys.exit(1)

def execute_sql_file(connection, sql_file):
    """Execute SQL file"""
    if not sql_file.exists():
        print(f"❌ ERROR: SQL file not found: {sql_file}")
        sys.exit(1)
    
    print(f"\nReading SQL file: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Better SQL parsing: split by semicolons, but handle multi-line statements
    # Remove single-line comments first
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove inline comments (-- to end of line)
        if '--' in line:
            comment_pos = line.find('--')
            # Check if it's not inside a string
            if comment_pos >= 0:
                line = line[:comment_pos].rstrip()
        cleaned_lines.append(line)
    
    # Join all lines and split by semicolon
    full_text = '\n'.join(cleaned_lines)
    # Split by semicolon, but keep the semicolon with the statement
    raw_statements = [s.strip() + ';' for s in full_text.split(';') if s.strip()]
    
    # Filter out empty statements and comment-only statements
    statements = []
    for stmt in raw_statements:
        stmt = stmt.strip()
        # Remove trailing semicolon for execution (we'll add it back if needed)
        if stmt.endswith(';'):
            stmt = stmt[:-1].strip()
        
        # Skip if empty or only comments
        if not stmt or stmt.startswith('--'):
            continue
        
        # Skip SELECT statements (verification queries)
        if stmt.strip().upper().startswith('SELECT'):
            continue
        
        statements.append(stmt)
    
    print(f"✓ Found {len(statements)} SQL statements to execute")
    
    cursor = connection.cursor()
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip verification queries (SELECT statements)
        if statement.strip().upper().startswith('SELECT'):
            continue
        
        try:
            cursor.execute(statement)
            success_count += 1
            # Extract table name if it's a CREATE TABLE statement
            if 'CREATE TABLE' in statement.upper():
                # Try to extract table name
                parts = statement.upper().split('CREATE TABLE')
                if len(parts) > 1:
                    table_part = parts[1].split()[0]
                    print(f"  ✓ Statement {i}: Created table {table_part}")
                else:
                    print(f"  ✓ Statement {i}: Executed successfully")
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            # Check if it's a "table already exists" error (not critical)
            if 'ORA-00955' in error_msg or 'already exists' in error_msg.lower():
                print(f"  ⚠️  Statement {i}: Table/view already exists (skipping)")
                success_count += 1  # Count as success
                error_count -= 1
            else:
                print(f"  ❌ Statement {i}: Error - {error_msg}")
                # Print first few lines of the statement for debugging
                lines = statement.split('\n')[:3]
                print(f"     Statement: {lines[0][:80]}...")
    
    connection.commit()
    cursor.close()
    
    print(f"\n✓ Executed {success_count} statements successfully")
    if error_count > 0:
        print(f"⚠️  {error_count} statements had errors (see above)")
    
    return error_count == 0

def verify_tables(connection):
    """Verify that tables were created"""
    print("\n" + "=" * 60)
    print("Verifying Tables")
    print("=" * 60)
    
    expected_tables = [
        'CHURN_DATASET_TRAINING',
        'USER_PROFILES',
        'CHURN_PREDICTIONS'
    ]
    
    cursor = connection.cursor()
    all_exist = True
    
    for table_name in expected_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM OML.{table_name}")
            count = cursor.fetchone()[0]
            print(f"✓ {table_name}: EXISTS ({count:,} rows)")
        except Exception as e:
            print(f"❌ {table_name}: DOES NOT EXIST - {e}")
            all_exist = False
    
    cursor.close()
    return all_exist

def main():
    """Main function"""
    print("=" * 60)
    print("Create Churn Prediction Tables")
    print("=" * 60)
    
    if not sql_file.exists():
        print(f"❌ ERROR: SQL file not found: {sql_file}")
        sys.exit(1)
    
    # Connect to database
    connection = get_connection()
    
    try:
        # Execute SQL file
        success = execute_sql_file(connection, sql_file)
        
        if success:
            # Verify tables
            tables_exist = verify_tables(connection)
            
            if tables_exist:
                print("\n" + "=" * 60)
                print("✓ All tables created successfully!")
                print("=" * 60)
                print("\nNext steps:")
                print("1. Run data ingestion: python scripts/ingest_churn_data.py")
                print("2. Validate data (Task 2.6)")
            else:
                print("\n⚠️  Some tables may not have been created. Check errors above.")
                sys.exit(1)
        else:
            print("\n⚠️  Some SQL statements failed. Check errors above.")
            sys.exit(1)
    
    finally:
        connection.close()
        print(f"\n✓ Connection closed")

if __name__ == '__main__':
    main()
