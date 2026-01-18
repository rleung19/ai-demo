#!/usr/bin/env python3
"""
Automated Churn Model Training (Local) - ALTERNATIVE APPROACH
================================================================

⚠️  NOTE: This is an ALTERNATIVE approach that trains models locally.
The RECOMMENDED approach is to use OML4Py in OML Notebooks (see docs/HOW_TO_USE_OML4PY.md).

This script trains the churn model locally without requiring OML4Py.
It can be scheduled via cron, Airflow, or any task scheduler.

Use this only if:
- OML4Py is not available in your environment
- You need full control over the training process
- You prefer local model storage over OML Datastore

Features:
- Connects to ADB via oracledb
- Pulls training data from database
- Trains model locally with XGBoost
- Stores model metadata in database
- Generates predictions and stores in CHURN_PREDICTIONS table
- Full logging and error handling

Usage:
    # Run manually:
    python scripts/train_churn_model_local.py
    
    # Schedule via cron (daily at 2 AM):
    0 2 * * * /path/to/python /path/to/scripts/train_churn_model_local.py >> /path/to/logs/training.log 2>&1
    
    # Schedule via Airflow:
    # Add as PythonOperator task in DAG
"""

import os
import sys
import json
import pickle
import logging
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

# Configure logging
log_dir = project_root / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'train_churn_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# Database Connection
# ============================================================================

def get_db_connection():
    """Connect to Oracle ADB using oracledb"""
    try:
        import oracledb
    except ImportError:
        logger.error("oracledb not installed. Install with: pip install oracledb")
        sys.exit(1)
    
    # Get connection parameters
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    
    if not password or not connection_string:
        logger.error("ADB_PASSWORD and ADB_CONNECTION_STRING must be set in .env file")
        sys.exit(1)
    
    try:
        # Try thick mode first (for wallet support)
        wallet_path = os.getenv('ADB_WALLET_PATH')
        if wallet_path and Path(wallet_path).exists():
            try:
                oracledb.init_oracle_client(lib_dir=os.getenv('ORACLE_CLIENT_LIB_DIR'))
            except Exception as e:
                logger.warning(f"Could not initialize Oracle client: {e}")
                logger.info("Falling back to thin mode...")
        
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        logger.info("✓ Connected to Oracle ADB")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

# ============================================================================
# Data Loading
# ============================================================================

def load_training_data(connection):
    """Load training data from CHURN_TRAINING_DATA view"""
    logger.info("Loading training data from CHURN_TRAINING_DATA view...")
    
    query = """
    SELECT * FROM OML.CHURN_TRAINING_DATA
    """
    
    try:
        df = pd.read_sql(query, connection)
        logger.info(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Failed to load training data: {e}")
        raise

def load_user_features(connection):
    """Load user features for scoring"""
    logger.info("Loading user features from CHURN_USER_FEATURES view...")
    
    query = """
    SELECT * FROM OML.CHURN_USER_FEATURES
    """
    
    try:
        df = pd.read_sql(query, connection)
        logger.info(f"✓ Loaded {len(df):,} user profiles")
        return df
    except Exception as e:
        logger.error(f"Failed to load user features: {e}")
        raise

# ============================================================================
# Model Training
# ============================================================================

def train_model(X_train, y_train, X_val, y_val, feature_cols):
    """Train XGBoost model locally"""
    logger.info("=" * 60)
    logger.info("Training XGBoost Model")
    logger.info("=" * 60)
    
    # Try XGBoost first, fallback to RandomForest
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
        logger.info("Using XGBoost classifier")
    except (ImportError, Exception) as e:
        logger.warning(f"XGBoost not available: {e}")
        logger.info("Falling back to RandomForest...")
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
            logger.error("Neither XGBoost nor sklearn available")
            sys.exit(1)
    
    # Clean data
    X_train = X_train.replace([np.inf, -np.inf], np.nan).fillna(0)
    X_val = X_val.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Ensure numeric
    for col in feature_cols:
        X_train[col] = pd.to_numeric(X_train[col], errors='coerce').fillna(0)
        X_val[col] = pd.to_numeric(X_val[col], errors='coerce').fillna(0)
    
    logger.info(f"Training {model_name} model...")
    logger.info(f"  Training samples: {len(X_train):,}")
    logger.info(f"  Validation samples: {len(X_val):,}")
    logger.info(f"  Features: {len(feature_cols)}")
    
    # Train
    model.fit(X_train, y_train)
    logger.info("✓ Model training completed")
    
    # Evaluate
    from sklearn.metrics import (
        roc_auc_score, accuracy_score, precision_score, 
        recall_score, f1_score, confusion_matrix
    )
    
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    auc = roc_auc_score(y_val, y_pred_proba)
    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred, zero_division=0)
    recall = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)
    cm = confusion_matrix(y_val, y_pred)
    
    logger.info("\nModel Performance:")
    logger.info(f"  AUC-ROC: {auc:.4f}")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1-Score: {f1:.4f}")
    logger.info(f"\nConfusion Matrix:\n{cm}")
    
    # Threshold optimization
    thresholds = np.arange(0.3, 0.7, 0.05)
    best_threshold = 0.5
    best_f1 = f1
    
    for threshold in thresholds:
        y_pred_t = (y_pred_proba >= threshold).astype(int)
        f1_t = f1_score(y_val, y_pred_t, zero_division=0)
        if f1_t > best_f1:
            best_f1 = f1_t
            best_threshold = threshold
    
    logger.info(f"\nOptimal threshold: {best_threshold:.3f} (F1: {best_f1:.4f})")
    
    return {
        'model': model,
        'model_name': model_name,
        'auc': auc,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'best_threshold': best_threshold,
        'feature_cols': feature_cols
    }

