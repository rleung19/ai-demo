#!/usr/bin/env python3
"""
Create Model Registry Table
Task 3.10: Model Versioning and Performance Tracking

Creates the MODEL_REGISTRY table for tracking model versions and performance.
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
        print("   Install with: pip install oracledb")
        sys.exit(1)
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set in environment")
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
    
    if not connection_string:
        print("❌ ERROR: ADB_CONNECTION_STRING not set in environment")
        sys.exit(1)
    
    if not password:
        print("❌ ERROR: ADB_PASSWORD not set in environment")
        sys.exit(1)
    
    try:
        return oracledb.connect(user=username, password=password, dsn=connection_string)
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to database: {e}")
        sys.exit(1)

def execute_sql_file(connection, sql_file):
    """Execute SQL file"""
    print(f"Reading SQL file: {sql_file}")
    
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolons (basic SQL parsing)
    statements = [s.strip() + ';' for s in sql_content.split(';') if s.strip()]
    
    cursor = connection.cursor()
    
    for i, statement in enumerate(statements, 1):
        if not statement.strip() or statement.strip() == ';':
            continue
        
        try:
            cursor.execute(statement)
            print(f"✓ Executed statement {i}/{len(statements)}")
        except Exception as e:
            # Check if table already exists
            if 'ORA-00955' in str(e) or 'name is already used' in str(e).lower():
                print(f"⚠️  Statement {i}: Table/view already exists (skipping)")
            else:
                print(f"❌ ERROR in statement {i}: {e}")
                print(f"   Statement: {statement[:100]}...")
                raise
    
    connection.commit()
    cursor.close()
    print("✓ All SQL statements executed successfully")

def main():
    """Main function"""
    print("=" * 60)
    print("Create Model Registry Table")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sql_file = project_root / 'sql' / 'create_model_registry_table.sql'
    
    if not sql_file.exists():
        print(f"❌ ERROR: SQL file not found: {sql_file}")
        sys.exit(1)
    
    connection = get_connection()
    
    try:
        execute_sql_file(connection, sql_file)
        print("\n" + "=" * 60)
        print("✓ Model Registry table created successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create table: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
