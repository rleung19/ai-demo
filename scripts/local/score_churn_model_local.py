#!/usr/bin/env python3
"""
Churn Model Scoring Script (Local Model)
Task 3.8: Implement model scoring (batch prediction for all customers)

This script:
    1. Loads trained model from pickle file (local model)
    2. Connects to ADB as OML user
    3. Loads user features from CHURN_USER_FEATURES view (SQL query)
    4. Scores all users using local model (batch prediction)
    5. Stores predictions in CHURN_PREDICTIONS table

Usage:
    python scripts/local/score_churn_model_local.py [--model-path PATH]
"""

import os
import sys
import pickle
import json
import glob
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import argparse

# Find project root
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
env_file = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

# ============================================================================
# ADB Connection (as OML user)
# ============================================================================

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
    """Get database connection as OML user"""
    oracledb = initialize_oracle_client()
    
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')  # Default to OML user
    password = os.getenv('ADB_PASSWORD')
    
    if not connection_string:
        print("❌ ERROR: ADB_CONNECTION_STRING not set in environment")
        sys.exit(1)
    
    if not password:
        print("❌ ERROR: ADB_PASSWORD not set in environment")
        sys.exit(1)
    
    print(f"✓ Connecting as {username} user...")
    
    try:
        return oracledb.connect(user=username, password=password, dsn=connection_string)
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to database: {e}")
        sys.exit(1)

# ============================================================================
# Model Loading (from pickle file)
# ============================================================================

def find_latest_model(model_dir=None):
    """Find the latest model file in models directory"""
    if model_dir is None:
        model_dir = project_root / 'models'
    
    if not model_dir.exists():
        print(f"❌ ERROR: Model directory does not exist: {model_dir}")
        return None, None
    
    # Find all pickle files
    model_files = list(model_dir.glob('churn_model_*.pkl'))
    
    if not model_files:
        print(f"❌ ERROR: No model files found in {model_dir}")
        return None, None
    
    # Sort by modification time (newest first)
    model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_model = model_files[0]
    
    # Find corresponding metadata file
    metadata_file = latest_model.parent / latest_model.name.replace('.pkl', '_metadata.json')
    
    return latest_model, metadata_file

def load_model_from_pickle(model_path=None):
    """Load trained model from pickle file"""
    print("\n" + "=" * 60)
    print("Loading Model from Pickle File")
    print("=" * 60)
    
    if model_path is None:
        model_path, metadata_path = find_latest_model()
        if model_path is None:
            return None, None
    else:
        model_path = Path(model_path)
        metadata_path = model_path.parent / model_path.name.replace('.pkl', '_metadata.json')
    
    # Load model
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✓ Model loaded: {model_path.name}")
    except Exception as e:
        print(f"❌ ERROR: Failed to load model: {e}")
        return None, None
    
    # Load metadata
    metadata = None
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            print(f"✓ Metadata loaded: {metadata_path.name}")
            print(f"  Model: {metadata.get('model_name', 'Unknown')}")
            print(f"  AUC: {metadata.get('performance', {}).get('auc', 'N/A'):.4f}")
            print(f"  Optimal threshold: {metadata.get('optimal_threshold', 0.5):.3f}")
        except Exception as e:
            print(f"⚠️  WARNING: Failed to load metadata: {e}")
    
    return model, metadata

# ============================================================================
# User Feature Loading (from ADB view)
# ============================================================================

def load_user_features_from_db(connection):
    """Load user features from CHURN_USER_FEATURES view"""
    print("\n" + "=" * 60)
    print("Loading User Features from Database")
    print("=" * 60)
    
    # Load from view
    print("Loading data from OML.CHURN_USER_FEATURES view...")
    query = "SELECT * FROM OML.CHURN_USER_FEATURES"
    
    try:
        df = pd.read_sql(query, connection)
        print(f"✓ Loaded {len(df):,} user profiles")
    except Exception as e:
        print(f"❌ ERROR: Failed to load user features: {e}")
        return None, None, None
    
    # Get USER_ID and features
    user_ids = df['USER_ID'].copy()
    feature_cols = [col for col in df.columns if col != 'USER_ID']
    X_users = df[feature_cols].copy()
    
    print(f"✓ Features: {len(feature_cols)}")
    
    # Clean data
    print("\nCleaning data...")
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(X_users[col]):
            X_users[col] = X_users[col].replace([np.inf, -np.inf], np.nan)
            X_users[col] = pd.to_numeric(X_users[col], errors='coerce').fillna(0)
    
    print("✓ Data cleaned")
    
    return user_ids, X_users, feature_cols

