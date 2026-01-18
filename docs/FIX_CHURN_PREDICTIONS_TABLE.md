# Fix CHURN_PREDICTIONS Table

## Issue

The `OML.CHURN_PREDICTIONS` table has a different schema than expected.

### Current Table Structure

The existing table has:
- `CUSTOMER_ID` VARCHAR2(4000) NULL
- `CUSTOMER_SEGMENT` VARCHAR2(4000) NULL
- `TOTAL_SPENT` NUMBER(22) NULL
- `AFFINITY_CARD` NUMBER(22) NULL
- `DAYS_SINCE_LAST_PURCHASE` NUMBER(22) NULL
- `CHURN_RISK_SCORE` NUMBER(22) NULL

### Expected Table Structure

The table should have (from `create_churn_tables.sql`):
- `USER_ID` VARCHAR2(36) NOT NULL
- `PREDICTED_CHURN_PROBABILITY` NUMBER(5,4) NOT NULL
- `PREDICTED_CHURN_LABEL` NUMBER(1) NOT NULL
- `RISK_SCORE` NUMBER(3) NOT NULL
- `MODEL_VERSION` VARCHAR2(50) NOT NULL
- `PREDICTION_DATE` TIMESTAMP NOT NULL
- `LAST_UPDATED` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `CONFIDENCE_SCORE` NUMBER(5,4) NULL

## Solution

Run the fix script to recreate the table with the correct schema:

```bash
python scripts/fix_churn_predictions_table.py
```

**⚠️ WARNING**: This will:
- **DROP** the existing table
- **DELETE** all existing data
- Create a new table with the correct schema

## Steps

1. **Backup existing data** (if needed):
   ```sql
   CREATE TABLE OML.CHURN_PREDICTIONS_BACKUP AS 
   SELECT * FROM OML.CHURN_PREDICTIONS;
   ```

2. **Run the fix script**:
   ```bash
   python scripts/fix_churn_predictions_table.py
   ```

3. **Verify the table**:
   ```bash
   python scripts/verify_churn_predictions_table.py
   ```

4. **Test with notebooks**:
   - Import and run `train_churn_model.ipynb`
   - Import and run `score_churn_model.ipynb`
   - Check that predictions are stored correctly

## What the Script Does

1. Checks if table exists
2. Prompts for confirmation (if table exists)
3. Drops existing table (if confirmed)
4. Creates new table with correct schema
5. Adds table and column comments
6. Creates indexes for performance
7. Verifies the new structure

## After Fixing

After running the fix script, the table will be ready for:
- ✅ Model training (stores model metadata)
- ✅ Model scoring (stores predictions)
- ✅ API queries (returns predictions for dashboard)

## Alternative: Manual SQL

If you prefer to run SQL manually:

```sql
-- Drop existing table
DROP TABLE OML.CHURN_PREDICTIONS CASCADE CONSTRAINTS;

-- Create new table (from create_churn_tables.sql)
CREATE TABLE OML.CHURN_PREDICTIONS (
    USER_ID VARCHAR2(36) NOT NULL,
    PREDICTED_CHURN_PROBABILITY NUMBER(5,4) NOT NULL,
    PREDICTED_CHURN_LABEL NUMBER(1) NOT NULL,
    RISK_SCORE NUMBER(3) NOT NULL,
    MODEL_VERSION VARCHAR2(50) NOT NULL,
    PREDICTION_DATE TIMESTAMP NOT NULL,
    LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONFIDENCE_SCORE NUMBER(5,4),
    CONSTRAINT CHK_PREDICTED_LABEL CHECK (PREDICTED_CHURN_LABEL IN (0, 1)),
    CONSTRAINT CHK_PROBABILITY CHECK (PREDICTED_CHURN_PROBABILITY >= 0 AND PREDICTED_CHURN_PROBABILITY <= 1),
    CONSTRAINT CHK_RISK_SCORE CHECK (RISK_SCORE >= 0 AND RISK_SCORE <= 100),
    CONSTRAINT CHK_CONFIDENCE CHECK (CONFIDENCE_SCORE IS NULL OR (CONFIDENCE_SCORE >= 0 AND CONFIDENCE_SCORE <= 1)),
    CONSTRAINT PK_CHURN_PREDICTIONS PRIMARY KEY (USER_ID)
);

-- Add comments
COMMENT ON TABLE OML.CHURN_PREDICTIONS IS 'Predicted churn scores from ML model (output, not input features)';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.USER_ID IS 'Real UUID from ADMIN.USERS.ID';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.PREDICTED_CHURN_PROBABILITY IS 'Churn probability (0.0 to 1.0)';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.PREDICTED_CHURN_LABEL IS 'Binary prediction: 0 = retained, 1 = churned';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.RISK_SCORE IS 'Risk score (0-100) for display';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.MODEL_VERSION IS 'Version of model used for prediction';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.PREDICTION_DATE IS 'When prediction was made';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.CONFIDENCE_SCORE IS 'Model confidence (optional)';

-- Create indexes
CREATE INDEX IDX_CHURN_PRED_LABEL ON OML.CHURN_PREDICTIONS(PREDICTED_CHURN_LABEL);
CREATE INDEX IDX_CHURN_PRED_RISK ON OML.CHURN_PREDICTIONS(RISK_SCORE);
CREATE INDEX IDX_CHURN_PRED_DATE ON OML.CHURN_PREDICTIONS(PREDICTION_DATE);
CREATE INDEX IDX_CHURN_PRED_MODEL ON OML.CHURN_PREDICTIONS(MODEL_VERSION);
```
