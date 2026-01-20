# CHURNED Field Design: Numeric vs Categorical

## Current Design: NUMBER(1) with 0/1

**Current**: `CHURNED NUMBER(1)` with values:
- `0` = Retained (not churned)
- `1` = Churned

## Why Numeric is Better for ML Models

### 1. **OML4Py/XGBoost Requirement**
- OML4Py XGBoost expects **numeric labels** for binary classification
- The model training code uses: `y_train_oml = train_oml['CHURNED']` where CHURNED must be numeric
- sklearn metrics (precision, recall, AUC) expect numeric labels (0/1)

### 2. **Mathematical Operations**
- Can calculate churn rate: `CHURNED.mean() * 100`
- Can use in aggregations: `SUM(CHURNED)`, `AVG(CHURNED)`
- Can use in WHERE clauses: `WHERE CHURNED = 1`
- Can use in CASE statements: `CASE WHEN CHURNED = 1 THEN ...`

### 3. **Performance**
- NUMBER(1) is 1 byte vs VARCHAR2(10) which is variable length
- More efficient for indexes
- Faster comparisons in SQL

### 4. **Industry Standard**
- Binary classification labels are almost always 0/1 in ML pipelines
- Matches the format of model predictions (PREDICTED_CHURN_LABEL)

## If We Used Categorical (VARCHAR2)

### Problems:
- ❌ OML4Py would need conversion: `df['CHURNED'].map({'YES': 1, 'NO': 0})`
- ❌ Cannot use `.mean()` directly
- ❌ More storage space
- ❌ Slower comparisons
- ❌ Inconsistent with model predictions (which are 0/1)

### Benefits:
- ✅ More readable in queries: `WHERE CHURNED = 'YES'`
- ✅ Self-documenting

## Recommended Solution: Keep Numeric + Add View

**Best of both worlds**: Keep numeric in base tables, add a view for readability.

### Option 1: Add Computed Column in View (Recommended)

```sql
-- Create readable view
CREATE OR REPLACE VIEW OML.USER_PROFILES_READABLE AS
SELECT 
    USER_ID,
    AGE,
    -- ... other columns ...
    CHURNED,
    CASE 
        WHEN CHURNED = 1 THEN 'CHURNED'
        WHEN CHURNED = 0 THEN 'RETAINED'
        ELSE 'UNKNOWN'
    END AS CHURN_STATUS,
    -- ... rest of columns ...
FROM OML.USER_PROFILES;
```

### Option 2: Add Comments (Current Approach)

```sql
COMMENT ON COLUMN OML.USER_PROFILES.CHURNED IS 
    'Historical churn label: 0 = retained, 1 = churned';
```

This is already in our schema!

### Option 3: Use Check Constraint with Meaningful Values

We already have:
```sql
CONSTRAINT CHK_CHURNED CHECK (CHURNED IN (0, 1))
```

## Recommendation

✅ **Keep CHURNED as NUMBER(1) with 0/1** for these reasons:

1. **ML Compatibility**: OML4Py/XGBoost requires numeric labels
2. **Performance**: More efficient storage and queries
3. **Consistency**: Matches model predictions format
4. **Industry Standard**: Binary classification uses 0/1
5. **Readability**: Can add views/comments for documentation

## Current Schema is Correct

Our current design with:
- `CHURNED NUMBER(1)` with check constraint `CHECK (CHURNED IN (0, 1))`
- Comments explaining: `0 = retained, 1 = churned`
- Consistent with `PREDICTED_CHURN_LABEL NUMBER(1)`

This is the **optimal design** for ML models.

## If You Still Want Categorical

If you have a specific reason for categorical (e.g., business requirements, reporting needs), we can:
1. Keep base table as numeric (for ML)
2. Add a view with categorical column
3. Or add a computed column in queries

But the base table should remain numeric for ML compatibility.
