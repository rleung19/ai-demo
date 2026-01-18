# Troubleshooting Poor Model Performance

## Issue: Model AUC < 0.55 (Poor Performance)

If your model shows AUC < 0.55 (essentially random or worse), this indicates the model is not learning from the data.

## Quick Diagnostics

### 1. Run the Diagnostic Cell

The updated training notebook includes a **Cell 2.5: Data Quality Diagnostics**. Run this cell to check:
- Feature distributions
- Feature-target correlations
- Data quality issues

### 2. Check Data Quality

Run these checks in a new cell:

```python
%python

# Check churn distribution
print(f"Churn rate: {train_data_pd['CHURNED'].mean()*100:.2f}%")
print(f"Churned: {train_data_pd['CHURNED'].sum():,}")
print(f"Retained: {(train_data_pd['CHURNED'] == 0).sum():,}")

# Check for class imbalance
if train_data_pd['CHURNED'].mean() < 0.05 or train_data_pd['CHURNED'].mean() > 0.95:
    print("⚠️  WARNING: Severe class imbalance!")
```

### 3. Check Feature Quality

```python
%python

# Check feature correlations with target
correlations = []
for col in feature_cols:
    if pd.api.types.is_numeric_dtype(X_pd[col]):
        corr = abs(X_pd[col].corr(y_pd))
        if not np.isnan(corr):
            correlations.append((col, corr))

correlations.sort(key=lambda x: x[1], reverse=True)
print("Top 10 features by correlation with churn:")
for col, corr in correlations[:10]:
    print(f"  {col:30} {corr:.4f}")

# If all correlations < 0.1, features may not be predictive
if correlations and max([c[1] for c in correlations]) < 0.1:
    print("\n⚠️  WARNING: Very low feature-target correlations!")
```

## Common Causes and Solutions

### Cause 1: Features Not Informative

**Symptoms:**
- All feature-target correlations < 0.1
- Model predictions have very low variance

**Solutions:**
1. **Check feature engineering views**: Verify `CHURN_TRAINING_DATA` view has meaningful features
2. **Review data mapping**: Ensure features are correctly mapped from source data
3. **Feature selection**: Remove non-informative features
4. **Create new features**: Consider feature engineering (e.g., ratios, interactions)

### Cause 2: Data Quality Issues

**Symptoms:**
- Many missing values
- Constant columns (no variance)
- Extreme outliers

**Solutions:**
1. **Check for constant columns**: The notebook now removes these automatically
2. **Handle missing values**: Ensure proper imputation
3. **Check data types**: Ensure numeric features are actually numeric
4. **Verify data source**: Check if training data is correct

### Cause 3: Class Imbalance

**Symptoms:**
- Churn rate < 5% or > 95%
- Model predicts majority class only

**Solutions:**
1. **Use stratified sampling**: Already implemented in notebook
2. **Adjust class weights**: Modify XGBoost parameters
3. **Use different metrics**: Focus on precision/recall instead of accuracy

### Cause 4: Model Configuration

**Symptoms:**
- Model trains but doesn't improve
- Predictions are all similar

**Solutions:**
1. **Try different hyperparameters**: 
   ```python
   xgb_model = oml.xgb('classification', 
                       max_depth=6,
                       learning_rate=0.1,
                       n_estimators=100)
   ```
2. **Increase training time**: More iterations
3. **Feature scaling**: Normalize features if needed

## Step-by-Step Fix Process

### Step 1: Verify Data Source

```sql
-- Run in SQL cell
SELECT 
    COUNT(*) AS TOTAL,
    SUM(CHURNED) AS CHURNED_COUNT,
    AVG(CHURNED) * 100 AS CHURN_RATE
FROM OML.CHURN_TRAINING_DATA;
```

### Step 2: Check Feature Views

```sql
-- Verify view has data
SELECT COUNT(*) FROM OML.CHURN_TRAINING_DATA;

-- Check a few sample rows
SELECT * FROM OML.CHURN_TRAINING_DATA WHERE ROWNUM <= 5;
```

### Step 3: Run Diagnostics

Run **Cell 2.5** in the training notebook to see:
- Feature statistics
- Feature-target correlations
- Data quality issues

### Step 4: Check Feature Engineering

Verify your feature engineering views (`CHURN_TRAINING_DATA`) are creating meaningful features:

```sql
-- Check feature distributions
SELECT 
    AVG(DAYS_SINCE_LAST_PURCHASE) AS AVG_DAYS,
    AVG(TOTAL_PURCHASES) AS AVG_PURCHASES,
    AVG(LIFETIME_VALUE) AS AVG_LTV
FROM OML.CHURN_TRAINING_DATA;
```

### Step 5: Try Feature Selection

If you have many features, try selecting only the most correlated ones:

```python
%python

# Select top correlated features
top_features = [col for col, corr in correlations[:20] if corr > 0.05]
print(f"Using {len(top_features)} top features")
feature_cols = top_features
```

## Expected Results

### Good Performance
- **AUC >= 0.70**: Model is learning effectively
- **Feature correlations > 0.1**: Features are informative
- **Prediction variance > 0.01**: Model is making diverse predictions

### Poor Performance Indicators
- **AUC < 0.55**: Model is not learning (essentially random)
- **All correlations < 0.1**: Features not predictive
- **Prediction variance < 0.01**: Model predictions are constant

## Next Steps

1. **Run diagnostic cell** (Cell 2.5) to identify issues
2. **Check feature engineering** - verify views are correct
3. **Review data source** - ensure training data is correct
4. **Try feature selection** - use only informative features
5. **Adjust hyperparameters** - tune model parameters

## If Nothing Works

If performance remains poor after all checks:

1. **Verify dataset**: The Kaggle dataset should have proven churn prediction capability
2. **Check data mapping**: Ensure features are correctly mapped from source
3. **Review feature views**: Verify `create_feature_views.sql` is creating meaningful features
4. **Consider different approach**: May need to re-examine feature engineering strategy

## Contact Points

- Check `docs/DATA_MAPPING_DOCUMENT.md` for feature mapping
- Check `sql/create_feature_views.sql` for feature engineering
- Check `scripts/validate_churn_data.py` for data validation
