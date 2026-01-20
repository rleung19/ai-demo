#!/usr/bin/env python3
"""
Churn Prediction Model Training Pipeline (Local Training)
Section 3: ML Pipeline Development

This script implements the complete ML pipeline using LOCAL training:
- Task 3.1: ADB connection (oracledb, not OML4Py)
- Task 3.2: Data loading and preprocessing
- Task 3.3: Feature selection and validation
- Task 3.4: Model training (XGBoost - best performing model, AUC 0.9269)
- Task 3.5: Model evaluation
- Task 3.6: Threshold optimization
- Task 3.7: Model saving (pickle file + database metadata)

Usage:
    python scripts/train_churn_model_local.py
"""

import os
import sys
import pickle
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Find project root (script is in scripts/local/, so go up 2 levels)
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
# Task 3.1: ADB Connection (oracledb)
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

# ============================================================================
# Task 3.2: Data Loading and Preprocessing
# ============================================================================

def load_training_data(connection):
    """Load training data from view and preprocess"""
    print("\n" + "=" * 60)
    print("Task 3.2: Data Loading and Preprocessing")
    print("=" * 60)
    
    # Load from view
    print("Loading data from CHURN_TRAINING_DATA view...")
    query = "SELECT * FROM OML.CHURN_TRAINING_DATA"
    df = pd.read_sql(query, connection)
    
    print(f"✓ Loaded {len(df):,} rows")
    print(f"✓ Columns: {len(df.columns)}")
    
    # Identify feature columns (exclude USER_ID and CHURNED)
    exclude_cols = ['USER_ID', 'CHURNED']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    print(f"✓ Feature columns: {len(feature_cols)}")
    
    # Prepare X and y
    X_pd = df[feature_cols].copy()
    y_pd = df['CHURNED'].copy()
    
    # Clean data - replace NaN and infinity
    print("\nCleaning data...")
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(X_pd[col]):
            X_pd[col] = X_pd[col].replace([np.inf, -np.inf], np.nan)
            # Use robust type conversion
            X_pd[col] = pd.to_numeric(X_pd[col], errors='coerce').fillna(0)
    
    print("✓ Data cleaned (NaN and infinity handled)")
    
    # Check for any remaining issues
    null_count = X_pd.isna().sum().sum()
    if null_count > 0:
        print(f"⚠️  WARNING: {null_count} NULL values still present")
    else:
        print("✓ No NULL values remaining")
    
    return X_pd, y_pd, feature_cols

def split_data(X_pd, y_pd, test_size=0.2, random_state=42):
    """Split data into train/test sets"""
    from sklearn.model_selection import train_test_split
    
    print("\n" + "=" * 60)
    print("Splitting Data")
    print("=" * 60)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_pd, y_pd,
        test_size=test_size,
        random_state=random_state,
        stratify=y_pd
    )
    
    print(f"✓ Train size: {len(X_train):,} samples")
    print(f"✓ Test size: {len(X_test):,} samples")
    print(f"✓ Train churn rate: {y_train.mean() * 100:.2f}%")
    print(f"✓ Test churn rate: {y_test.mean() * 100:.2f}%")
    
    return X_train, X_test, y_train, y_test

# ============================================================================
# Task 3.3: Feature Selection and Validation
# ============================================================================

def validate_features(X_train_pd, feature_cols):
    """Validate and select features"""
    print("\n" + "=" * 60)
    print("Task 3.3: Feature Selection and Validation")
    print("=" * 60)
    
    valid_features = []
    
    for col in feature_cols:
        if col not in X_train_pd.columns:
            print(f"⚠️  Skipping missing feature: {col}")
            continue
        
        # Check if numeric
        if not pd.api.types.is_numeric_dtype(X_train_pd[col]):
            print(f"⚠️  Skipping non-numeric feature: {col}")
            continue
        
        # Check for constant values
        if X_train_pd[col].nunique() <= 1:
            print(f"⚠️  Skipping constant feature: {col}")
            continue
        
        # Check for very low variance
        if X_train_pd[col].std() < 1e-6:
            print(f"⚠️  Skipping low variance feature: {col}")
            continue
        
        valid_features.append(col)
    
    print(f"✓ Valid features: {len(valid_features)}/{len(feature_cols)}")
    
    if len(valid_features) < len(feature_cols):
        removed = set(feature_cols) - set(valid_features)
        print(f"  Removed: {removed}")
    
    return valid_features

# ============================================================================
# Task 3.4: Model Training (CatBoost - Best Performing Model)
# ============================================================================

