# Random Forest Alternative - Why and How

## Problem with XGBoost

- **AUC: 0.4764** (worse than random chance!)
- **Only 1 feature used** (MONTHS_SINCE_LAST_PURCHASE)
- **OML XGBoost doesn't support parameters** to force feature diversity

## Solution: Random Forest

Random Forest naturally uses feature diversity because:
- Each tree uses a random subset of features
- Multiple trees vote on the final prediction
- Less prone to overfitting to one feature

## What Changed in Notebook

### Step 5: Now Uses Random Forest
```python
from oml import rf
xgb_model = rf('classification')  # Using RF for better feature diversity
```

**Note**: Variable is still named `xgb_model` for compatibility with rest of notebook.

## Expected Results

### With Random Forest:
- **Features Used**: Should increase to 10-20 features
- **AUC**: Should improve to 0.55-0.65 (better than current 0.4764)
- **Feature Importance**: Should be distributed across multiple features

## Alternative: Exclude Dominant Feature

If Random Forest still doesn't work well, you can temporarily exclude `MONTHS_SINCE_LAST_PURCHASE`:

1. In Step 4, after diagnostic, uncomment the exclusion code:
```python
if 'MONTHS_SINCE_LAST_PURCHASE' in feature_cols:
    print('\n⚠️  Excluding MONTHS_SINCE_LAST_PURCHASE to force feature diversity')
    feature_cols = [col for col in feature_cols if col != 'MONTHS_SINCE_LAST_PURCHASE']
    X_train_pd = X_train_pd[feature_cols]
    X_test_pd = X_test_pd[feature_cols]
```

This forces the model to learn from other features.

## Why AUC Got Worse

AUC 0.4764 is **below random chance** (0.5), which suggests:
1. Model is making predictions that are systematically wrong
2. The single feature (MONTHS_SINCE_LAST_PURCHASE) might have a weak or reversed relationship
3. Need multiple features to capture the true churn pattern

## Next Steps

1. **Re-run Step 5** with Random Forest
2. **Check Step 7** - should show 10-20 features with importance
3. **Check Step 6** - AUC should improve to 0.55-0.65
4. **If still poor**, try excluding MONTHS_SINCE_LAST_PURCHASE in Step 4

## Why Random Forest Should Help

- **Feature Diversity**: Each tree uses different features
- **Less Overfitting**: Multiple trees average out errors
- **Better for Tabular Data**: RF often works better than XGBoost for structured data
- **No Parameter Tuning Needed**: Works well with defaults
