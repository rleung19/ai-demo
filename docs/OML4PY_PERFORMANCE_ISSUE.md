# OML4Py Performance Issue Investigation

## Problem

**Task 2.8 Validation**: AUC = 0.9190 (RandomForest locally) ✅  
**OML4Py XGBoost**: AUC = 0.5040 (essentially random) ❌

This is a **huge discrepancy** that suggests either:
1. OML4Py XGBoost has issues with default parameters
2. Data is being corrupted when pushed to OML
3. OML4Py XGBoost needs explicit hyperparameters
4. There's a bug or limitation in OML4Py

## Key Differences

### Task 2.8 (AUC 0.9190)
- Used **RandomForest** locally (not OML4Py)
- Used `pd.to_numeric(X[col], errors='coerce').fillna(0)` for robust type conversion
- Trained on pandas DataFrame directly
- No data push to OML

### Current Notebook (AUC 0.5040)
- Uses **OML4Py XGBoost** (in-database)
- Pushes data to OML with `oml.push()`
- Trains in database
- Uses default OML4Py XGBoost parameters

## Possible Causes

### 1. OML4Py XGBoost Default Parameters

OML4Py XGBoost might have very restrictive default parameters that prevent learning. The notebook now includes hyperparameters to:
- Force feature diversity (`colsample_bytree=0.8`)
- Prevent overfitting (`max_depth=6`, regularization)
- Handle class imbalance (`scale_pos_weight`)

### 2. Data Type Issues

When data is pushed to OML, data types might change or get corrupted. The diagnostic cell (4.5) checks for this.

### 3. OML4Py Version/Limitations

Some OML4Py versions might have bugs or limitations. Check Oracle documentation for known issues.

## Fixes Applied

### 1. Improved Data Cleaning
- Now uses `pd.to_numeric(..., errors='coerce')` like validation script
- More robust type conversion

### 2. Added Hyperparameters
- `colsample_bytree=0.8` - Forces feature diversity
- `max_depth=6` - Prevents overfitting
- Regularization parameters
- Class imbalance handling

### 3. Diagnostic Cell
- Cell 4.5 compares data before/after OML push
- Checks for data corruption

## Next Steps

1. **Re-run training** with updated hyperparameters
2. **Run diagnostic cell** (4.5) to check data integrity
3. **Compare results** - if still poor, try:
   - Using OML4Py RandomForest instead of XGBoost
   - Training locally and deploying model
   - Checking OML4Py version and known issues

## Alternative: Use RandomForest in OML

If XGBoost continues to fail, try RandomForest (which worked in validation):

```python
# Instead of XGBoost
rf_model = oml.rf('classification', n_estimators=100, max_depth=10)
rf_model = rf_model.fit(X_train_oml, y_train_oml)
```

## References

- Task 2.8 achieved AUC 0.9190 with RandomForest
- Previous fixes suggest `colsample_bytree` is critical for feature diversity
- OML4Py documentation may have version-specific notes
