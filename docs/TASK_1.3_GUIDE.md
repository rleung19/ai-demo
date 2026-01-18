# Task 1.3: Design Database Schema for OML Dataset Storage

## Status

✅ **Completed**: Database schema designed and SQL scripts created

## What Was Created

### SQL Schema Script
- **File**: `sql/create_churn_tables.sql`
- **Purpose**: Creates all three tables needed for churn prediction model

### Tables Created

1. **`OML.CHURN_DATASET_TRAINING`**
   - Training data (45,858 rows)
   - Placeholder USER_IDs (TRAIN_1, TRAIN_2, etc.)
   - All 25 features + CHURNED label

2. **`OML.USER_PROFILES`**
   - Input features for actual users (4,142 rows)
   - Real USER_IDs from `ADMIN.USERS.ID`
   - Same structure as training table
   - **Note**: Contains features only, NOT predictions

3. **`OML.CHURN_PREDICTIONS`**
   - Model predictions/output (4,142 rows)
   - Stores predicted churn scores
   - Includes: probability, label, risk score, model version, timestamps

## Schema Features

### Constraints
- Primary keys on all tables
- Check constraints for:
  - CHURNED values (0 or 1)
  - Probability ranges (0.0 to 1.0)
  - Risk score ranges (0 to 100)
  - Confidence score ranges (0.0 to 1.0)

### Indexes
- Performance indexes on:
  - CHURNED column (for filtering)
  - LIFETIME_VALUE (for LTV calculations)
  - DAYS_SINCE_LAST_PURCHASE (for cohort analysis)
  - PREDICTED_CHURN_LABEL (for at-risk counts)
  - RISK_SCORE (for sorting/filtering)
  - PREDICTION_DATE (for time-based queries)
  - MODEL_VERSION (for model tracking)

### Comments
- Table-level comments explaining purpose
- Column-level comments for key fields
- Clarifies that USER_PROFILES contains features only, not predictions

## How to Use

### 1. Connect to ADB as OML User

```bash
# Using SQL*Plus or SQL Developer
sqlplus OML@your_connection_string
```

### 2. Run Schema Creation Script

```sql
@sql/create_churn_tables.sql
```

Or copy/paste the contents of `sql/create_churn_tables.sql` into your SQL client.

### 3. Verify Tables Created

```sql
-- Check tables exist
SELECT TABLE_NAME FROM USER_TABLES 
WHERE TABLE_NAME IN (
    'CHURN_DATASET_TRAINING',
    'USER_PROFILES',
    'CHURN_PREDICTIONS'
);

-- Check row counts (should be 0 initially)
SELECT 
    'CHURN_DATASET_TRAINING' AS TABLE_NAME, COUNT(*) AS ROW_COUNT 
FROM OML.CHURN_DATASET_TRAINING
UNION ALL
SELECT 
    'USER_PROFILES' AS TABLE_NAME, COUNT(*) AS ROW_COUNT 
FROM OML.USER_PROFILES
UNION ALL
SELECT 
    'CHURN_PREDICTIONS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT 
FROM OML.CHURN_PREDICTIONS;
```

## Next Steps

1. ✅ **Task 1.3 Complete**: Schema designed
2. ⏳ **Task 2.5**: Create data ingestion script to load dataset into OML schema
3. ⏳ **Task 2.6**: Validate data loaded correctly

## Related Documentation

- `docs/DATA_MAPPING_DOCUMENT.md` - Column mappings and data types
- `docs/USER_PROFILES_TABLE.md` - USER_PROFILES table design
- `docs/CHURN_PREDICTIONS_TABLE.md` - CHURN_PREDICTIONS table design
- `docs/TABLE_DESIGN_SUMMARY.md` - Overview of all tables
