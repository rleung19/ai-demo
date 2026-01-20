# Feature Exclusion Strategy

## Current Results Analysis

### Progress Made
- ✅ **Before**: Model used only 1 feature (MONTHS_SINCE_LAST_PURCHASE)
- ✅ **After exclusion**: Model now uses 3 features
- ⚠️ **Still dominated**: EMAIL_OPEN_RATE_30D is 98.8% of importance

### Current Performance
- **AUC**: 0.5238 (barely better than random)
- **Features Used**: 3 (but one dominates)
- **Scoring Issue**: 0 at-risk customers at 0.1 threshold (probabilities too low)

## Problem: Sequential Dominance

When we exclude one dominant feature, XGBoost immediately latches onto the next strongest feature. This suggests:

1. **Feature correlation**: These features may be highly correlated with the target
2. **Weak other features**: Other features may not have strong predictive power
3. **Model simplicity**: XGBoost defaults may be too simple

## Solution: Exclude Multiple Dominant Features

### Strategy
Exclude both `MONTHS_SINCE_LAST_PURCHASE` and `EMAIL_OPEN_RATE_30D` to force the model to:
- Use a **diverse set of features** (5-10 features)
- Learn **interactions** between features
- Avoid **overfitting** to a single strong signal

### Updated Step 4
Now excludes both features:
```python
dominant_features_to_exclude = ['MONTHS_SINCE_LAST_PURCHASE', 'EMAIL_OPEN_RATE_30D']
excluded_features = [f for f in dominant_features_to_exclude if f in feature_cols]
if excluded_features:
    print('\n⚠️  Excluding dominant features to force feature diversity:')
    for feat in excluded_features:
        print(f'  - {feat}')
    feature_cols = [col for col in feature_cols if col not in excluded_features]
    X_train_pd = X_train_pd[feature_cols]
    X_test_pd = X_test_pd[feature_cols]
    print(f'Remaining features after exclusion: {len(feature_cols)}')
```

## Expected Results

### After Excluding Both Features:
- **Features Used**: 5-10 (instead of 3)
- **Feature Distribution**: More balanced importance across features
- **AUC**: Should improve to 0.55-0.60 (better than current 0.5238)
- **Scoring**: Should identify at-risk customers properly

## Why This Should Work

1. **Forces Diversity**: Model must learn from multiple signals
2. **Reduces Overfitting**: Less reliance on single strong features
3. **Better Generalization**: Multiple features capture different aspects of churn
4. **More Robust**: Model won't break if one feature is missing

## Alternative Approaches (If Still Poor)

If excluding both features still doesn't work well:

### Option 1: Exclude Top 3 Features
```python
dominant_features_to_exclude = [
    'MONTHS_SINCE_LAST_PURCHASE',
    'EMAIL_OPEN_RATE_30D',
    'LOGIN_COUNT_30D'  # Next most important
]
```

### Option 2: Feature Engineering
Create interaction features from the excluded ones:
- `MONTHS_X_EMAIL_RATE`
- `LOGIN_X_EMAIL_RATE`
- `PURCHASE_X_EMAIL_RATE`

### Option 3: Use Different Algorithm
Try other OML algorithms if available:
- Decision Tree
- Naive Bayes
- GLM (Generalized Linear Model)

## Next Steps

1. **Re-run Step 4** - Should exclude both features
2. **Re-run Step 5** - Train with remaining features
3. **Check Step 7** - Should show 5-10 features with balanced importance
4. **Check Step 6** - AUC should improve, scoring should work

## Monitoring

Watch for:
- ✅ **More features used** (5-10 instead of 1-3)
- ✅ **Balanced importance** (no single feature > 50%)
- ✅ **Better AUC** (0.55+ instead of 0.52)
- ✅ **Proper scoring** (at-risk customers identified)
