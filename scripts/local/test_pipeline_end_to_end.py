#!/usr/bin/env python3
"""
End-to-End Pipeline Test
Task 3.12: Test pipeline end-to-end (data → model → predictions)

This script tests the complete ML pipeline:
1. Train model
2. Score users
3. Verify predictions in database
4. Validate data quality

Usage:
    python scripts/local/test_pipeline_end_to_end.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Find project root
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent  # scripts/local -> scripts -> project_root
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
    
    if not connection_string or not password:
        print("❌ ERROR: ADB connection credentials not set")
        sys.exit(1)
    
    try:
        return oracledb.connect(user=username, password=password, dsn=connection_string)
    except Exception as e:
        print(f"❌ ERROR: Failed to connect: {e}")
        sys.exit(1)

def test_data_availability(connection):
    """Test 1: Verify training data is available"""
    print("\n" + "=" * 60)
    print("Test 1: Data Availability")
    print("=" * 60)
    
    try:
        cursor = connection.cursor()
        
        # Check training data
        cursor.execute("SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING")
        train_count = cursor.fetchone()[0]
        print(f"✓ Training data: {train_count:,} rows")
        
        # Check user profiles
        cursor.execute("SELECT COUNT(*) FROM OML.USER_PROFILES")
        user_count = cursor.fetchone()[0]
        print(f"✓ User profiles: {user_count:,} rows")
        
        # Check views
        cursor.execute("SELECT COUNT(*) FROM OML.CHURN_TRAINING_DATA")
        view_count = cursor.fetchone()[0]
        print(f"✓ Training view: {view_count:,} rows")
        
        cursor.close()
        
        if train_count > 0 and user_count > 0:
            print("✓ All data sources available")
            return True
        else:
            print("❌ Missing data")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_model_training():
    """Test 2: Train model"""
    print("\n" + "=" * 60)
    print("Test 2: Model Training")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(script_dir))
        from train_churn_model_local import main as train_main
        
        print("Running training pipeline...")
        train_main()
        print("✓ Model training completed")
        return True
    except Exception as e:
        print(f"❌ ERROR: Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_scoring():
    """Test 3: Score users"""
    print("\n" + "=" * 60)
    print("Test 3: Model Scoring")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(script_dir))
        from score_churn_model_local import main as score_main
        
        print("Running scoring pipeline...")
        score_main()
        print("✓ User scoring completed")
        return True
    except Exception as e:
        print(f"❌ ERROR: Scoring failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predictions_in_db(connection):
    """Test 4: Verify predictions in database"""
    print("\n" + "=" * 60)
    print("Test 4: Predictions in Database")
    print("=" * 60)
    
    try:
        cursor = connection.cursor()
        
        # Check prediction count
        cursor.execute("SELECT COUNT(*) FROM OML.CHURN_PREDICTIONS")
        pred_count = cursor.fetchone()[0]
        print(f"✓ Predictions stored: {pred_count:,} rows")
        
        # Check user profile count
        cursor.execute("SELECT COUNT(*) FROM OML.USER_PROFILES")
        user_count = cursor.fetchone()[0]
        print(f"✓ User profiles: {user_count:,} rows")
        
        # Verify counts match
        if pred_count == user_count:
            print(f"✓ All {user_count:,} users have predictions")
        else:
            print(f"⚠️  WARNING: Prediction count ({pred_count}) doesn't match user count ({user_count})")
        
        # Check data quality
        cursor.execute("""
            SELECT 
                COUNT(*) AS TOTAL,
                COUNT(CASE WHEN PREDICTED_CHURN_PROBABILITY IS NULL THEN 1 END) AS NULL_PROB,
                COUNT(CASE WHEN PREDICTED_CHURN_LABEL IS NULL THEN 1 END) AS NULL_LABEL,
                MIN(PREDICTED_CHURN_PROBABILITY) AS MIN_PROB,
                MAX(PREDICTED_CHURN_PROBABILITY) AS MAX_PROB,
                AVG(PREDICTED_CHURN_PROBABILITY) AS AVG_PROB
            FROM OML.CHURN_PREDICTIONS
        """)
        stats = cursor.fetchone()
        total, null_prob, null_label, min_prob, max_prob, avg_prob = stats
        
        print(f"\nData Quality:")
        print(f"  Total predictions: {total:,}")
        print(f"  NULL probabilities: {null_prob}")
        print(f"  NULL labels: {null_label}")
        print(f"  Probability range: {min_prob:.4f} - {max_prob:.4f}")
        print(f"  Average probability: {avg_prob:.4f}")
        
        # Check for issues
        issues = []
        if null_prob > 0:
            issues.append(f"{null_prob} NULL probabilities")
        if null_label > 0:
            issues.append(f"{null_label} NULL labels")
        if min_prob < 0 or max_prob > 1:
            issues.append("Probabilities outside [0, 1] range")
        
        if issues:
            print(f"⚠️  WARNING: Found issues: {', '.join(issues)}")
        else:
            print("✓ Data quality checks passed")
        
        cursor.close()
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_registry(connection):
    """Test 5: Verify model registry"""
    print("\n" + "=" * 60)
    print("Test 5: Model Registry")
    print("=" * 60)
    
    try:
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) FROM user_tables 
            WHERE table_name = 'MODEL_REGISTRY'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("⚠️  WARNING: MODEL_REGISTRY table does not exist")
            print("   Run: python scripts/create_model_registry_table.py")
            cursor.close()
            return False
        
        # Get latest model
        cursor.execute("""
            SELECT MODEL_ID, MODEL_NAME, AUC_SCORE, TRAINING_DATE, STATUS
            FROM OML.MODEL_REGISTRY
            ORDER BY TRAINING_DATE DESC
            FETCH FIRST 1 ROWS ONLY
        """)
        model = cursor.fetchone()
        
        if model:
            model_id, model_name, auc, train_date, status = model
            print(f"✓ Latest model in registry:")
            print(f"  ID: {model_id}")
            print(f"  Name: {model_name}")
            print(f"  AUC: {auc:.4f}")
            print(f"  Training Date: {train_date}")
            print(f"  Status: {status}")
            cursor.close()
            return True
        else:
            print("⚠️  WARNING: No models in registry")
            cursor.close()
            return False
            
    except Exception as e:
        print(f"⚠️  WARNING: Model registry check failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("End-to-End Pipeline Test")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Connect to database
    connection = get_connection()
    
    try:
        # Test 1: Data availability
        results['data'] = test_data_availability(connection)
        
        # Test 2: Model training
        results['training'] = test_model_training()
        
        # Test 3: Model scoring
        results['scoring'] = test_model_scoring()
        
        # Test 4: Predictions in database
        results['predictions'] = test_predictions_in_db(connection)
        
        # Test 5: Model registry
        results['registry'] = test_model_registry(connection)
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        all_passed = all(results.values())
        
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "❌ FAIL"
            print(f"{test_name.upper():15} {status}")
        
        if all_passed:
            print("\n✓ All tests passed! Pipeline is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Review errors above.")
            sys.exit(1)
        
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
