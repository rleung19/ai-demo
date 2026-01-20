# Notebook Fixes Applied

## Issues Found

1. **Hot Fix Worked!** ✅
   - Churn patterns are now realistic:
     - Churners: 1.91 months, 3 logins, 0.21 email, 4.43 abandons
     - Non-churners: 0.25 months, 13.9 logins, 0.82 email, 0.35 abandons
   - This is MUCH better than before!

2. **Model Only Using 1 Feature** ❌
   - Only MONTHS_SINCE_LAST_PURCHASE (100% importance)
   - AUC still low: 0.5074

3. **Root Cause**: XGBoost overfitting to one strong feature

## Fixes Applied

### Fix 1: Updated XGBoost Parameters (Step 5)

**Changed from**:
```python
xgb_model = oml.xgb('classification')
```

**Changed to**:
```python
xgb_model = oml.xgb('classification',
                    max_depth=4,              # Limit depth to prevent overfitting
                    learning_rate=0.1,        # Slower learning
                    n_estimators=100,         # More trees
                    subsample=0.8,            # Use 80% of data per tree
                    colsample_bytree=0.8,     # Use 80% of features per tree (FORCES diversity!)
                    min_child_weight=3,        # Require more samples per leaf
                    gamma=0.1,                # Minimum loss reduction
                    reg_alpha=0.1,            # L1 regularization
                    reg_lambda=1.0,           # L2 regularization
                    scale_pos_weight=5.7)     # Handle class imbalance
```

**Key Parameter**: `colsample_bytree=0.8`
- Forces model to use different subsets of features in each tree
- Prevents over-reliance on one feature
- Should increase features used from 1 to 10-20

### Fix 2: Added Feature Diagnostics (Step 4)

Added diagnostic code to check for:
- **Constant features**: Features with only one value (removed automatically)
- **Low variance features**: Features with variance < 0.01 (warns but keeps)

This helps identify if some features are being ignored because they have no variation.

## Expected Results After Re-running

### Before Fixes
- Features Used: 1 (MONTHS_SINCE_LAST_PURCHASE only)
- AUC: 0.5074 (50.74%)
- Feature Importance: 100% on one feature

### After Fixes
- Features Used: 10-20 features (distributed importance)
- AUC: 0.60-0.70 (60-70%)
- Feature Importance: Distributed across multiple features

## Next Steps

1. **Re-run the notebook from Step 4** (or Step 5 if Step 4 already ran)
2. **Check Step 4 output** - Look for:
   - Constant features removed
   - Low variance warnings
   - Final feature count
3. **Check Step 5 output** - Training should complete
4. **Check Step 7 output** - Should show 10-20 features with importance > 0
5. **Check Step 13 output** - AUC should improve to 0.60-0.70

## Why This Will Work

1. **`colsample_bytree=0.8`**: Each tree uses only 80% of features, forcing diversity
2. **Regularization (`reg_alpha`, `reg_lambda`)**: Prevents overfitting to one feature
3. **`max_depth=4`**: Limits tree depth, prevents memorization
4. **More trees (`n_estimators=100`)**: Allows model to explore different feature combinations

## If Still Only 1 Feature

If after these fixes you still see only 1 feature:

1. **Check Step 4 diagnostics** - Are other features constant?
2. **Check feature importance in Step 7** - Are other features truly 0 or just very small?
3. **Try even more aggressive parameters**:
   ```python
   colsample_bytree=0.5,  # Use only 50% of features per tree
   max_depth=3,           # Even shallower trees
   ```

## Summary

✅ Hot fix applied - data patterns are realistic
✅ XGBoost parameters updated - forces feature diversity
✅ Feature diagnostics added - identifies problematic features

**Re-run the notebook and check Step 7 for feature importance distribution!**
