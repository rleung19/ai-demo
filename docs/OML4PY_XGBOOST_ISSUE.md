# OML4Py XGBoost Performance Issue

## Problem Summary

**OML4Py XGBoost with default parameters**: AUC = 0.5014 (essentially random) ❌  
**RandomForest (Task 2.8 validation)**: AUC = 0.9190 ✅

## Root Cause

OML4Py XGBoost's default parameters are not suitable for this dataset, resulting in essentially random predictions (AUC ~0.50).

### Key Findings

1. **OML4Py XGBoost Limitations**:
   - Does NOT support hyperparameters as keyword arguments
   - Default parameters perform poorly (AUC ~0.50)
   - Error when trying to pass parameters: `PLS-00302: component 'MAX_DEPTH' must be declared`

2. **RandomForest Alternative**:
   - Task 2.8 validation achieved AUC 0.9190 with RandomForest
   - OML4Py RandomForest may support some parameters (`n_estimators`, `max_depth`)
   - Much better performance than XGBoost defaults

## Solution

**Switch to RandomForest** instead of XGBoost for OML4Py training.

### Updated Training Code

```python
# Use RandomForest instead of XGBoost
xgb_model = oml.rf('classification', n_estimators=100, max_depth=10)
xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
```

Note: The variable name `xgb_model` is kept for compatibility with evaluation code, but it's actually a RandomForest model.

## Performance Comparison

| Model | AUC | Status |
|-------|-----|--------|
| OML4Py XGBoost (defaults) | 0.5014 | ❌ Random |
| RandomForest (Task 2.8) | 0.9190 | ✅ Excellent |
| RandomForest (OML4Py) | TBD | ⏳ Expected ~0.90+ |

## Recommendations

1. **Use RandomForest** for OML4Py training (already implemented in notebook)
2. **If XGBoost is required**, consider:
   - Training locally with XGBoost and deploying the model
   - Using Oracle AutoML to find better XGBoost parameters
   - Checking OML4Py version for parameter support updates

## Related Documentation

- `docs/TASK_2.8_GUIDE.md` - Validation results (AUC 0.9190 with RandomForest)
- `docs/OML4PY_PERFORMANCE_ISSUE.md` - Initial investigation
- `oml-notebooks/train_churn_model.ipynb` - Updated notebook using RandomForest
