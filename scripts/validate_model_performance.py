#!/usr/bin/env python3
"""
Validate Model Performance
Task 2.8: Validate dataset produces reasonable model performance (AUC > 0.70)

Usage:
    python scripts/validate_model_performance.py

This script:
    1. Loads training data from CHURN_TRAINING_DATA view
    2. Splits into train/validation sets
    3. Trains XGBoost model
    4. Evaluates AUC on validation set
    5. Verifies AUC > 0.70 threshold

Note: Requires OML4Py (typically available in OML Notebooks)
      Falls back to local sklearn/xgboost if OML4Py unavailable
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

def load_data_from_view(connection):
    """Load training data from view"""
    print("\n" + "=" * 60)
    print("Loading Training Data from View")
    print("=" * 60)
    
    import pandas as pd
    
    # Query the view
    query = """
        SELECT * FROM OML.CHURN_TRAINING_DATA
    """
    
    df = pd.read_sql(query, connection)
    print(f"✓ Loaded {len(df):,} rows from CHURN_TRAINING_DATA view")
    
    # Separate features and target
    exclude_cols = ['USER_ID', 'CHURNED']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].copy()
    y = df['CHURNED'].copy()
    
    print(f"✓ Features: {len(feature_cols)}")
    print(f"✓ Target distribution: {y.value_counts().to_dict()}")
    print(f"✓ Churn rate: {y.mean() * 100:.2f}%")
    
    return X, y, feature_cols

def train_model_local(X_train, y_train, X_val, y_val, feature_cols):
    """Train model using local sklearn (XGBoost or RandomForest)"""
    print("\n" + "=" * 60)
    print("Training Model (Local)")
    print("=" * 60)
    
    try:
        from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
    except ImportError:
        print("❌ ERROR: sklearn not installed")
        print("   Install with: pip install scikit-learn")
        sys.exit(1)
    
    # Try XGBoost first, fallback to RandomForest
    model = None
    model_name = None
    
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        model_name = "XGBoost"
    except (ImportError, Exception) as e:
        print(f"⚠️  XGBoost not available: {e}")
        print("   Using RandomForest as fallback...")
        try:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            model_name = "RandomForest"
        except ImportError:
            print("❌ ERROR: sklearn not installed")
            print("   Install with: pip install scikit-learn")
            sys.exit(1)
    
    # Clean data
    import numpy as np
    import pandas as pd
    
    # Replace infinity and NaN
    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_train = X_train.fillna(0)
    X_val = X_val.replace([np.inf, -np.inf], np.nan)
    X_val = X_val.fillna(0)
    
    # Ensure numeric
    for col in feature_cols:
        X_train[col] = pd.to_numeric(X_train[col], errors='coerce').fillna(0)
        X_val[col] = pd.to_numeric(X_val[col], errors='coerce').fillna(0)
    
    print(f"Training {model_name} model...")
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Validation samples: {len(X_val):,}")
    print(f"  Features: {len(feature_cols)}")
    
    # Train model
    model.fit(X_train, y_train)
    print("✓ Model training completed")
    
    # Predictions
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Calculate metrics
    auc = roc_auc_score(y_val, y_pred_proba)
    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred, zero_division=0)
    recall = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)
    
    return {
        'model': model,
        'auc': auc,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'y_pred_proba': y_pred_proba,
        'y_pred': y_pred
    }

def train_model_oml(X_train, y_train, X_val, y_val, feature_cols):
    """Train model using OML4Py (if available)"""
    print("\n" + "=" * 60)
    print("Training Model (OML4Py XGBoost)")
    print("=" * 60)
    
    try:
        import oml
        import pandas as pd
        import numpy as np
    except ImportError:
        print("⚠️  OML4Py not available, falling back to local training")
        return None
    
    if not oml.isconnected():
        print("⚠️  OML not connected, falling back to local training")
        return None
    
    try:
        # Push training data to OML
        train_combined = X_train.copy()
        train_combined['CHURNED'] = y_train.values
        train_oml = oml.push(train_combined)
        
        # Push validation data to OML
        val_combined = X_val.copy()
        val_combined['CHURNED'] = y_val.values
        val_oml = oml.push(val_combined)
        
        # Get features and target
        X_train_oml = train_oml[feature_cols]
        y_train_oml = train_oml['CHURNED']
        X_val_oml = val_oml[feature_cols]
        
        print(f"Training XGBoost model with OML4Py...")
        print(f"  Training samples: {len(X_train_oml):,}")
        print(f"  Validation samples: {len(X_val_oml):,}")
        print(f"  Features: {len(feature_cols)}")
        
        # Create and train model
        xgb_model = oml.xgb('classification')
        xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
        print("✓ Model training completed")
        
        # Predictions
        y_pred_proba_oml = xgb_model.predict_proba(X_val_oml)
        y_pred_proba_pd = y_pred_proba_oml.pull()
        
        # Extract probabilities
        if isinstance(y_pred_proba_pd, pd.DataFrame):
            if 1 in y_pred_proba_pd.columns:
                y_pred_proba = y_pred_proba_pd[1].values
            elif len(y_pred_proba_pd.columns) == 2:
                y_pred_proba = y_pred_proba_pd.iloc[:, 1].values
            else:
                y_pred_proba = y_pred_proba_pd.values.flatten()
        else:
            y_pred_proba = np.array(y_pred_proba_pd)
        
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Calculate metrics
        from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
        
        auc = roc_auc_score(y_val, y_pred_proba)
        accuracy = accuracy_score(y_val, y_pred)
        precision = precision_score(y_val, y_pred, zero_division=0)
        recall = recall_score(y_val, y_pred, zero_division=0)
        f1 = f1_score(y_val, y_pred, zero_division=0)
        
        return {
            'model': xgb_model,
            'auc': auc,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'y_pred_proba': y_pred_proba,
            'y_pred': y_pred
        }
    except Exception as e:
        print(f"⚠️  OML4Py training failed: {e}")
        print("   Falling back to local training")
        return None

def main():
    """Main validation function"""
    print("=" * 60)
    print("Model Performance Validation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTarget: AUC > 0.70 on validation set")
    
    # Connect to database
    connection = get_connection()
    
    try:
        # Load data
        X, y, feature_cols = load_data_from_view(connection)
        
        # Split into train/validation (80/20)
        from sklearn.model_selection import train_test_split
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        
        print(f"\n✓ Data split:")
        print(f"  Training: {len(X_train):,} samples")
        print(f"  Validation: {len(X_val):,} samples")
        print(f"  Train churn rate: {y_train.mean() * 100:.2f}%")
        print(f"  Val churn rate: {y_val.mean() * 100:.2f}%")
        
        # Try OML4Py first, fallback to local
        results = train_model_oml(X_train, y_train, X_val, y_val, feature_cols)
        if results is None:
            results = train_model_local(X_train, y_train, X_val, y_val, feature_cols)
        
        # Display results
        print("\n" + "=" * 60)
        print("Model Performance Metrics")
        print("=" * 60)
        print(f"AUC-ROC:     {results['auc']:.4f}")
        print(f"Accuracy:    {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
        print(f"Precision:   {results['precision']:.4f} ({results['precision']*100:.2f}%)")
        print(f"Recall:      {results['recall']:.4f} ({results['recall']*100:.2f}%)")
        print(f"F1 Score:    {results['f1']:.4f}")
        
        # Validation result
        print("\n" + "=" * 60)
        print("Validation Result")
        print("=" * 60)
        
        auc = results['auc']
        threshold = 0.70
        
        if auc >= threshold:
            print(f"✓ PASS: AUC = {auc:.4f} >= {threshold:.2f}")
            print("\n✓ Dataset produces reasonable model performance!")
            print("  Ready for production model training (Task 3.x)")
        else:
            print(f"❌ FAIL: AUC = {auc:.4f} < {threshold:.2f}")
            print("\n⚠️  Dataset may need improvement:")
            print("  - Consider feature engineering")
            print("  - Check data quality")
            print("  - Review churn definition")
            print("  - Try different algorithms")
            sys.exit(1)
        
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
