# Quick Reference Card

## OML4Py Common Patterns

### Connection
```python
import oml
print("OML Connected:", oml.isconnected())
```

### Sync View/Table
```python
# For views
features = oml.sync(view='CHURN_FEATURES')

# For tables
data = oml.sync(table='MY_TABLE')
```

### Push Pandas DataFrame to OML
```python
# Push pandas DataFrame to OML (creates temporary table)
oml_df = oml.push(pandas_df)
```

### Pull OML DataFrame to Pandas
```python
# Convert OML DataFrame to pandas
pandas_df = oml_df.pull()
```

### Create XGBoost Model
```python
# Create model
xgb_model = oml.xgb('classification')

# Fit model (X and y must be OML DataFrames/Vectors)
xgb_model = xgb_model.fit(X_oml, y_oml)
```

### Get Predictions
```python
# Predict probabilities
y_proba_oml = xgb_model.predict_proba(X_oml)
y_proba_pd = y_proba_oml.pull()
# Extract positive class probabilities
if isinstance(y_proba_pd, pd.DataFrame):
    if 1 in y_proba_pd.columns:
        y_proba = y_proba_pd[1].values
    elif len(y_proba_pd.columns) == 2:
        y_proba = y_proba_pd.iloc[:, 1].values
```

### Feature Importance
```python
# Get importance (it's a property, not a method!)
importance_df = xgb_model.importance.pull()
# Extract ATTRIBUTE_NAME and GAIN columns
```

### Save/Load Model
```python
# Save
oml.ds.save({'model_key': model}, 'model_name', description='...', overwrite=True)

# Load
loaded_dict = oml.ds.load('model_name')
model = loaded_dict['model_key']  # or loaded_dict[0] if it's a list
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: table does not exist` | Using `table=` for view | Use `oml.sync(view='VIEW_NAME')` |
| `AttributeError: 'String' object has no attribute 'value_counts'` | Using pandas methods on OML Vector | Use `.pull()` to convert to pandas first |
| `ValueError: y should be either string or oml vector` | Wrong format for target | Pass target column name as string or OML Vector |
| `TypeError: push() got an unexpected keyword argument 'table'` | `oml.push()` doesn't accept `table` | Remove `table` parameter, `oml.push()` creates temp table |
| `ORA-00932: expression is of data type TIMESTAMP` | Non-numeric column in features | Exclude or convert TIMESTAMP columns |
| `ORA-40104: invalid training data` | Data quality issues | Clean NaN, infinity, ensure all numeric |

## Magic Commands in OML Notebooks

- `%script` - SQL code
- `%python` - Python code
- `%md` - Markdown text

## Data Cleaning Checklist

Before training:
- [ ] Replace infinity with NaN: `df.replace([np.inf, -np.inf], np.nan)`
- [ ] Fill NaN: `df.fillna(0)` or `df.fillna(df.median())`
- [ ] Convert to numeric: `pd.to_numeric(df[col], errors='coerce')`
- [ ] Exclude non-numeric columns (or convert categoricals)
- [ ] Verify no NULLs: `df.isna().sum().sum() == 0`

## Model Evaluation Checklist

- [ ] Calculate all metrics (Accuracy, Precision, Recall, F1, AUC-ROC)
- [ ] Generate confusion matrix
- [ ] Optimize threshold (not just 0.5)
- [ ] Compare with baseline
- [ ] Analyze feature importance
- [ ] Score all customers
- [ ] Generate cohort-level metrics
