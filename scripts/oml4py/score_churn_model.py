#!/usr/bin/env python3
"""
Churn Model Scoring Script
Task 3.8: Implement model scoring (batch prediction for all customers)

This script:
    1. Loads trained model from OML datastore
    2. Loads user features from CHURN_USER_FEATURES view
    3. Scores all users (batch prediction)
    4. Stores predictions in CHURN_PREDICTIONS table

Usage:
    # In OML Notebooks (recommended):
    %python
    exec(open('scripts/score_churn_model.py').read())
    
    # Or run as standalone (requires OML4Py):
    python scripts/score_churn_model.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Find project root
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
env_file = project_root / '.env'

# Import shared store_predictions function
sys.path.insert(0, str(script_dir.parent / 'shared'))
from store_predictions import store_predictions

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

def connect_oml():
    """Connect to OML4Py"""
    print("=" * 60)
    print("OML4Py Connection")
    print("=" * 60)
    
    try:
        import oml
        print("✓ OML4Py imported successfully")
    except ImportError:
        print("❌ ERROR: OML4Py not available")
        print("   This script requires OML4Py (typically in OML Notebooks)")
        return None
    
    if oml.isconnected():
        print("✓ OML connection is active")
        return oml
    else:
        print("⚠️  WARNING: OML reports not connected")
        return oml  # Return anyway, connection may be established later

def load_model(oml, model_name='churn_xgboost_v1'):
    """Load trained model from OML datastore"""
    print("\n" + "=" * 60)
    print("Loading Model from OML Datastore")
    print("=" * 60)
    
    try:
        loaded_dict = oml.ds.load(model_name)
        
        # Extract model (could be dict or list)
        if isinstance(loaded_dict, dict):
            if 'model' in loaded_dict:
                model = loaded_dict['model']
            else:
                # Get first value
                model = list(loaded_dict.values())[0]
        elif isinstance(loaded_dict, list):
            model = loaded_dict[0]
        else:
            model = loaded_dict
        
        print(f"✓ Model loaded: {model_name}")
        return model
    except Exception as e:
        print(f"❌ ERROR: Failed to load model: {e}")
        print(f"   Model '{model_name}' may not exist in datastore")
        print("   Train model first using scripts/train_churn_model.py")
        return None

def load_user_features(oml):
    """Load user features for scoring"""
    print("\n" + "=" * 60)
    print("Loading User Features")
    print("=" * 60)
    
    # Load from view
    print("Loading data from CHURN_USER_FEATURES view...")
    user_features_oml = oml.sync(view='CHURN_USER_FEATURES')
    user_features_pd = user_features_oml.pull()
    
    print(f"✓ Loaded {len(user_features_pd):,} user profiles")
    
    # Get USER_ID and features
    user_ids = user_features_pd['USER_ID'].copy()
    feature_cols = [col for col in user_features_pd.columns if col != 'USER_ID']
    X_users = user_features_pd[feature_cols].copy()
    
    print(f"✓ Features: {len(feature_cols)}")
    
    # Clean data
    print("\nCleaning data...")
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(X_users[col]):
            X_users[col] = X_users[col].replace([np.inf, -np.inf], np.nan)
            X_users[col] = X_users[col].fillna(0)
    
    print("✓ Data cleaned")
    
    return user_ids, X_users, feature_cols, user_features_oml

def score_users(oml, model, X_users, feature_cols):
    """Score all users with the model"""
    print("\n" + "=" * 60)
    print("Scoring Users")
    print("=" * 60)
    
    # Push to OML
    print("Pushing user features to OML...")
    X_users_oml = oml.push(X_users)
    X_users_oml_features = X_users_oml[feature_cols]
    
    print(f"✓ Features pushed: {X_users_oml_features.shape}")
    
    # Get predictions
    print("Generating predictions...")
    y_pred_proba_oml = model.predict_proba(X_users_oml_features)
    
    # Convert to pandas
    y_pred_proba_pd = y_pred_proba_oml.pull()
    if isinstance(y_pred_proba_pd, pd.DataFrame):
        if 1 in y_pred_proba_pd.columns:
            churn_probabilities = y_pred_proba_pd[1].values
        elif len(y_pred_proba_pd.columns) == 2:
            churn_probabilities = y_pred_proba_pd.iloc[:, 1].values
        else:
            churn_probabilities = y_pred_proba_pd.values.flatten()
    else:
        churn_probabilities = np.array(y_pred_proba_pd)
    
    print(f"✓ Generated {len(churn_probabilities):,} predictions")
    print(f"  Average churn probability: {churn_probabilities.mean():.4f}")
    print(f"  Max churn probability: {churn_probabilities.max():.4f}")
    print(f"  Min churn probability: {churn_probabilities.min():.4f}")
    
    return churn_probabilities

# Import shared store_predictions function
import sys
from pathlib import Path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent / 'shared'))
from store_predictions import store_predictions

def get_connection():
    """Get database connection for storing predictions"""
    try:
        import oracledb
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        return None
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set")
        return None
    
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
    
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    return oracledb.connect(user=username, password=password, dsn=connection_string)

def main():
    """Main scoring function"""
    print("=" * 60)
    print("Churn Model Scoring (Batch Prediction)")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to OML
    oml = connect_oml()
    if oml is None:
        sys.exit(1)
    
    # Connect to database for storing predictions
    connection = get_connection()
    if connection is None:
        sys.exit(1)
    
    try:
        # Load model
        model = load_model(oml, model_name='churn_xgboost_v1')
        if model is None:
            sys.exit(1)
        
        # Load user features
        user_ids, X_users, feature_cols, user_features_oml = load_user_features(oml)
        
        # Score users
        churn_probabilities = score_users(oml, model, X_users, feature_cols)
        
        # Store predictions
        success = store_predictions(
            connection,
            user_ids,
            churn_probabilities,
            model_version='v1.0',
            threshold=0.5
        )
        
        if success:
            print("\n" + "=" * 60)
            print("✓ Scoring completed successfully!")
            print("=" * 60)
            print("\nPredictions stored in OML.CHURN_PREDICTIONS table")
            print("Ready for API integration (Task 4.x)")
        else:
            print("\n❌ Scoring failed. Check errors above.")
            sys.exit(1)
    
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    try:
        import oml
        if oml.isconnected():
            main()
        else:
            print("⚠️  OML not connected")
            print("   This script should be run in OML Notebooks")
    except ImportError:
        print("⚠️  OML4Py not available")
        print("   This script requires OML4Py (typically in OML Notebooks)")
        sys.exit(1)