# ============================================================================
# Model Storage
# ============================================================================

def save_model_metadata(connection, model_info, model_version):
    """Save model metadata to database"""
    logger.info("Saving model metadata to database...")
    
    # Create model metadata table if it doesn't exist
    # Oracle doesn't support IF NOT EXISTS, so we check first
    check_table_sql = """
    SELECT COUNT(*) FROM ALL_TABLES 
    WHERE OWNER = 'OML' AND TABLE_NAME = 'MODEL_METADATA'
    """
    
    create_table_sql = """
    CREATE TABLE OML.MODEL_METADATA (
        MODEL_VERSION VARCHAR2(50) PRIMARY KEY,
        MODEL_NAME VARCHAR2(100),
        TRAINING_DATE TIMESTAMP,
        AUC_SCORE NUMBER(10,4),
        ACCURACY NUMBER(10,4),
        PRECISION_SCORE NUMBER(10,4),
        RECALL_SCORE NUMBER(10,4),
        F1_SCORE NUMBER(10,4),
        OPTIMAL_THRESHOLD NUMBER(10,4),
        FEATURE_COUNT NUMBER(10),
        MODEL_TYPE VARCHAR2(50),
        METADATA_JSON CLOB
    )
    """
    
    try:
        cursor = connection.cursor()
        cursor.execute(check_table_sql)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            cursor.execute(create_table_sql)
            connection.commit()
            logger.info("✓ Model metadata table created")
        else:
            logger.info("✓ Model metadata table already exists")
    except Exception as e:
        # Table might already exist (race condition)
        logger.debug(f"Table creation check: {e}")
        try:
            cursor.execute(create_table_sql)
            connection.commit()
            logger.info("✓ Model metadata table created")
        except Exception as e2:
            if "ORA-00955" in str(e2):  # Table already exists
                logger.info("✓ Model metadata table already exists")
            else:
                logger.warning(f"Could not create table: {e2}")
    
    # Insert metadata
    insert_sql = """
    INSERT INTO OML.MODEL_METADATA (
        MODEL_VERSION, MODEL_NAME, TRAINING_DATE,
        AUC_SCORE, ACCURACY, PRECISION_SCORE, RECALL_SCORE, F1_SCORE,
        OPTIMAL_THRESHOLD, FEATURE_COUNT, MODEL_TYPE, METADATA_JSON
    ) VALUES (
        :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12
    )
    """
    
    metadata_json = json.dumps({
        'feature_cols': model_info['feature_cols'],
        'training_timestamp': datetime.now().isoformat()
    })
    
    try:
        cursor = connection.cursor()
        cursor.execute(insert_sql, (
            model_version,
            model_info['model_name'],
            datetime.now(),
            model_info['auc'],
            model_info['accuracy'],
            model_info['precision'],
            model_info['recall'],
            model_info['f1'],
            model_info['best_threshold'],
            len(model_info['feature_cols']),
            model_info['model_name'],
            metadata_json
        ))
        connection.commit()
        logger.info(f"✓ Model metadata saved (version: {model_version})")
    except Exception as e:
        logger.error(f"Failed to save model metadata: {e}")
        raise

def save_model_file(model, model_version, output_dir=None):
    """Save model to file (optional, for backup)"""
    if output_dir is None:
        output_dir = project_root / 'models'
    output_dir.mkdir(exist_ok=True)
    
    model_file = output_dir / f'churn_model_{model_version}.pkl'
    
    try:
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"✓ Model saved to {model_file}")
        return str(model_file)
    except Exception as e:
        logger.warning(f"Could not save model file: {e}")
        return None

# ============================================================================
# Scoring
# ============================================================================

