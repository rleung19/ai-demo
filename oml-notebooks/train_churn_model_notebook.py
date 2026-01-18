"""
OML Notebook Cell: Train Churn Model
Copy this into OML Notebooks as Python cells

This is the complete training pipeline for OML Notebooks environment.
"""

# ============================================================================
# Cell 1: Import and Setup
# ============================================================================
"""
%python

import oml
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
from datetime import datetime

print("=" * 60)
print("Churn Prediction Model Training")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Check OML connection
if oml.isconnected():
    print("✓ OML connected")
else:
    print("⚠️  OML not connected")
"""

# ============================================================================
# Cell 2: Load Training Data
# ============================================================================
"""
%python

# Load data from view
print("Loading data from CHURN_TRAINING_DATA view...")
train_data_oml = oml.sync(view='CHURN_TRAINING_DATA')
train_data_pd = train_data_oml.pull()

print(f"✓ Loaded {len(train_data_pd):,} rows")
print(f"✓ Columns: {len(train_data_pd.columns)}")

# Identify feature columns
exclude_cols = ['USER_ID', 'CHURNED']
feature_cols = [col for col in train_data_pd.columns if col not in exclude_cols]

print(f"✓ Feature columns: {len(feature_cols)}")

# Prepare X and y
X_pd = train_data_pd[feature_cols].copy()
y_pd = train_data_pd['CHURNED'].copy()

# Clean data
print("\nCleaning data...")
for col in feature_cols:
    if pd.api.types.is_numeric_dtype(X_pd[col]):
        X_pd[col] = X_pd[col].replace([np.inf, -np.inf], np.nan)
        X_pd[col] = X_pd[col].fillna(0)

print("✓ Data cleaned")
"""

# ============================================================================
# Cell 3: Split Data
# ============================================================================
"""
%python

# Split into train/test
X_train_pd, X_test_pd, y_train_pd, y_test_pd = train_test_split(
    X_pd, y_pd,
    test_size=0.2,
    random_state=42,
    stratify=y_pd
)

print(f"✓ Train size: {len(X_train_pd):,}")
print(f"✓ Test size: {len(X_test_pd):,}")
print(f"✓ Train churn rate: {y_train_pd.mean() * 100:.2f}%")
print(f"✓ Test churn rate: {y_test_pd.mean() * 100:.2f}%")
"""

# ============================================================================
# Cell 4: Train XGBoost Model
# ============================================================================
"""
%python

# Merge X_train and y_train for database push
train_combined_pd = X_train_pd.copy()
train_combined_pd['CHURNED'] = y_train_pd.values

# Push to database
print("Pushing training data to OML...")
train_oml = oml.push(train_combined_pd)
print(f"✓ Training data pushed: {train_oml.shape}")

# Create XGBoost model
xgb_model = oml.xgb('classification')

# Get features and target
X_train_oml = train_oml[feature_cols]
y_train_oml = train_oml['CHURNED']

print(f"✓ X_train_oml shape: {X_train_oml.shape}")
print("Training started...")

# Fit the model
xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
print("✓ Training completed!")
"""

# ============================================================================
# Cell 5: Evaluate Model
# ============================================================================
"""
%python

# Prepare test data
test_combined_pd = X_test_pd.copy()
test_combined_pd['CHURNED'] = y_test_pd.values
test_oml = oml.push(test_combined_pd)
X_test_oml = test_oml[feature_cols]

# Get predictions
print("Generating predictions...")
y_pred_proba_oml = xgb_model.predict_proba(X_test_oml)

# Convert to numpy
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

y_pred = (y_pred_proba >= 0.5).astype(int)
y_test_vals = y_test_pd.values

# Calculate metrics
accuracy = accuracy_score(y_test_vals, y_pred)
precision = precision_score(y_test_vals, y_pred, zero_division=0)
recall = recall_score(y_test_vals, y_pred, zero_division=0)
f1 = f1_score(y_test_vals, y_pred, zero_division=0)
auc = roc_auc_score(y_test_vals, y_pred_proba)

print("=" * 60)
print("Model Performance Metrics")
print("=" * 60)
print(f"AUC-ROC:     {auc:.4f} ({auc*100:.2f}%)")
print(f"Accuracy:    {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision:   {precision:.4f} ({precision*100:.2f}%)")
print(f"Recall:      {recall:.4f} ({recall*100:.2f}%)")
print(f"F1 Score:    {f1:.4f}")

# Confusion matrix
cm = confusion_matrix(y_test_vals, y_pred)
tn, fp, fn, tp = cm.ravel()
print("\nConfusion Matrix:")
print("                Predicted")
print("              Non-Churn  Churn")
print(f"Actual Non-Churn   {tn:5d}   {fp:5d}")
print(f"       Churn       {fn:5d}   {tp:5d}")
"""

# ============================================================================
# Cell 6: Save Model
# ============================================================================
"""
%python

# Save model to OML datastore
model_name = 'churn_xgboost_v1'
description = f'Churn prediction XGBoost model - AUC: {auc:.4f}'

try:
    oml.ds.save(
        {'model': xgb_model},
        model_name,
        description=description,
        overwrite=True
    )
    print(f"✓ Model saved to OML datastore: {model_name}")
except Exception as e:
    print(f"❌ ERROR: Failed to save model: {e}")
"""
