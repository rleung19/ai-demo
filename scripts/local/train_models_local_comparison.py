#!/usr/bin/env python3
"""
Local Model Training and Comparison
Trains multiple models locally with proper hyperparameters and compares performance

Usage:
    python scripts/train_models_local_comparison.py

This script:
    1. Loads training data from CHURN_TRAINING_DATA view
    2. Splits into train/validation sets
    3. Trains multiple models (XGBoost, RandomForest, GradientBoosting, etc.)
    4. Compares performance (AUC, Accuracy, Precision, Recall, F1)
    5. Recommends best model
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

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
    
    return oracledb.connect(user=username, password=password, dsn=connection_string)

def load_data_from_view(connection):
    """Load training data from view"""
    print("\n" + "=" * 60)
    print("Loading Training Data from View")
    print("=" * 60)
    
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

def clean_data(X, feature_cols):
    """Clean and prepare data"""
    print("\nCleaning data...")
    
    # Replace infinity and NaN
    X = X.replace([np.inf, -np.inf], np.nan)
    
    # Ensure numeric
    for col in feature_cols:
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
    
    print("✓ Data cleaned")
    return X

def train_model(model_name, model, X_train, y_train, X_val, y_val):
    """Train a model and return metrics"""
    from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
    
    print(f"\n  Training {model_name}...")
    
    # Train
    model.fit(X_train, y_train)
    
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
        'model_name': model_name,
        'auc': auc,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'y_pred_proba': y_pred_proba,
        'y_pred': y_pred
    }

def train_all_models(X_train, y_train, X_val, y_val, feature_cols):
    """Train multiple models and compare"""
    print("\n" + "=" * 60)
    print("Training Multiple Models")
    print("=" * 60)
    
    results = []
    
    # 1. RandomForest
    try:
        from sklearn.ensemble import RandomForestClassifier
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        results.append(train_model("RandomForest", rf_model, X_train, y_train, X_val, y_val))
    except Exception as e:
        print(f"  ⚠️  RandomForest failed: {e}")
    
    # 2. XGBoost
    try:
        from xgboost import XGBClassifier
        xgb_model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        results.append(train_model("XGBoost", xgb_model, X_train, y_train, X_val, y_val))
    except Exception as e:
        print(f"  ⚠️  XGBoost failed: {e}")
    
    # 3. GradientBoosting
    try:
        from sklearn.ensemble import GradientBoostingClassifier
        gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        results.append(train_model("GradientBoosting", gb_model, X_train, y_train, X_val, y_val))
    except Exception as e:
        print(f"  ⚠️  GradientBoosting failed: {e}")
    
    # 4. LightGBM (if available)
    try:
        import lightgbm as lgb
        lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        results.append(train_model("LightGBM", lgb_model, X_train, y_train, X_val, y_val))
    except ImportError:
        print("  ⚠️  LightGBM not available (install with: pip install lightgbm)")
    except Exception as e:
        print(f"  ⚠️  LightGBM failed: {e}")
    
    # 5. CatBoost (if available)
    try:
        import catboost as cb
        cat_model = cb.CatBoostClassifier(
            iterations=100,
            depth=6,
            learning_rate=0.1,
            random_seed=42,
            verbose=False
        )
        results.append(train_model("CatBoost", cat_model, X_train, y_train, X_val, y_val))
    except ImportError:
        print("  ⚠️  CatBoost not available (install with: pip install catboost)")
    except Exception as e:
        print(f"  ⚠️  CatBoost failed: {e}")
    
    # 6. AdaBoost
    try:
        from sklearn.ensemble import AdaBoostClassifier
        from sklearn.tree import DecisionTreeClassifier
        # Use estimator parameter (new API) instead of base_estimator (deprecated)
        ada_model = AdaBoostClassifier(
            estimator=DecisionTreeClassifier(max_depth=3),
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        results.append(train_model("AdaBoost", ada_model, X_train, y_train, X_val, y_val))
    except Exception as e:
        print(f"  ⚠️  AdaBoost failed: {e}")
    
    return results

def display_comparison(results):
    """Display model comparison"""
    print("\n" + "=" * 80)
    print("Model Performance Comparison")
    print("=" * 80)
    
    # Sort by AUC
    results_sorted = sorted(results, key=lambda x: x['auc'], reverse=True)
    
    # Create comparison table
    print(f"\n{'Model':<20} {'AUC':<10} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<10}")
    print("-" * 80)
    
    for r in results_sorted:
        print(f"{r['model_name']:<20} {r['auc']:<10.4f} {r['accuracy']:<12.4f} {r['precision']:<12.4f} {r['recall']:<12.4f} {r['f1']:<10.4f}")
    
    # Best model
    best = results_sorted[0]
    print("\n" + "=" * 80)
    print(f"🏆 Best Model: {best['model_name']}")
    print("=" * 80)
    print(f"AUC-ROC:      {best['auc']:.4f} ({best['auc']*100:.2f}%)")
    print(f"Accuracy:     {best['accuracy']:.4f} ({best['accuracy']*100:.2f}%)")
    print(f"Precision:    {best['precision']:.4f} ({best['precision']*100:.2f}%)")
    print(f"Recall:       {best['recall']:.4f} ({best['recall']*100:.2f}%)")
    print(f"F1 Score:     {best['f1']:.4f}")
    
    return best

def main():
    """Main function"""
    print("=" * 80)
    print("Local Model Training and Comparison")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to database
    connection = get_connection()
    
    try:
        # Load data
        X, y, feature_cols = load_data_from_view(connection)
        
        # Clean data
        X = clean_data(X, feature_cols)
        
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
        
        # Train all models
        results = train_all_models(X_train, y_train, X_val, y_val, feature_cols)
        
        if not results:
            print("\n❌ ERROR: No models trained successfully")
            sys.exit(1)
        
        # Display comparison
        best_model = display_comparison(results)
        
        # Summary
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"✓ Trained {len(results)} models successfully")
        print(f"✓ Best model: {best_model['model_name']} (AUC: {best_model['auc']:.4f})")
        print(f"\nRecommendation: Use {best_model['model_name']} for production")
        print(f"  This model achieved AUC {best_model['auc']:.4f}, which is {'excellent' if best_model['auc'] > 0.80 else 'good' if best_model['auc'] > 0.70 else 'acceptable' if best_model['auc'] > 0.60 else 'poor'}")
        
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
