#!/usr/bin/env python3
"""
Verify CHURN_PREDICTIONS Table Structure
=========================================

This script checks the actual structure of OML.CHURN_PREDICTIONS table
and compares it with the expected schema.
"""

import os
import sys
from pathlib import Path

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

def get_connection():
    """Get database connection"""
    try:
        import oracledb
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        return None
    
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    
    if not password or not connection_string:
        print("❌ ERROR: ADB_PASSWORD and ADB_CONNECTION_STRING must be set")
        return None
    
    try:
        wallet_path = os.getenv('ADB_WALLET_PATH')
        if wallet_path and Path(wallet_path).exists():
            try:
                oracledb.init_oracle_client(lib_dir=os.getenv('ORACLE_CLIENT_LIB_DIR'))
            except Exception:
                pass
        
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        return connection
    except Exception as e:
        print(f"❌ ERROR: Failed to connect: {e}")
        return None

def check_table_structure(connection):
    """Check actual table structure"""
    print("=" * 60)
    print("CHURN_PREDICTIONS Table Structure")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM USER_TABLES 
        WHERE TABLE_NAME = 'CHURN_PREDICTIONS'
    """)
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        print("❌ Table OML.CHURN_PREDICTIONS does not exist")
        return
    
    print("✓ Table exists")
    
    # Get column information
    print("\nColumns:")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            DATA_LENGTH,
            DATA_PRECISION,
            DATA_SCALE,
            NULLABLE,
            DATA_DEFAULT
        FROM USER_TAB_COLUMNS
        WHERE TABLE_NAME = 'CHURN_PREDICTIONS'
        ORDER BY COLUMN_ID
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        name, dtype, length, precision, scale, nullable, default = col
        dtype_str = dtype
        if precision:
            dtype_str += f"({precision}"
            if scale:
                dtype_str += f",{scale}"
            dtype_str += ")"
        elif length:
            dtype_str += f"({length})"
        
        nullable_str = "NULL" if nullable == "Y" else "NOT NULL"
        default_str = f" DEFAULT {default}" if default else ""
        
        print(f"  {name:30} {dtype_str:20} {nullable_str}{default_str}")
    
    # Get constraints
    print("\nConstraints:")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            CONSTRAINT_NAME,
            CONSTRAINT_TYPE,
            SEARCH_CONDITION
        FROM USER_CONSTRAINTS
        WHERE TABLE_NAME = 'CHURN_PREDICTIONS'
        ORDER BY CONSTRAINT_TYPE, CONSTRAINT_NAME
    """)
    
    constraints = cursor.fetchall()
    for constraint in constraints:
        name, ctype, condition = constraint
        ctype_str = {
            'P': 'PRIMARY KEY',
            'C': 'CHECK',
            'U': 'UNIQUE',
            'R': 'FOREIGN KEY'
        }.get(ctype, ctype)
        
        condition_str = f" ({condition})" if condition else ""
        print(f"  {name:30} {ctype_str}{condition_str}")
    
    # Get indexes
    print("\nIndexes:")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            INDEX_NAME,
            COLUMN_NAME
        FROM USER_IND_COLUMNS
        WHERE TABLE_NAME = 'CHURN_PREDICTIONS'
        ORDER BY INDEX_NAME, COLUMN_POSITION
    """)
    
    indexes = cursor.fetchall()
    current_index = None
    for index in indexes:
        idx_name, col_name = index
        if idx_name != current_index:
            if current_index:
                print()
            print(f"  {idx_name}:")
            current_index = idx_name
        print(f"    - {col_name}")
    
    # Expected schema
    print("\n" + "=" * 60)
    print("Expected Schema (from create_churn_tables.sql)")
    print("=" * 60)
    expected_columns = [
        ('USER_ID', 'VARCHAR2(36)', 'NOT NULL'),
        ('PREDICTED_CHURN_PROBABILITY', 'NUMBER(5,4)', 'NOT NULL'),
        ('PREDICTED_CHURN_LABEL', 'NUMBER(1)', 'NOT NULL'),
        ('RISK_SCORE', 'NUMBER(3)', 'NOT NULL'),
        ('MODEL_VERSION', 'VARCHAR2(50)', 'NOT NULL'),
        ('PREDICTION_DATE', 'TIMESTAMP', 'NOT NULL'),
        ('LAST_UPDATED', 'TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP'),
        ('CONFIDENCE_SCORE', 'NUMBER(5,4)', 'NULL')
    ]
    
    print("\nExpected Columns:")
    print("-" * 60)
    for name, dtype, nullable in expected_columns:
        print(f"  {name:30} {dtype:20} {nullable}")
    
    cursor.close()

def main():
    connection = get_connection()
    if not connection:
        sys.exit(1)
    
    try:
        check_table_structure(connection)
    finally:
        connection.close()

if __name__ == '__main__':
    main()
