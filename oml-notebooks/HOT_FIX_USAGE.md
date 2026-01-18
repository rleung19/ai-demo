# Using Hot-Fixed Data in Your Notebook

## Quick Start

### Step 1: Run the SQL Hot Fix Script

Add this as a new SQL cell in your notebook (before Step 2):

```sql
-- Run the hot fix script to create fixed views
-- Copy and paste the contents of HOT_FIX_DATA.sql here
-- Or execute it directly from the file
```

### Step 2: Update Your Notebook to Use Fixed Views

Replace these lines in your notebook:

#### In Step 3 (Explore Data):
```python
# OLD:
features = oml.sync(view='CHURN_FEATURES')

# NEW:
features = oml.sync(view='CHURN_FEATURES_CORRELATED')
```

#### In Step 4 (Prepare Features):
```python
# OLD:
training_data = oml.sync(view='CHURN_TRAINING_DATA')

# NEW:
training_data = oml.sync(view='CHURN_TRAINING_DATA_FINAL')
```

### Step 3: Verify the Fix Worked

Add this verification cell after running the hot fix:

```python
# Verify patterns are fixed
import pandas as pd

# Check churn patterns
training_fixed = oml.sync(view='CHURN_TRAINING_DATA_FINAL')
training_fixed_pd = training_fixed.pull()

print("=" * 60)
print("CHURN PATTERNS AFTER FIX")
print("=" * 60)
churn_summary = training_fixed_pd.groupby('CHURNED_60_90D').agg({
    'MONTHS_SINCE_LAST_PURCHASE': 'mean',
    'LOGIN_COUNT_30D': 'mean',
    'EMAIL_OPEN_RATE_30D': 'mean',
    'CART_ABANDONMENTS_30D': 'mean'
}).round(2)
print(churn_summary)

# Check correlations
features_fixed = oml.sync(view='CHURN_FEATURES_CORRELATED')
features_fixed_pd = features_fixed.pull()

print("\n" + "=" * 60)
print("CORRELATIONS AFTER FIX")
print("=" * 60)
correlations = features_fixed_pd[[
    'TOTAL_SPENT_24M', 'LOGIN_COUNT_30D', 'EMAIL_OPEN_RATE_30D',
    'ORDER_COUNT_24M', 'TOTAL_RETURNS_COUNT', 'AVG_REVIEW_RATING',
    'CART_ABANDONMENTS_30D'
]].corr()

print("Spend-Login:", correlations.loc['TOTAL_SPENT_24M', 'LOGIN_COUNT_30D'])
print("Spend-Email:", correlations.loc['TOTAL_SPENT_24M', 'EMAIL_OPEN_RATE_30D'])
print("Returns-Rating:", correlations.loc['TOTAL_RETURNS_COUNT', 'AVG_REVIEW_RATING'])
print("Abandon-Email:", correlations.loc['CART_ABANDONMENTS_30D', 'EMAIL_OPEN_RATE_30D'])
```

## Expected Results After Fix

### Churn Patterns (Target)
```
CHURNED_60_90D  AVG_MONTHS  AVG_LOGINS  AVG_EMAIL  AVG_ABANDONS
--------------  ----------  ----------  ----------  ------------
             0        0.25       15.0       0.72          1.2
             1        2.10        3.5       0.32          5.5
```

### Correlations (Target)
- Spend-Login: 0.45-0.60 (currently 0.159)
- Spend-Email: 0.45-0.60 (currently 0.256)
- Returns-Rating: -0.50 to -0.70 (currently NULL)
- Abandon-Email: -0.30 to -0.50 (currently 0.125 - wrong direction!)

## What the Hot Fix Does

1. **Fixes Churn Patterns**:
   - Increases months since purchase for churners (1.0 → 2.0-3.0)
   - Decreases logins for churners (8.94 → 2-5)
   - Decreases email engagement for churners (0.994 → 0.2-0.4)
   - Increases cart abandons for churners (0.89 → 3-8)

2. **Strengthens Correlations**:
   - High spenders get more logins and better email engagement
   - More returns correlate with lower ratings
   - More abandons correlate with lower email engagement (fixes direction!)

3. **Preserves Original Data**:
   - Uses views (doesn't modify original tables)
   - Can easily revert by using original views
   - Safe to experiment with

## Troubleshooting

### If patterns still look wrong:
1. Check that you're using the `_FINAL` and `_CORRELATED` views
2. Verify the views were created successfully
3. Re-run the verification queries

### If correlations are still weak:
- The hot fix applies multipliers, but if original data has no variation, correlations will still be weak
- Consider regenerating data for better results

### If you want to revert:
- Simply use original views: `CHURN_FEATURES` and `CHURN_TRAINING_DATA`

## Next Steps

After applying the hot fix:
1. ✅ Verify patterns are fixed (run verification queries)
2. ✅ Re-train your model using fixed views
3. ✅ Check if AUC improves (should go from 0.50 to 0.65-0.75)
4. ✅ If still low, consider regenerating data with better patterns