def train_model(X_train, y_train, feature_cols):
    """Train XGBoost model (best performing model from comparison)"""
    print("\n" + "=" * 60)
    print("Task 3.4: Model Training (XGBoost)")
    print("=" * 60)
    
    # Try models in order of performance (from comparison results)
    model = None
    model_name = None
    
    # 1. Try XGBoost (best: AUC 0.9269)
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(
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
        model_name = "XGBoost"
    except (ImportError, Exception) as e:
        print(f"⚠️  XGBoost not available: {e}")
        print("   Trying CatBoost...")
        
        # 2. Try CatBoost (AUC 0.9255)
        try:
            import catboost as cb
            model = cb.CatBoostClassifier(
                iterations=100,
                depth=6,
                learning_rate=0.1,
                random_seed=42,
                verbose=False
            )
            model_name = "CatBoost"
        except ImportError:
            print("⚠️  CatBoost not available")
            print("   Falling back to GradientBoosting...")
            
            # 3. Fallback to GradientBoosting (AUC 0.9247)
            from sklearn.ensemble import GradientBoostingClassifier
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            )
            model_name = "GradientBoosting"
    
    print(f"Training {model_name} model...")
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Churn rate: {y_train.mean() * 100:.2f}%")
    
    # Train model
    model.fit(X_train[feature_cols], y_train)
    print("✓ Training completed!")
    
    return model, model_name

# ============================================================================
# Task 3.5: Model Evaluation
# ============================================================================

