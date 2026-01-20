# How to Import Notebooks into OML Notebooks UI

## Overview

I've created two Jupyter notebook files (`.ipynb`) that you can **import directly** into OML Notebooks UI without copy-pasting:

1. **`oml-notebooks/train_churn_model.ipynb`** - Model training notebook
2. **`oml-notebooks/score_churn_model.ipynb`** - Model scoring notebook

## Step-by-Step Import Instructions

### Step 1: Access OML Notebooks

1. Log into **Oracle Cloud Console**
2. Navigate to your **Autonomous Database** instance
3. Click **"OML Notebooks"** (or "Machine Learning" → "Notebooks")

### Step 2: Import Training Notebook

1. In OML Notebooks, click **"Import"** or **"Upload"** button
2. Select **`oml-notebooks/train_churn_model.ipynb`**
3. Click **"Import"** or **"Upload"**
4. The notebook will appear in your notebook list
5. Open it and run cells sequentially

### Step 3: Import Scoring Notebook

1. Click **"Import"** or **"Upload"** again
2. Select **`oml-notebooks/score_churn_model.ipynb`**
3. Click **"Import"** or **"Upload"**
4. Open it after training is complete

## Notebook Contents

### Training Notebook (`train_churn_model.ipynb`)

**6 Cells:**
1. **Import and Setup** - Import libraries, check OML connection
2. **Load Training Data** - Load from `CHURN_TRAINING_DATA` view
3. **Split Data** - Train/test split (80/20)
4. **Train XGBoost Model** - Train model using OML4Py
5. **Evaluate Model** - Calculate metrics (AUC, accuracy, etc.)
6. **Save Model** - Save to OML Datastore

### Scoring Notebook (`score_churn_model.ipynb`)

**5 Cells:**
1. **Import and Setup** - Import libraries, check OML connection
2. **Load Model** - Load trained model from OML Datastore
3. **Load User Features** - Load from `CHURN_USER_FEATURES` view
4. **Score Users** - Generate predictions for all users
5. **Store Predictions** - Store in `CHURN_PREDICTIONS` table

## Important Notes

### For Scoring Notebook (Cell 5)

The scoring notebook's last cell requires database connection configuration. In OML Notebooks, you may need to:

1. **Use OML's built-in connection** (if available)
2. **Configure connection manually** using `oracledb`
3. **Use SQL cells** to insert predictions directly

**Option: Use SQL Cell Instead**

If database connection in Python is problematic, you can:
1. Generate predictions in Cell 4 (already done)
2. Create a new SQL cell to insert predictions:

```sql
-- SQL Cell: Insert Predictions
-- Note: You'll need to prepare the data first in Python

INSERT INTO OML.CHURN_PREDICTIONS (
    USER_ID,
    PREDICTED_CHURN_PROBABILITY,
    PREDICTED_CHURN_LABEL,
    RISK_SCORE,
    MODEL_VERSION,
    PREDICTION_DATE
) 
SELECT ... FROM ...
```

## Verification

After importing, verify:

1. **Training Notebook**:
   - All cells run without errors
   - Model saved to OML Datastore
   - AUC > 0.70 (good performance)

2. **Scoring Notebook**:
   - Model loads successfully
   - Predictions generated
   - Predictions stored in `CHURN_PREDICTIONS` table

## Troubleshooting

### Notebook Won't Import

- **Check file format**: Must be `.ipynb` (Jupyter notebook format)
- **Check file size**: Should be < 1MB
- **Try re-downloading**: File might be corrupted

### Cells Fail to Run

- **Check OML connection**: First cell should show "✓ OML connected"
- **Check views exist**: Run `SELECT * FROM OML.CHURN_TRAINING_DATA WHERE ROWNUM <= 1`
- **Check model exists**: For scoring, make sure training completed first

### Database Connection Issues (Scoring)

- **Option 1**: Use OML's built-in SQL cells to insert predictions
- **Option 2**: Export predictions to CSV, then import via SQL
- **Option 3**: Configure `oracledb` connection in the cell

## Alternative: Manual Copy-Paste

If import doesn't work, you can still:
1. Open the `.ipynb` files in a text editor
2. Copy Python code from each cell
3. Paste into OML Notebooks as new cells

## Files Created

- ✅ `oml-notebooks/train_churn_model.ipynb` - Training notebook
- ✅ `oml-notebooks/score_churn_model.ipynb` - Scoring notebook
- ✅ `scripts/verify_churn_predictions_table.py` - Table verification script

## Next Steps

1. **Import training notebook** → Run to train model
2. **Import scoring notebook** → Run to score users
3. **Verify predictions** → Query `CHURN_PREDICTIONS` table
4. **Build API** → Read from `CHURN_PREDICTIONS` for dashboard
