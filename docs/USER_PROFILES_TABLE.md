# USER_PROFILES Table Design

## Table Name

**`OML.USER_PROFILES`**

## Purpose

Store **input features** for churn prediction on actual users. This table contains:
- Real user profiles mapped to `ADMIN.USERS.ID`
- **Feature data only** (input to the model)
- **NOT** where predictions are stored (see `CHURN_PREDICTIONS` table)

**Important**: This table provides features for prediction. The **predicted churn scores** are stored in a separate `CHURN_PREDICTIONS` table.

## Key Characteristics

- **Rows**: 4,142 (one per active user)
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Churn Rate**: 28.90% (maintains exact rate via stratified sampling)
- **Purpose**: Predict churn for actual users

## Usage

### 1. Model Scoring (Input Features)
```sql
-- Get features for model scoring
SELECT 
    USER_ID,
    AGE,
    TOTAL_PURCHASES,
    DAYS_SINCE_LAST_PURCHASE,
    -- ... all features (except CHURNED) ...
FROM OML.USER_PROFILES
WHERE USER_ID = :user_id
```

**Note**: `CHURNED` column in this table is the **historical label** (for reference), not the prediction.

### 2. Batch Scoring Workflow
```python
# Step 1: Load features from USER_PROFILES
features = load_features_from_user_profiles()

# Step 2: Score with model
predictions = model.predict(features)

# Step 3: Store predictions in CHURN_PREDICTIONS table
save_predictions_to_churn_predictions_table(predictions)
```

### 3. API Responses
```sql
-- Get prediction for user (from CHURN_PREDICTIONS table)
SELECT 
    USER_ID,
    PREDICTED_CHURN_PROBABILITY,
    PREDICTED_CHURN_LABEL,
    PREDICTION_DATE,
    MODEL_VERSION
FROM OML.CHURN_PREDICTIONS
WHERE USER_ID = :user_id
```

## Relationship to Other Tables

### Training Data
- **`OML.CHURN_DATASET_TRAINING`** (45,858 rows)
  - Used to train the model
  - No real user mapping needed
  - Contains features + CHURNED label

### User Profiles (Input Features)
- **`OML.USER_PROFILES`** (4,142 rows)
  - Contains **input features** for actual users
  - Real user mapping required
  - Used as input to model for scoring
  - Contains historical CHURNED label (for reference only)

### Predictions (Model Output)
- **`OML.CHURN_PREDICTIONS`** (separate table)
  - Stores **predicted churn scores** from the model
  - Contains: USER_ID, PREDICTED_CHURN_PROBABILITY, PREDICTED_CHURN_LABEL, etc.
  - Updated when model scores users
  - Used for API responses

## Data Flow

```
Training Phase:
  CHURN_DATASET_TRAINING → Train Model → Save Model to OML Datastore

Prediction Phase:
  USER_PROFILES (features) → Load Model → Score → CHURN_PREDICTIONS (predictions) → API Response
```

**Key Point**: 
- `USER_PROFILES` = **Input** (features)
- `CHURN_PREDICTIONS` = **Output** (predictions)

## Next Steps

1. Create table `OML.USER_PROFILES` (Task 1.3)
2. Load data from `data/processed/churn_dataset_mapped.csv` (Task 2.5)
3. Validate data loaded correctly (Task 2.6)
4. Use for model scoring in API (Task 4.x)
