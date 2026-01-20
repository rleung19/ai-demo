# Fix: Model Only Using 1 Feature

## Problem

After applying hot fix, the model is only using 1 feature (MONTHS_SINCE_LAST_PURCHASE) with 100% importance, and AUC is still low (0.5074).

## Root Causes

1. **XGBoost is overfitting to one strong feature**
   - MONTHS_SINCE_LAST_PURCHASE is the strongest signal
   - Model finds it easier to use just this one feature
   - Other features have very low importance (near 0)

2. **Model parameters may be too restrictive**
   - Default XGBoost parameters might not encourage feature diversity
   - Need to adjust parameters to force model to use more features

3. **Feature scaling issues**
   - Some features might be on different scales
   - XGBoost might favor features with larger ranges

## Solutions

### Solution 1: Adjust XGBoost Parameters (Recommended)

Update Step 5 (Train XGBoost Model) to use parameters that encourage feature diversity:

```python
# Step 5: Train XGBoost Model - UPDATED
from oml import xgb

# Create XGBoost model with parameters that encourage feature diversity
xgb_model = xgb('classification',
                max_depth=4,              # Limit depth to prevent overfitting
                learning_rate=0.1,        # Slower learning
                n_estimators=100,          # More trees
                subsample=0.8,            # Use 80% of data per tree
                colsample_bytree=0.8,     # Use 80% of features per tree (FORCES diversity!)
                min_child_weight=3,        # Require more samples per leaf
                gamma=0.1,                # Minimum loss reduction
                reg_alpha=0.1,            # L1 regularization
                reg_lambda=1.0,           # L2 regularization
                scale_pos_weight=5.7)     # Handle class imbalance

# Rest of training code stays the same...
```

**Key Parameters**:
- `colsample_bytree=0.8`: Forces model to use different features in each tree
- `max_depth=4`: Prevents overfitting to one feature
- `reg_alpha` and `reg_lambda`: Regularization to prevent overfitting

### Solution 2: Feature Selection - Remove Low Variance Features

Add this before training to remove features with no variation:

```python
# Remove features with zero or very low variance
from sklearn.feature_selection import VarianceThreshold

# Calculate variance for each feature
feature_variances = X_train_pd.var()
print("Features with zero variance:", feature_variances[feature_variances == 0].index.tolist())
print("Features with very low variance (< 0.01):", feature_variances[feature_variances < 0.01].index.tolist())

# Remove low variance features
selector = VarianceThreshold(threshold=0.01)
X_train_selected = selector.fit_transform(X_train_pd)
selected_features = X_train_pd.columns[selector.get_support()].tolist()

print(f"Original features: {len(feature_cols)}")
print(f"Selected features: {len(selected_features)}")
print(f"Removed features: {set(feature_cols) - set(selected_features)}")

# Update feature_cols
feature_cols = selected_features
```

### Solution 3: Check for Constant Features

Some features might be constant (same value for all rows), which XGBoost ignores:

```python
# Check for constant features
constant_features = []
for col in feature_cols:
    if X_train_pd[col].nunique() <= 1:
        constant_features.append(col)
        print(f"Constant feature: {col} (value: {X_train_pd[col].iloc[0]})")

if constant_features:
    print(f"\nRemoving {len(constant_features)} constant features")
    feature_cols = [col for col in feature_cols if col not in constant_features]
```

### Solution 4: Feature Importance Threshold

After training, check if other features have non-zero importance but are just very small:

```python
# After extracting importance, check all features
importance_df_result = importance_df  # From Step 7

# Show ALL features, not just top 20
print("All features with importance > 0:")
non_zero = importance_df_result[importance_df_result['IMPORTANCE_SCORE'] > 0]
print(f"Total: {len(non_zero)} features")
print(non_zero.to_string(index=False))

# If only 1 feature, the model is truly only using one
if len(non_zero) == 1:
    print("\n⚠️  Model is only using 1 feature!")
    print("This suggests:")
    print("  1. Other features have no predictive power")
    print("  2. Model parameters need adjustment (use Solution 1)")
    print("  3. Features might be constant or highly correlated")
```

## Recommended Fix

**Apply Solution 1 first** - Update XGBoost parameters to force feature diversity:

1. Open Step 5 in your notebook
2. Replace the XGBoost model creation with the updated parameters above
3. Re-run training
4. Check Step 7 to see if more features are now used

## Expected Results After Fix

- **Features Used**: Should increase from 1 to 10-20 features
- **AUC**: Should improve from 0.5074 to 0.60-0.70
- **Feature Importance**: Should be more distributed (not 100% on one feature)

## Why This Happens

Even though the hot fix improved data patterns, XGBoost can still overfit to the strongest feature if:
- Parameters allow it (no regularization, no feature sampling)
- Other features are redundant or have very low signal
- Model depth is too high (can memorize patterns)

The `colsample_bytree` parameter is key - it forces the model to use different subsets of features in each tree, preventing over-reliance on one feature.