def evaluate_model(model, X_test, y_test, feature_cols):
    """Evaluate model performance"""
    print("\n" + "=" * 60)
    print("Task 3.5: Model Evaluation")
    print("=" * 60)
    
    from sklearn.metrics import (
        roc_auc_score, accuracy_score, precision_score,
        recall_score, f1_score, confusion_matrix
    )
    
    # Predictions
    y_pred_proba = model.predict_proba(X_test[feature_cols])[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Calculate metrics
    auc = roc_auc_score(y_test, y_pred_proba)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    # Display results
    print("\n" + "=" * 60)
    print("Model Performance Metrics")
    print("=" * 60)
    print(f"AUC-ROC:      {auc:.4f} ({auc*100:.2f}%)")
    print(f"Accuracy:     {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision:    {precision:.4f} ({precision*100:.2f}%)")
    print(f"Recall:       {recall:.4f} ({recall*100:.2f}%)")
    print(f"F1 Score:     {f1:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(f"                Predicted")
    print(f"              Non-Churn  Churn")
    print(f"Actual Non-Churn    {cm[0,0]:5d}     {cm[0,1]:5d}")
    print(f"       Churn        {cm[1,0]:5d}     {cm[1,1]:5d}")
    
    return {
        'auc': auc,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'y_test': y_test,
        'y_pred_proba': y_pred_proba,
        'y_pred': y_pred
    }

# ============================================================================
# Task 3.6: Threshold Optimization
# ============================================================================

def optimize_threshold(y_test, y_pred_proba):
    """Find optimal probability threshold"""
    print("\n" + "=" * 60)
    print("Task 3.6: Threshold Optimization")
    print("=" * 60)
    
    from sklearn.metrics import f1_score
    
    thresholds = np.arange(0.3, 0.7, 0.01)
    best_threshold = 0.5
    best_f1 = 0
    
    for threshold in thresholds:
        y_pred = (y_pred_proba >= threshold).astype(int)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    print(f"✓ Optimal threshold: {best_threshold:.3f}")
    print(f"✓ F1 score at optimal threshold: {best_f1:.4f}")
    
    return best_threshold

# ============================================================================
# Task 3.7: Model Saving
# ============================================================================

def register_model_in_db(connection, model_id, model_name, model_type, model_path, metadata_path, 
                         metadata, train_samples, test_samples, training_duration):
    """Register model in MODEL_REGISTRY table (Task 3.10)"""
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
        
        # Prepare training parameters as JSON
        training_params = json.dumps({
            'model_type': model_type,
            'feature_count': len(metadata.get('feature_cols', [])),
            'optimal_threshold': metadata.get('optimal_threshold', 0.5)
        })
        
        # Insert into registry
        insert_sql = """
            INSERT INTO OML.MODEL_REGISTRY (
                MODEL_ID, MODEL_NAME, MODEL_VERSION, MODEL_TYPE,
                MODEL_FILE_PATH, METADATA_FILE_PATH,
                AUC_SCORE, ACCURACY, PRECISION_SCORE, RECALL_SCORE, F1_SCORE, OPTIMAL_THRESHOLD,
                TRAINING_DATE, TRAINING_DURATION_SECONDS,
                TRAIN_SAMPLES, TEST_SAMPLES, FEATURE_COUNT,
                STATUS, IS_PRODUCTION, TRAINING_PARAMETERS
            ) VALUES (
                :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20
            )
        """
        
        perf = metadata.get('performance', {})
        training_date = datetime.now()
        
        cursor.execute(insert_sql, (
            model_id,  # MODEL_ID
            model_name,  # MODEL_NAME
            metadata.get('timestamp', model_id),  # MODEL_VERSION
            model_type,  # MODEL_TYPE
            str(model_path),  # MODEL_FILE_PATH
            str(metadata_path),  # METADATA_FILE_PATH
            perf.get('auc'),  # AUC_SCORE
            perf.get('accuracy'),  # ACCURACY
            perf.get('precision'),  # PRECISION_SCORE
            perf.get('recall'),  # RECALL_SCORE
            perf.get('f1'),  # F1_SCORE
            metadata.get('optimal_threshold', 0.5),  # OPTIMAL_THRESHOLD
            training_date,  # TRAINING_DATE
            training_duration,  # TRAINING_DURATION_SECONDS
            train_samples,  # TRAIN_SAMPLES
            test_samples,  # TEST_SAMPLES
            len(metadata.get('feature_cols', [])),  # FEATURE_COUNT
            'ACTIVE',  # STATUS
            0,  # IS_PRODUCTION (set manually for production models)
            training_params  # TRAINING_PARAMETERS
        ))
        
        connection.commit()
        cursor.close()
        print(f"✓ Model registered in MODEL_REGISTRY: {model_id}")
        return True
    except Exception as e:
        print(f"⚠️  WARNING: Failed to register model in database: {e}")
        # Don't fail the entire process if registration fails
        return False

def save_model(model, model_name, feature_cols, eval_results, optimal_threshold, 
               model_dir=None, connection=None, train_samples=None, test_samples=None, 
               training_start_time=None):
    """Save model to disk and store metadata in database"""
    print("\n" + "=" * 60)
    print("Task 3.7: Model Saving")
    print("=" * 60)
    
    if model_dir is None:
        model_dir = project_root / 'models'
    model_dir.mkdir(exist_ok=True)
    
    # Generate model filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_id = timestamp  # Use timestamp as model ID
    model_filename = f'churn_model_{model_name.lower()}_{timestamp}.pkl'
    model_path = model_dir / model_filename
    
    # Calculate training duration
    training_duration = None
    if training_start_time:
        training_duration = (datetime.now() - training_start_time).total_seconds()
    
    # Save model
    try:
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Model saved: {model_path}")
    except Exception as e:
        print(f"❌ ERROR: Failed to save model: {e}")
        return None
    
    # Save metadata
    metadata = {
        'model_name': model_name,
        'model_path': str(model_path),
        'feature_cols': feature_cols,
        'timestamp': timestamp,
        'performance': {
            'auc': float(eval_results['auc']),
            'accuracy': float(eval_results['accuracy']),
            'precision': float(eval_results['precision']),
            'recall': float(eval_results['recall']),
            'f1': float(eval_results['f1'])
        },
        'optimal_threshold': float(optimal_threshold)
    }
    
    metadata_filename = f'churn_model_{model_name.lower()}_{timestamp}_metadata.json'
    metadata_path = model_dir / metadata_filename
    
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved: {metadata_path}")
    except Exception as e:
        print(f"⚠️  WARNING: Failed to save metadata: {e}")
    
    # Register in database (Task 3.10)
    if connection:
        register_model_in_db(
            connection, model_id, model_name, model_name,
            model_path, metadata_path, metadata,
            train_samples or 0, test_samples or 0, training_duration or 0
        )
    
    return {
        'model_path': model_path,
        'metadata_path': metadata_path,
        'metadata': metadata,
        'model_id': model_id
    }

# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    """Main training pipeline"""
    training_start_time = datetime.now()
    
    print("=" * 80)
    print("Churn Prediction Model Training Pipeline (Local Training)")
    print("=" * 80)
    print(f"Started at: {training_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to database
    connection = get_connection()
    
    try:
        # Task 3.2: Load and preprocess data
        X_pd, y_pd, all_feature_cols = load_training_data(connection)
        X_train, X_test, y_train, y_test = split_data(X_pd, y_pd)
        
        # Task 3.3: Validate features
        feature_cols = validate_features(X_train, all_feature_cols)
        
        # Task 3.4: Train model
        model, model_name = train_model(X_train, y_train, feature_cols)
        
        # Task 3.5: Evaluate model
        eval_results = evaluate_model(model, X_test, y_test, feature_cols)
        
        # Task 3.6: Optimize threshold
        optimal_threshold = optimize_threshold(eval_results['y_test'], eval_results['y_pred_proba'])
        
        # Task 3.7: Save model (with registry registration)
        save_info = save_model(
            model,
            model_name,
            feature_cols,
            eval_results,
            optimal_threshold,
            connection=connection,
            train_samples=len(X_train),
            test_samples=len(X_test),
            training_start_time=training_start_time
        )
        
        # Summary
        print("\n" + "=" * 80)
        print("Training Pipeline Summary")
        print("=" * 80)
        print(f"Model: {model_name}")
        print(f"Model Performance:")
        print(f"  AUC-ROC:     {eval_results['auc']:.4f}")
        print(f"  Accuracy:    {eval_results['accuracy']:.4f}")
        print(f"  F1 Score:    {eval_results['f1']:.4f}")
        print(f"  Optimal Threshold: {optimal_threshold:.3f}")
        if save_info:
            print(f"\nModel Files:")
            print(f"  Model: {save_info['model_path']}")
            print(f"  Metadata: {save_info['metadata_path']}")
        
        print("\n✓ Training pipeline completed successfully!")
        
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
