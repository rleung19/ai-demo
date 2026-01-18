# OML4Py Quick Start Guide

## TL;DR: Train Your Model in 5 Steps

1. **Open OML Notebooks** (Oracle Cloud Console → ADB → OML Notebooks)
2. **Create new notebook** (Python)
3. **Copy cells** from `oml-notebooks/train_churn_model_notebook.py`
4. **Run cells** sequentially
5. **Model trained and saved** in ADB!

## Complete Example (Copy-Paste Ready)

### Cell 1: Setup

```python
%python
import oml
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from datetime import datetime

print("=" * 60)
print("Churn Model Training")
print("=" * 60)
```

### Cell 2: Load Data

```python
%python
# Load from view
train_data_oml = oml.sync(view='CHURN_TRAINING_DATA')
train_data_pd = train_data_oml.pull()

# Get features
exclude_cols = ['USER_ID', 'CHURNED']
feature_cols = [col for col in train_data_pd.columns if col not in exclude_cols]

X_pd = train_data_pd[feature_cols].copy()
y_pd = train_data_pd['CHURNED'].copy()

# Clean
for col in feature_cols:
    if pd.api.types.is_numeric_dtype(X_pd[col]):
        X_pd[col] = X_pd[col].replace([np.inf, -np.inf], np.nan).fillna(0)

print(f"✓ Loaded {len(X_pd):,} rows, {len(feature_cols)} features")
```

### Cell 3: Split

```python
%python
X_train_pd, X_test_pd, y_train_pd, y_test_pd = train_test_split(
    X_pd, y_pd, test_size=0.2, random_state=42, stratify=y_pd
)
print(f"Train: {len(X_train_pd):,}, Test: {len(X_test_pd):,}")
```

### Cell 4: Train

```python
%python
# Push to database
train_combined_pd = X_train_pd.copy()
train_combined_pd['CHURNED'] = y_train_pd.values
train_oml = oml.push(train_combined_pd)

# Create and train model
xgb_model = oml.xgb('classification')
X_train_oml = train_oml[feature_cols]
y_train_oml = train_oml['CHURNED']

print("Training...")
xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
print("✓ Training complete!")
```

### Cell 5: Evaluate

```python
%python
# Test
test_combined_pd = X_test_pd.copy()
test_combined_pd['CHURNED'] = y_test_pd.values
test_oml = oml.push(test_combined_pd)
X_test_oml = test_oml[feature_cols]

# Predict
y_pred_proba_oml = xgb_model.predict_proba(X_test_oml)
y_pred_proba = y_pred_proba_oml.pull()

# Get probabilities (handle different formats)
if isinstance(y_pred_proba, pd.DataFrame):
    if 1 in y_pred_proba.columns:
        y_pred_proba = y_pred_proba[1].values
    else:
        y_pred_proba = y_pred_proba.iloc[:, 1].values
else:
    y_pred_proba = np.array(y_pred_proba).flatten()

y_pred = (y_pred_proba >= 0.5).astype(int)
y_test_vals = y_test_pd.values

# Metrics
auc = roc_auc_score(y_test_vals, y_pred_proba)
accuracy = accuracy_score(y_test_vals, y_pred)
precision = precision_score(y_test_vals, y_pred, zero_division=0)
recall = recall_score(y_test_vals, y_pred, zero_division=0)
f1 = f1_score(y_test_vals, y_pred, zero_division=0)

print(f"AUC: {auc:.4f}")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1: {f1:.4f}")
```

### Cell 6: Save

```python
%python
model_name = 'churn_xgboost_v1'
oml.ds.save(
    {'model': xgb_model},
    model_name,
    description=f'Churn model - AUC: {auc:.4f}',
    overwrite=True
)
print(f"✓ Model saved: {model_name}")
```

## That's It! 🎉

Your model is now:
- ✅ Trained in your ADB
- ✅ Saved in OML Datastore
- ✅ Ready for scoring

## Next: Score Users

See `scripts/score_churn_model.py` for scoring all users.

## Full Documentation

- **`docs/HOW_TO_USE_OML4PY.md`**: Complete guide with explanations
- **`oml-notebooks/train_churn_model_notebook.py`**: Full notebook cells
