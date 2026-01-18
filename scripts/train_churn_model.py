#!/usr/bin/env python3
"""
Churn Prediction Model Training Pipeline
Section 3: ML Pipeline Development

This script implements the complete ML pipeline:
- Task 3.1: ADB connection (OML4Py)
- Task 3.2: Data loading and preprocessing
- Task 3.3: Feature selection and validation
- Task 3.4: Model training (XGBoost via OML4Py)
- Task 3.5: Model evaluation
- Task 3.6: Threshold optimization
- Task 3.7: Model saving to OML datastore

Usage:
    # In OML Notebooks (recommended):
    %python
    exec(open('scripts/train_churn_model.py').read())
    
    # Or run as standalone (requires OML4Py):
    python scripts/train_churn_model.py
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

# ============================================================================
# Task 3.1: ADB Connection (OML4Py)
# ============================================================================

def connect_oml():
    """Connect to OML4Py"""
    print("=" * 60)
    print("Task 3.1: OML4Py Connection")
    print("=" * 60)
    
    try:
        import oml
        print("✓ OML4Py imported successfully")
    except ImportError:
        print("❌ ERROR: OML4Py not available")
        print("   OML4Py is typically only available in OML Notebooks")
        print("   For standalone Python, use oracledb for database access")
        print("   Model training should be done in OML Notebooks")
        return None
    
    # Check connection
    if oml.isconnected():
        print("✓ OML connection is active")
        try:
            version = oml.__version__
            print(f"✓ OML version: {version}")
        except:
            pass
        return oml
    else:
        print("⚠️  WARNING: OML reports not connected")
        print("   Connection will be established when needed")
        print("   This may be normal if running outside OML Notebooks")
        return oml  # Return anyway, connection may be established later

# ============================================================================
# Task 3.2: Data Loading and Preprocessing
# ============================================================================

def load_training_data(oml):
    """Load training data from view and preprocess"""
    print("\n" + "=" * 60)
    print("Task 3.2: Data Loading and Preprocessing")
    print("=" * 60)
    
    # Load from view
    print("Loading data from CHURN_TRAINING_DATA view...")
    train_data_oml = oml.sync(view='CHURN_TRAINING_DATA')
    train_data_pd = train_data_oml.pull()
    
    print(f"✓ Loaded {len(train_data_pd):,} rows")
    print(f"✓ Columns: {len(train_data_pd.columns)}")
    
    # Identify feature columns (exclude USER_ID and CHURNED)
    exclude_cols = ['USER_ID', 'CHURNED']
    feature_cols = [col for col in train_data_pd.columns if col not in exclude_cols]
    
    print(f"✓ Feature columns: {len(feature_cols)}")
    
    # Prepare X and y
    X_pd = train_data_pd[feature_cols].copy()
    y_pd = train_data_pd['CHURNED'].copy()
    
    # Clean data - replace NaN and infinity
    print("\nCleaning data...")
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(X_pd[col]):
            X_pd[col] = X_pd[col].replace([np.inf, -np.inf], np.nan)
            X_pd[col] = X_pd[col].fillna(0)
    
    print("✓ Data cleaned (NaN and infinity handled)")
    
    # Check for any remaining issues
    null_count = X_pd.isna().sum().sum()
    if null_count > 0:
        print(f"⚠️  WARNING: {null_count} NULL values still present")
    else:
        print("✓ No NULL values remaining")
    
    return X_pd, y_pd, feature_cols, train_data_oml

def split_data(X_pd, y_pd, test_size=0.2, random_state=42):
    """Split data into train/test sets"""
    from sklearn.model_selection import train_test_split
    
    print("\nSplitting data into train/test sets...")
    X_train_pd, X_test_pd, y_train_pd, y_test_pd = train_test_split(
        X_pd, y_pd,
        test_size=test_size,
        random_state=random_state,
        stratify=y_pd
    )
    
    print(f"✓ Train size: {len(X_train_pd):,} ({len(X_train_pd)/len(X_pd)*100:.1f}%)")
    print(f"✓ Test size: {len(X_test_pd):,} ({len(X_test_pd)/len(X_pd)*100:.1f}%)")
    print(f"✓ Train churn rate: {y_train_pd.mean() * 100:.2f}%")
    print(f"✓ Test churn rate: {y_test_pd.mean() * 100:.2f}%")
    
    return X_train_pd, X_test_pd, y_train_pd, y_test_pd

# ============================================================================
# Task 3.3: Feature Selection and Validation
# ============================================================================

def validate_features(X_train_pd, feature_cols):
    """Validate features for model training"""
    print("\n" + "=" * 60)
    print("Task 3.3: Feature Selection and Validation")
    print("=" * 60)
    
    # Check all features are numeric
    numeric_cols = []
    non_numeric_cols = []
    
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(X_train_pd[col]):
            numeric_cols.append(col)
        else:
            non_numeric_cols.append(col)
    
    print(f"✓ Numeric features: {len(numeric_cols)}")
    if non_numeric_cols:
        print(f"⚠️  Non-numeric features found: {non_numeric_cols}")
        print("   These will be excluded from training")
    
    # Check for constant features (zero variance)
    constant_features = []
    for col in numeric_cols:
        if X_train_pd[col].nunique() <= 1:
            constant_features.append(col)
    
    if constant_features:
        print(f"⚠️  Constant features found: {constant_features}")
        print("   These will be excluded from training")
        numeric_cols = [col for col in numeric_cols if col not in constant_features]
    
    # Final feature list
    valid_features = numeric_cols
    print(f"\n✓ Valid features for training: {len(valid_features)}")
    print(f"  First 10: {', '.join(valid_features[:10])}")
    
    return valid_features

# ============================================================================
# Task 3.4: Model Training (XGBoost via OML4Py)
# ============================================================================

def train_xgboost_model(oml, X_train_pd, y_train_pd, feature_cols):
    """Train XGBoost model using OML4Py"""
    print("\n" + "=" * 60)
    print("Task 3.4: Model Training (XGBoost via OML4Py)")
    print("=" * 60)
    
    # Merge X_train and y_train for database push
    train_combined_pd = X_train_pd.copy()
    train_combined_pd['CHURNED'] = y_train_pd.values
    
    # Push to database
    print("Pushing training data to OML...")
    train_oml = oml.push(train_combined_pd)
    print(f"✓ Training data pushed: {train_oml.shape}")
    
    # Create XGBoost model
    print("\nCreating XGBoost model...")
    xgb_model = oml.xgb('classification')
    
    # Get features and target from OML DataFrame
    X_train_oml = train_oml[feature_cols]
    y_train_oml = train_oml['CHURNED']
    
    print(f"✓ X_train_oml shape: {X_train_oml.shape}")
    print(f"✓ Features: {len(feature_cols)}")
    print(f"✓ Training started...")
    
    # Fit the model
    xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
    print("✓ Training completed!")
    
    return xgb_model, train_oml

# ============================================================================
# Task 3.5: Model Evaluation
# ============================================================================

def evaluate_model(oml, xgb_model, X_test_pd, y_test_pd, feature_cols):
    """Evaluate model performance"""
    print("\n" + "=" * 60)
    print("Task 3.5: Model Evaluation")
    print("=" * 60)
    
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score,
        f1_score, roc_auc_score, confusion_matrix, classification_report
    )
    
    # Prepare test data in OML format
    test_combined_pd = X_test_pd.copy()
    test_combined_pd['CHURNED'] = y_test_pd.values
    test_oml = oml.push(test_combined_pd)
    X_test_oml = test_oml[feature_cols]
    
    # Get predictions
    print("Generating predictions...")
    y_pred_proba_oml = xgb_model.predict_proba(X_test_oml)
    
    # Convert OML Vector to numpy array
    y_pred_proba_pd = y_pred_proba_oml.pull()
    if isinstance(y_pred_proba_pd, pd.DataFrame):
        if 1 in y_pred_proba_pd.columns:
            y_pred_proba = y_pred_proba_pd[1].values
        elif len(y_pred_proba_pd.columns) == 2:
            y_pred_proba = y_pred_proba_pd.iloc[:, 1].values
        else:
            y_pred_proba = y_pred_proba_pd.values.flatten()
    else:
        y_pred_proba = np.array(y_pred_proba_pd)
    
    # Convert probabilities to binary predictions (threshold = 0.5)
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Convert y_test to numpy array
    y_test_vals = y_test_pd.values
    
    # Calculate metrics
    accuracy = accuracy_score(y_test_vals, y_pred)
    precision = precision_score(y_test_vals, y_pred, zero_division=0)
    recall = recall_score(y_test_vals, y_pred, zero_division=0)
    f1 = f1_score(y_test_vals, y_pred, zero_division=0)
    auc = roc_auc_score(y_test_vals, y_pred_proba)
    
    # Confusion matrix
    cm = confusion_matrix(y_test_vals, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print("\nModel Performance Metrics:")
    print(f"  AUC-ROC:     {auc:.4f} ({auc*100:.2f}%)")
    print(f"  Accuracy:    {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision:   {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:      {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1 Score:    {f1:.4f}")
    
    print("\nConfusion Matrix:")
    print("                Predicted")
    print("              Non-Churn  Churn")
    print(f"Actual Non-Churn   {tn:5d}   {fp:5d}")
    print(f"       Churn       {fn:5d}   {tp:5d}")
    
    return {
        'auc': auc,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'y_pred_proba': y_pred_proba,
        'y_pred': y_pred,
        'y_test': y_test_vals,
        'cm': cm
    }

# ============================================================================
# Task 3.6: Threshold Optimization
# ============================================================================

def optimize_threshold(y_test, y_pred_proba):
    """Find optimal probability threshold"""
    print("\n" + "=" * 60)
    print("Task 3.6: Threshold Optimization")
    print("=" * 60)
    
    from sklearn.metrics import precision_recall_curve, f1_score
    
    # Calculate precision-recall curve
    precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
    
    # Find threshold that maximizes F1 score
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
    optimal_idx = np.argmax(f1_scores)
    optimal_threshold = thresholds[optimal_idx] if optimal_idx < len(thresholds) else 0.5
    
    # Also try common thresholds
    test_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    best_threshold = 0.5
    best_f1 = 0
    
    for threshold in test_thresholds:
        y_pred_thresh = (y_pred_proba >= threshold).astype(int)
        f1 = f1_score(y_test, y_pred_thresh, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    # Use the better threshold
    if f1_scores[optimal_idx] > best_f1:
        optimal_threshold = thresholds[optimal_idx] if optimal_idx < len(thresholds) else 0.5
    else:
        optimal_threshold = best_threshold
    
    print(f"✓ Optimal threshold: {optimal_threshold:.3f}")
    print(f"  (Default: 0.5)")
    
    return optimal_threshold

# ============================================================================
# Task 3.7: Model Saving to OML Datastore
# ============================================================================

def save_model(oml, xgb_model, model_name='churn_xgboost_v1', description='Churn prediction XGBoost model'):
    """Save model to OML datastore"""
    print("\n" + "=" * 60)
    print("Task 3.7: Model Saving to OML Datastore")
    print("=" * 60)
    
    try:
        oml.ds.save(
            {'model': xgb_model},
            model_name,
            description=description,
            overwrite=True
        )
        print(f"✓ Model saved to OML datastore: {model_name}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to save model: {e}")
        return False

# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("Churn Prediction Model Training Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Task 3.1: Connect to OML
    oml = connect_oml()
    if oml is None:
        print("\n❌ Cannot proceed without OML4Py connection")
        print("   This script should be run in OML Notebooks")
        sys.exit(1)
    
    try:
        # Task 3.2: Load and preprocess data
        X_pd, y_pd, all_feature_cols, train_data_oml = load_training_data(oml)
        X_train_pd, X_test_pd, y_train_pd, y_test_pd = split_data(X_pd, y_pd)
        
        # Task 3.3: Validate features
        feature_cols = validate_features(X_train_pd, all_feature_cols)
        
        # Task 3.4: Train model
        xgb_model, train_oml = train_xgboost_model(oml, X_train_pd, y_train_pd, feature_cols)
        
        # Task 3.5: Evaluate model
        eval_results = evaluate_model(oml, xgb_model, X_test_pd, y_test_pd, feature_cols)
        
        # Task 3.6: Optimize threshold
        optimal_threshold = optimize_threshold(eval_results['y_test'], eval_results['y_pred_proba'])
        
        # Task 3.7: Save model
        model_saved = save_model(
            oml,
            xgb_model,
            model_name='churn_xgboost_v1',
            description=f'Churn prediction XGBoost model - AUC: {eval_results["auc"]:.4f}'
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("Training Pipeline Summary")
        print("=" * 60)
        print(f"Model Performance:")
        print(f"  AUC-ROC:     {eval_results['auc']:.4f}")
        print(f"  Accuracy:    {eval_results['accuracy']:.4f}")
        print(f"  F1 Score:    {eval_results['f1']:.4f}")
        print(f"  Optimal Threshold: {optimal_threshold:.3f}")
        print(f"Model Saved:   {'✓ YES' if model_saved else '❌ NO'}")
        
        if eval_results['auc'] >= 0.70:
            print("\n✓ Model meets performance target (AUC >= 0.70)")
            print("  Ready for deployment (Task 3.8: Model Scoring)")
        else:
            print("\n⚠️  Model below performance target (AUC < 0.70)")
            print("  Consider feature engineering or hyperparameter tuning")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'model': xgb_model,
            'eval_results': eval_results,
            'optimal_threshold': optimal_threshold,
            'feature_cols': feature_cols,
            'model_saved': model_saved
        }
    
    except Exception as e:
        print(f"\n❌ ERROR: Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # Check if running in OML Notebooks environment
    try:
        import oml
        if oml.isconnected():
            main()
        else:
            print("⚠️  OML not connected")
            print("   This script should be run in OML Notebooks")
            print("   Or ensure OML4Py is properly configured")
    except ImportError:
        print("⚠️  OML4Py not available")
        print("   This script requires OML4Py (typically in OML Notebooks)")
        print("   For standalone Python, use oracledb + sklearn/xgboost")
        sys.exit(1)
