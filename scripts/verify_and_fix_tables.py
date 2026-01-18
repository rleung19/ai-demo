#!/usr/bin/env python3
"""
Verify and fix churn prediction tables
Checks if tables exist and creates missing ones
"""

import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

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

def check_table_exists(connection, table_name):
    """Check if table exists"""
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM OML.{table_name}")
        cursor.fetchone()
        cursor.close()
        return True
    except Exception:
        cursor.close()
        return False

def create_churn_predictions_table(connection):
    """Create CHURN_PREDICTIONS table"""
    cursor = connection.cursor()
    
    # Drop table if exists
    try:
        cursor.execute("DROP TABLE OML.CHURN_PREDICTIONS CASCADE CONSTRAINTS")
        print("  Dropped existing CHURN_PREDICTIONS table")
    except Exception:
        pass
    
    # Create table
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
    
    cursor.execute(create_sql)
    
    # Add comments
    comments = [
        ("TABLE", "OML.CHURN_PREDICTIONS", "Predicted churn scores from ML model (output, not input features)"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.USER_ID", "Real UUID from ADMIN.USERS.ID"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.PREDICTED_CHURN_PROBABILITY", "Churn probability (0.0 to 1.0)"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.PREDICTED_CHURN_LABEL", "Binary prediction: 0 = retained, 1 = churned"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.RISK_SCORE", "Risk score (0-100) for display"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.MODEL_VERSION", "Version of model used for prediction"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.PREDICTION_DATE", "When prediction was made"),
        ("COLUMN", "OML.CHURN_PREDICTIONS.CONFIDENCE_SCORE", "Model confidence (optional)"),
    ]
    
    for comment_type, object_name, comment_text in comments:
        try:
            if comment_type == "TABLE":
                cursor.execute(f"COMMENT ON TABLE {object_name} IS '{comment_text}'")
            else:
                cursor.execute(f"COMMENT ON {comment_type} {object_name} IS '{comment_text}'")
        except Exception as e:
            print(f"  ⚠️  Could not add comment: {e}")
    
    # Create indexes
    indexes = [
        ("IDX_CHURN_PRED_LABEL", "PREDICTED_CHURN_LABEL"),
        ("IDX_CHURN_PRED_RISK", "RISK_SCORE"),
        ("IDX_CHURN_PRED_DATE", "PREDICTION_DATE"),
        ("IDX_CHURN_PRED_MODEL", "MODEL_VERSION"),
    ]
    
    for idx_name, col_name in indexes:
        try:
            cursor.execute(f"CREATE INDEX {idx_name} ON OML.CHURN_PREDICTIONS({col_name})")
        except Exception as e:
            print(f"  ⚠️  Could not create index {idx_name}: {e}")
    
    connection.commit()
    cursor.close()
    print("  ✓ Created CHURN_PREDICTIONS table with comments and indexes")

def main():
    print("=" * 60)
    print("Verify and Fix Tables")
    print("=" * 60)
    
    connection = get_connection()
    
    try:
        tables = {
            'CHURN_DATASET_TRAINING': check_table_exists(connection, 'CHURN_DATASET_TRAINING'),
            'USER_PROFILES': check_table_exists(connection, 'USER_PROFILES'),
            'CHURN_PREDICTIONS': check_table_exists(connection, 'CHURN_PREDICTIONS'),
        }
        
        print("\nTable Status:")
        for table, exists in tables.items():
            status = "✓ EXISTS" if exists else "❌ MISSING"
            print(f"  {table}: {status}")
        
        if not tables['CHURN_PREDICTIONS']:
            print("\nCreating CHURN_PREDICTIONS table...")
            create_churn_predictions_table(connection)
        else:
            print("\nCHURN_PREDICTIONS table exists. Verifying structure...")
            # Try to query it to see if it works
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM OML.CHURN_PREDICTIONS")
                count = cursor.fetchone()[0]
                print(f"  ✓ Table is accessible ({count} rows)")
            except Exception as e:
                print(f"  ❌ Table exists but has issues: {e}")
                print("  Recreating table...")
                create_churn_predictions_table(connection)
            cursor.close()
        
        # Final verification
        print("\nFinal Status:")
        for table in tables.keys():
            exists = check_table_exists(connection, table)
            status = "✓ EXISTS" if exists else "❌ MISSING"
            print(f"  {table}: {status}")
        
    finally:
        connection.close()

if __name__ == '__main__':
    main()