def score_users(connection, model, feature_cols, model_info):
    """Score all users and store predictions"""
    logger.info("=" * 60)
    logger.info("Scoring Users")
    logger.info("=" * 60)
    
    # Load user features
    user_features = load_user_features(connection)
    
    if len(user_features) == 0:
        logger.warning("No user features found")
        return
    
    # Prepare features
    X = user_features[feature_cols].copy()
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    for col in feature_cols:
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
    
    # Predict
    logger.info(f"Generating predictions for {len(X):,} users...")
    probabilities = model.predict_proba(X)[:, 1]
    labels = (probabilities >= model_info['best_threshold']).astype(int)
    
    # Calculate risk scores (0-100)
    risk_scores = (probabilities * 100).round(2)
    
    # Prepare data for insert
    predictions_df = pd.DataFrame({
        'USER_ID': user_features['USER_ID'].values,
        'PREDICTED_CHURN_PROBABILITY': probabilities,
        'PREDICTED_CHURN_LABEL': labels,
        'RISK_SCORE': risk_scores,
        'PREDICTION_DATE': datetime.now(),
        'MODEL_VERSION': f"local_v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    })
    
    # Clear existing predictions (optional - comment out to keep history)
    logger.info("Clearing existing predictions...")
    try:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE OML.CHURN_PREDICTIONS")
        connection.commit()
        logger.info("✓ Cleared existing predictions")
    except Exception as e:
        logger.warning(f"Could not clear predictions: {e}")
    
    # Insert predictions
    logger.info("Inserting predictions...")
    insert_sql = """
    INSERT INTO OML.CHURN_PREDICTIONS (
        USER_ID, PREDICTED_CHURN_PROBABILITY, PREDICTED_CHURN_LABEL,
        RISK_SCORE, PREDICTION_DATE, MODEL_VERSION
    ) VALUES (:1, :2, :3, :4, :5, :6)
    """
    
    try:
        cursor = connection.cursor()
        cursor.executemany(insert_sql, [
            (row['USER_ID'], row['PREDICTED_CHURN_PROBABILITY'], 
             row['PREDICTED_CHURN_LABEL'], row['RISK_SCORE'],
             row['PREDICTION_DATE'], row['MODEL_VERSION'])
            for _, row in predictions_df.iterrows()
        ])
        connection.commit()
        logger.info(f"✓ Inserted {len(predictions_df):,} predictions")
        
        # Summary
        at_risk = predictions_df['PREDICTED_CHURN_LABEL'].sum()
        avg_risk = predictions_df['PREDICTED_CHURN_PROBABILITY'].mean() * 100
        logger.info(f"\nPrediction Summary:")
        logger.info(f"  Total users: {len(predictions_df):,}")
        logger.info(f"  At risk (churn predicted): {at_risk:,} ({at_risk/len(predictions_df)*100:.1f}%)")
        logger.info(f"  Average risk score: {avg_risk:.2f}%")
        
    except Exception as e:
        logger.error(f"Failed to insert predictions: {e}")
        raise

# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    """Main training pipeline"""
    logger.info("=" * 60)
    logger.info("Automated Churn Model Training (Local)")
    logger.info("=" * 60)
    logger.info(f"Start time: {datetime.now()}")
    
    connection = None
    try:
        # Connect to database
        connection = get_db_connection()
        
        # Load training data
        train_df = load_training_data(connection)
        
        # Prepare features
        exclude_cols = ['USER_ID', 'CHURNED']
        feature_cols = [col for col in train_df.columns if col not in exclude_cols]
        
        X = train_df[feature_cols].copy()
        y = train_df['CHURNED'].values
        
        # Train/validation split
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Train/validation split: {len(X_train):,} / {len(X_val):,}")
        
        # Train model
        model_info = train_model(X_train, y_train, X_val, y_val, feature_cols)
        
        # Check performance threshold
        if model_info['auc'] < 0.70:
            logger.warning(f"⚠️  Model AUC ({model_info['auc']:.4f}) below threshold (0.70)")
            logger.warning("Consider reviewing data quality or feature engineering")
        else:
            logger.info(f"✓ Model performance acceptable (AUC: {model_info['auc']:.4f})")
        
        # Save model metadata
        model_version = f"local_v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_model_metadata(connection, model_info, model_version)
        
        # Save model file (optional)
        model_file = save_model_file(model_info['model'], model_version)
        
        # Score users
        score_users(connection, model_info['model'], feature_cols, model_info)
        
        logger.info("=" * 60)
        logger.info("Training Pipeline Completed Successfully")
        logger.info("=" * 60)
        logger.info(f"End time: {datetime.now()}")
        logger.info(f"Log file: {log_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1
        
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed")

if __name__ == '__main__':
    sys.exit(main())
