# How to Use OML4Py for Model Training

## Overview

This guide shows you how to use **OML4Py** (Oracle Machine Learning for Python) to train your churn prediction model **in your Oracle ADB database**. OML4Py is the recommended approach as it:
- Trains models **inside the database** (faster, more efficient)
- Stores models in **OML Datastore** (integrated with database)
- Keeps data **in the database** (no data movement)
- Uses **in-database XGBoost** (optimized for Oracle)

## Prerequisites

1. **Access to OML Notebooks**
   - Log into Oracle Cloud Console
   - Navigate to your ADB instance
   - Open "OML Notebooks" (or "Machine Learning" → "Notebooks")

2. **Database Setup Complete**
   - Tables created: `OML.CHURN_DATASET_TRAINING`, `OML.USER_PROFILES`, `OML.CHURN_PREDICTIONS`
   - Views created: `OML.CHURN_TRAINING_DATA`, `OML.CHURN_USER_FEATURES`
   - Data loaded into training table

## Step-by-Step Guide

### Step 1: Open OML Notebooks

1. Log into **Oracle Cloud Console**
2. Navigate to your **Autonomous Database** instance
3. Click **"OML Notebooks"** (or "Machine Learning" → "Notebooks")
4. This opens a web-based Jupyter-like interface

### Step 2: Create New Notebook

1. Click **"New Notebook"** or **"Create"**
2. Name it: `churn_model_training`
3. Select **Python** as the language
4. Click **"Create"**

### Step 3: Copy and Run Training Cells

I've created a notebook-ready version for you. Open `oml-notebooks/train_churn_model_notebook.py` and copy each cell into your OML Notebook.

#### Cell 1: Import and Setup

```python
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
```

**What this does**: Imports OML4Py and checks connection to ADB.

#### Cell 2: Load Training Data

```python
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
```

**What this does**: 
- Loads data from `OML.CHURN_TRAINING_DATA` view using `oml.sync()`
- Identifies feature columns (excludes USER_ID and CHURNED)
- Cleans data (handles infinity and NaN values)

**Key OML4Py function**: `oml.sync(view='...')` - Syncs a database view/table to OML

#### Cell 3: Split Data

```python
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
```

**What this does**: Splits data into training (80%) and testing (20%) sets.

#### Cell 4: Train XGBoost Model

```python
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
```

**What this does**:
- **`oml.push(dataframe)`**: Pushes pandas DataFrame to database (creates temporary table)
- **`oml.xgb('classification')`**: Creates XGBoost classifier for in-database training
- **`xgb_model.fit(X, y)`**: Trains model **inside ADB** (not on your machine!)

**Key OML4Py functions**:
- `oml.push()` - Push data to database
- `oml.xgb()` - Create XGBoost model
- `.fit()` - Train model in database

#### Cell 5: Evaluate Model

```python
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
```

**What this does**:
- Pushes test data to database
- Generates predictions using the trained model
- Calculates performance metrics (AUC, accuracy, precision, recall, F1)
- Displays confusion matrix

**Key OML4Py functions**:
- `.predict_proba()` - Get prediction probabilities (executes in database)
- `.pull()` - Pull results back to pandas DataFrame

#### Cell 6: Save Model

```python
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
```

**What this does**: Saves the trained model to OML Datastore in your database.

**Key OML4Py function**: `oml.ds.save()` - Save model to OML Datastore

## Complete Notebook File

For convenience, all cells are in: **`oml-notebooks/train_churn_model_notebook.py`**

You can:
1. Open that file
2. Copy each cell (marked with `%python`)
3. Paste into OML Notebooks
4. Run sequentially

## Understanding OML4Py Functions

### Data Operations

| Function | Purpose | Example |
|----------|---------|---------|
| `oml.sync()` | Sync database view/table to OML | `oml.sync(view='CHURN_TRAINING_DATA')` |
| `oml.push()` | Push pandas DataFrame to database | `oml.push(df)` |
| `.pull()` | Pull OML data to pandas DataFrame | `data_oml.pull()` |

### Model Operations

| Function | Purpose | Example |
|----------|---------|---------|
| `oml.xgb()` | Create XGBoost model | `oml.xgb('classification')` |
| `.fit()` | Train model (in database) | `model.fit(X, y)` |
| `.predict()` | Generate predictions | `model.predict(X)` |
| `.predict_proba()` | Get probabilities | `model.predict_proba(X)` |

### Model Storage

| Function | Purpose | Example |
|----------|---------|---------|
| `oml.ds.save()` | Save model to datastore | `oml.ds.save({'model': m}, 'name')` |
| `oml.ds.load()` | Load model from datastore | `oml.ds.load('name')` |

## Key Concepts

### 1. In-Database Training

When you call `xgb_model.fit(X_oml, y_oml)`:
- **Training happens in ADB**, not on your machine
- Data stays in the database
- Model is stored in OML Datastore
- Much faster for large datasets

### 2. OML Data Types

- **`oml.DataFrame`**: OML's data structure (like pandas DataFrame, but in database)
- **`.pull()`**: Convert OML DataFrame to pandas DataFrame
- **`oml.push()`**: Convert pandas DataFrame to OML DataFrame

### 3. Model Persistence

Models saved with `oml.ds.save()` are:
- Stored in **OML Datastore** (in your database)
- Accessible from any OML Notebook
- Can be loaded with `oml.ds.load()`
- Versioned by name

## Next Steps: Scoring Users

After training, you'll want to score all users. See:
- **`scripts/score_churn_model.py`**: Scoring script (for OML Notebooks)
- **`docs/TASK_3.8_GUIDE.md`**: Scoring documentation

## Troubleshooting

### OML Not Connected

**Error**: `oml.isconnected()` returns `False`

**Solution**: 
- OML connection is automatic in OML Notebooks
- If not connected, check you're in OML Notebooks environment
- Connection happens automatically when you use OML functions

### View Not Found

**Error**: `ORA-00942: table or view does not exist`

**Solution**:
- Verify view exists: `SELECT * FROM OML.CHURN_TRAINING_DATA WHERE ROWNUM <= 1`
- Check you're using correct schema (OML)
- Run `scripts/create_feature_views.py` if views don't exist

### Model Training Fails

**Error**: Training takes too long or fails

**Solution**:
- Check data size (too large?)
- Verify data quality (no nulls, correct types)
- Try smaller sample first
- Check ADB resources

## Summary

**OML4Py Workflow**:
1. **Load data**: `oml.sync(view='...')` or `oml.push(df)`
2. **Create model**: `oml.xgb('classification')`
3. **Train**: `model.fit(X, y)` ← **Happens in ADB**
4. **Evaluate**: `model.predict_proba(X)`
5. **Save**: `oml.ds.save({'model': model}, 'name')`

**Key Advantage**: Everything happens **in your database**, making it fast, secure, and integrated.