# ============================================================================
# Scoring (using local model)
# ============================================================================

def score_users_local(model, X_users, feature_cols):
    """Score all users with the local model"""
    print("\n" + "=" * 60)
    print("Scoring Users (Local Model)")
    print("=" * 60)
    
    # Ensure feature order matches training
    X_users_aligned = X_users[feature_cols].copy()
    
    print(f"✓ Features aligned: {X_users_aligned.shape}")
    
    # Get predictions
    print("Generating predictions...")
    try:
        y_pred_proba = model.predict_proba(X_users_aligned)
        
        # Handle different model output formats
        if isinstance(y_pred_proba, np.ndarray):
            if y_pred_proba.ndim == 2:
                # Binary classification: get probability of class 1
                if y_pred_proba.shape[1] == 2:
                    churn_probabilities = y_pred_proba[:, 1]
                else:
                    churn_probabilities = y_pred_proba.flatten()
            else:
                churn_probabilities = y_pred_proba
        else:
            # Handle pandas DataFrame or other formats
            if hasattr(y_pred_proba, 'values'):
                y_pred_proba = y_pred_proba.values
            if y_pred_proba.ndim == 2 and y_pred_proba.shape[1] == 2:
                churn_probabilities = y_pred_proba[:, 1]
            else:
                churn_probabilities = y_pred_proba.flatten()
        
        print(f"✓ Generated {len(churn_probabilities):,} predictions")
        print(f"  Average churn probability: {churn_probabilities.mean():.4f}")
        print(f"  Max churn probability: {churn_probabilities.max():.4f}")
        print(f"  Min churn probability: {churn_probabilities.min():.4f}")
        
        return churn_probabilities
    except Exception as e:
        print(f"❌ ERROR: Failed to generate predictions: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main scoring function"""
    parser = argparse.ArgumentParser(description='Score users with local churn model')
    parser.add_argument('--model-path', type=str, help='Path to model pickle file (default: latest)')
    parser.add_argument('--threshold', type=float, default=None, help='Churn threshold (default: from metadata)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Churn Model Scoring (Local Model - Batch Prediction)")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to database as OML user
    connection = get_connection()
    if connection is None:
        sys.exit(1)
    
    try:
        # Load model
        model, metadata = load_model_from_pickle(args.model_path)
        if model is None:
            print("❌ ERROR: Failed to load model")
            sys.exit(1)
        
        # Get feature columns and threshold from metadata
        if metadata:
            feature_cols = metadata.get('feature_cols', None)
            optimal_threshold = metadata.get('optimal_threshold', 0.5)
        else:
            feature_cols = None
            optimal_threshold = 0.5
        
        # Use provided threshold or metadata threshold
        threshold = args.threshold if args.threshold is not None else optimal_threshold
        
        # Load user features from database
        user_ids, X_users, feature_cols_from_db = load_user_features_from_db(connection)
        if user_ids is None:
            print("❌ ERROR: Failed to load user features")
            sys.exit(1)
        
        # Use feature columns from metadata if available, otherwise use from DB
        if feature_cols:
            # Ensure all metadata features exist in loaded data
            missing_features = set(feature_cols) - set(X_users.columns)
            if missing_features:
                print(f"⚠️  WARNING: Missing features from metadata: {missing_features}")
                # Use intersection
                feature_cols = [f for f in feature_cols if f in X_users.columns]
            print(f"✓ Using {len(feature_cols)} features from metadata")
        else:
            feature_cols = feature_cols_from_db
            print(f"✓ Using {len(feature_cols)} features from database")
        
        # Score users
        churn_probabilities = score_users_local(model, X_users, feature_cols)
        if churn_probabilities is None:
            print("❌ ERROR: Failed to score users")
            sys.exit(1)
        
        # Store predictions (import from shared utility)
        sys.path.insert(0, str(script_dir.parent / 'shared'))
        from store_predictions import store_predictions
        
        # Get model version from metadata or use default
        model_version = metadata.get('timestamp', 'unknown') if metadata else 'v1.0'
        
        success = store_predictions(
            connection,
            user_ids,
            churn_probabilities,
            model_version=model_version,
            threshold=threshold
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
    main()
