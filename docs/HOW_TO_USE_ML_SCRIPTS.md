# How to Use the ML Training Scripts

## Quick Answer

**You need to run these scripts in OML Notebooks UI** (web interface), not on your local machine. The model training happens remotely in your ADB.

## Step-by-Step Guide

### Step 1: Access OML Notebooks

1. Log into Oracle Cloud Console
2. Navigate to your ADB instance
3. Click on **"OML Notebooks"** (or "Machine Learning" → "Notebooks")
4. This opens a web-based Jupyter-like interface

### Step 2: Create New Notebook

1. Click "New Notebook" or "Create"
2. Name it: `churn_model_training`
3. This creates a new notebook in the web interface

### Step 3: Run Training Pipeline

**Option A: Use Notebook Cells (Recommended)**

1. Open `oml-notebooks/train_churn_model_notebook.py`
2. Copy each cell (marked with `%python`)
3. Paste into OML Notebooks as separate cells
4. Run cells sequentially

**Option B: Execute Script**

1. Upload `scripts/train_churn_model.py` to OML Notebooks
2. In a notebook cell, run:
   ```python
   %python
   exec(open('scripts/train_churn_model.py').read())
   ```

### Step 4: Run Scoring Pipeline

1. Upload `scripts/score_churn_model.py` to OML Notebooks
2. In a notebook cell, run:
   ```python
   %python
   exec(open('scripts/score_churn_model.py').read())
   ```
3. This populates `CHURN_PREDICTIONS` table

### Step 5: Verify Predictions

In OML Notebooks, run SQL:
```sql
%script
SELECT 
    COUNT(*) AS TOTAL,
    SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS AT_RISK,
    AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS AVG_RISK
FROM OML.CHURN_PREDICTIONS;
```

## What Happens When You Run in OML Notebooks

### Training Script Execution:

```
Your Action (in OML Notebooks UI):
  ↓ Run Python cell
  ↓
OML4Py (in OML Notebooks server):
  ↓ Sends command to ADB
  ↓
Oracle ADB (Remote):
  ↓ Executes XGBoost training
  ↓ Stores model in OML Datastore
  ↓
Result returned to OML Notebooks:
  ↓ Displays in notebook cell
```

### Key Points:

1. **You run** the script in OML Notebooks UI (web browser)
2. **OML Notebooks server** (Oracle's infrastructure) executes it
3. **ADB** (your database) does the actual training
4. **Model** is stored in ADB's OML Datastore
5. **You see** results in the notebook interface

## Why Not Run Locally?

### OML4Py Availability:

- ✅ **Available in**: OML Notebooks UI (Oracle's servers)
- ❌ **Not available in**: Standard Python environments
- ❌ **Not installable via**: `pip install oml`

### What You CAN Do Locally:

- ✅ Use `oracledb` to query data
- ✅ Use `sklearn/xgboost` to train models locally
- ✅ Read predictions from `CHURN_PREDICTIONS` table
- ❌ Use OML4Py (requires OML Notebooks)

## Alternative: Local Training (If Needed)

If you want to train locally (without OML Notebooks):

```python
# Use oracledb to get data
import oracledb
import pandas as pd
from xgboost import XGBClassifier

# Connect and query
connection = oracledb.connect(...)
df = pd.read_sql("SELECT * FROM OML.CHURN_TRAINING_DATA", connection)

# Train locally
X = df[feature_cols]
y = df['CHURNED']
model = XGBClassifier()
model.fit(X, y)

# Save locally (not in OML Datastore)
import pickle
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
```

**Trade-offs**:
- ✅ Works without OML Notebooks
- ❌ Model not in OML Datastore
- ❌ Can't use OML4Py features
- ❌ Data must be pulled to local machine

## Recommended Approach

### For This Project:

1. **Model Training**: Use OML Notebooks UI
   - Run `train_churn_model_notebook.py` cells
   - Model saved to OML Datastore

2. **Model Scoring**: Use OML Notebooks UI
   - Run `score_churn_model.py`
   - Predictions in `CHURN_PREDICTIONS` table

3. **API Server**: Use `oracledb` (local or server)
   - Read from `CHURN_PREDICTIONS` table
   - No OML4Py needed
   - No model training needed

## Summary

| Task | Where to Run | Tool Used |
|------|--------------|-----------|
| **Train Model** | OML Notebooks UI | OML4Py |
| **Score Users** | OML Notebooks UI | OML4Py |
| **API Server** | Your server/local | oracledb |
| **Read Predictions** | Your server/local | oracledb |

**The scripts are ready to use - just run them in OML Notebooks UI!**
