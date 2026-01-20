#!/usr/bin/env python3
"""
Fix CHURN_PREDICTIONS Table Structure
=====================================

This script recreates the CHURN_PREDICTIONS table with the correct schema
as defined in create_churn_tables.sql.

WARNING: This will DROP the existing table and recreate it.
Make sure to backup any data if needed.
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

def recreate_table(connection):
    """Recreate CHURN_PREDICTIONS table with correct schema"""
    print("=" * 60)
    print("Recreating CHURN_PREDICTIONS Table")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM USER_TABLES 
        WHERE TABLE_NAME = 'CHURN_PREDICTIONS'
    """)
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        print("⚠️  WARNING: Table CHURN_PREDICTIONS already exists")
        print("   This will DROP the existing table and recreate it")
        print("   Any existing data will be lost!")
        
        response = input("\nDo you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return False
        
        # Drop existing table
        print("\nDropping existing table...")
        try:
            cursor.execute("DROP TABLE OML.CHURN_PREDICTIONS CASCADE CONSTRAINTS")
            connection.commit()
            print("✓ Table dropped")
        except Exception as e:
            print(f"⚠️  Could not drop table: {e}")
            connection.rollback()
    
    # Create table with correct schema
    print("\nCreating table with correct schema...")
    create_sql = """
    CREATE TABLE OML.CHURN_PREDICTIONS (
        USER_ID VARCHAR2(36) NOT NULL,
        PREDICTED_CHURN_PROBABILITY NUMBER(5,4) NOT NULL,
        PREDICTED_CHURN_LABEL NUMBER(1) NOT NULL,
        RISK_SCORE NUMBER(3) NOT NULL,
        MODEL_VERSION VARCHAR2(50) NOT NULL,
        PREDICTION_DATE TIMESTAMP NOT NULL,
        LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONFIDENCE_SCORE NUMBER(5,4),
        CONSTRAINT CHK_PREDICTED_LABEL CHECK (PREDICTED_CHURN_LABEL IN (0, 1)),
        CONSTRAINT CHK_PROBABILITY CHECK (PREDICTED_CHURN_PROBABILITY >= 0 AND PREDICTED_CHURN_PROBABILITY <= 1),
        CONSTRAINT CHK_RISK_SCORE CHECK (RISK_SCORE >= 0 AND RISK_SCORE <= 100),
        CONSTRAINT CHK_CONFIDENCE CHECK (CONFIDENCE_SCORE IS NULL OR (CONFIDENCE_SCORE >= 0 AND CONFIDENCE_SCORE <= 1)),
        CONSTRAINT PK_CHURN_PREDICTIONS PRIMARY KEY (USER_ID)
    )
    """
    
    try:
        cursor.execute(create_sql)
        connection.commit()
        print("✓ Table created successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to create table: {e}")
        connection.rollback()
        return False
    
    # Add comments
    print("\nAdding table comments...")
    comments = [
        ("TABLE", "CHURN_PREDICTIONS", "Predicted churn scores from ML model (output, not input features)"),
        ("COLUMN", "CHURN_PREDICTIONS.USER_ID", "Real UUID from ADMIN.USERS.ID"),
        ("COLUMN", "CHURN_PREDICTIONS.PREDICTED_CHURN_PROBABILITY", "Churn probability (0.0 to 1.0)"),
        ("COLUMN", "CHURN_PREDICTIONS.PREDICTED_CHURN_LABEL", "Binary prediction: 0 = retained, 1 = churned"),
        ("COLUMN", "CHURN_PREDICTIONS.RISK_SCORE", "Risk score (0-100) for display"),
        ("COLUMN", "CHURN_PREDICTIONS.MODEL_VERSION", "Version of model used for prediction"),
        ("COLUMN", "CHURN_PREDICTIONS.PREDICTION_DATE", "When prediction was made"),
        ("COLUMN", "CHURN_PREDICTIONS.CONFIDENCE_SCORE", "Model confidence (optional)"),
    ]
    
    for comment_type, object_name, comment_text in comments:
        try:
            if comment_type == "TABLE":
                cursor.execute(f"COMMENT ON TABLE {object_name} IS '{comment_text}'")
            else:
                cursor.execute(f"COMMENT ON {comment_type} {object_name} IS '{comment_text}'")
        except Exception as e:
            print(f"⚠️  Could not add comment to {object_name}: {e}")
    
    connection.commit()
    print("✓ Comments added")
    
    # Create indexes
    print("\nCreating indexes...")
    indexes = [
        ("IDX_CHURN_PRED_LABEL", "PREDICTED_CHURN_LABEL"),
        ("IDX_CHURN_PRED_RISK", "RISK_SCORE"),
        ("IDX_CHURN_PRED_DATE", "PREDICTION_DATE"),
        ("IDX_CHURN_PRED_MODEL", "MODEL_VERSION"),
    ]
    
    for idx_name, col_name in indexes:
        try:
            cursor.execute(f"""
                CREATE INDEX {idx_name} ON OML.CHURN_PREDICTIONS({col_name})
            """)
            print(f"  ✓ Created index {idx_name}")
        except Exception as e:
            print(f"  ⚠️  Could not create index {idx_name}: {e}")
    
    connection.commit()
    print("✓ Indexes created")
    
    # Verify
    print("\nVerifying table structure...")
    cursor.execute("""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            DATA_PRECISION,
            DATA_SCALE,
            NULLABLE
        FROM USER_TAB_COLUMNS
        WHERE TABLE_NAME = 'CHURN_PREDICTIONS'
        ORDER BY COLUMN_ID
    """)
    
    columns = cursor.fetchall()
    print("\nTable columns:")
    print("-" * 60)
    for col in columns:
        name, dtype, precision, scale, nullable = col
        dtype_str = dtype
        if precision:
            dtype_str += f"({precision}"
            if scale:
                dtype_str += f",{scale}"
            dtype_str += ")"
        nullable_str = "NULL" if nullable == "Y" else "NOT NULL"
        print(f"  {name:30} {dtype_str:20} {nullable_str}")
    
    cursor.close()
    return True

def main():
    print("=" * 60)
    print("Fix CHURN_PREDICTIONS Table")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Drop the existing CHURN_PREDICTIONS table (if exists)")
    print("  2. Create a new table with the correct schema")
    print("  3. Add comments and indexes")
    print("\n⚠️  WARNING: This will delete any existing data in the table!")
    print()
    
    connection = get_connection()
    if not connection:
        sys.exit(1)
    
    try:
        success = recreate_table(connection)
        if success:
            print("\n" + "=" * 60)
            print("✓ Table recreated successfully!")
            print("=" * 60)
            print("\nYou can now:")
            print("  1. Run the training notebook")
            print("  2. Run the scoring notebook")
            print("  3. Predictions will be stored in the correct format")
        else:
            print("\n❌ Failed to recreate table")
            sys.exit(1)
    finally:
        connection.close()

if __name__ == '__main__':
    main()
