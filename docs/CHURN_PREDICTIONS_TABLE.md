# CHURN_PREDICTIONS Table Design

## Table Name

**`OML.CHURN_PREDICTIONS`**

## Purpose

Store **predicted churn scores** produced by the ML model for actual users. This table contains:
- Model predictions (churn probability, churn label)
- Prediction metadata (model version, prediction date)
- Used for API responses and dashboard display

## Key Characteristics

- **Rows**: One per user (matches USER_PROFILES)
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Updated**: When model scores users (batch or on-demand)
- **Purpose**: Store model predictions, not input features

## Table Schema

| Column | Data Type | Description |
|--------|-----------|-------------|
| `USER_ID` | VARCHAR2(36) | Foreign key to ADMIN.USERS.ID |
| `PREDICTED_CHURN_PROBABILITY` | NUMBER(5,4) | Churn probability (0.0 to 1.0) |
| `PREDICTED_CHURN_LABEL` | NUMBER(1) | Binary prediction (0 = retained, 1 = churned) |
| `RISK_SCORE` | NUMBER(3) | Risk score (0-100) for display |
| `MODEL_VERSION` | VARCHAR2(50) | Version of model used for prediction |
| `PREDICTION_DATE` | TIMESTAMP | When prediction was made |
| `LAST_UPDATED` | TIMESTAMP | Last update timestamp |
| `CONFIDENCE_SCORE` | NUMBER(5,4) | Model confidence (optional) |

## Relationship to USER_PROFILES

```
USER_PROFILES (Input Features)
    ↓
  Model Scoring
    ↓
CHURN_PREDICTIONS (Output Predictions)
```

- **USER_PROFILES**: Provides features → Model input
- **CHURN_PREDICTIONS**: Stores predictions → Model output

## Usage

### 1. Store Predictions After Scoring
```sql
-- After model scoring, insert/update predictions
INSERT INTO OML.CHURN_PREDICTIONS (
    USER_ID,
    PREDICTED_CHURN_PROBABILITY,
    PREDICTED_CHURN_LABEL,
    RISK_SCORE,
    MODEL_VERSION,
    PREDICTION_DATE
) VALUES (...)
```

### 2. API Responses
```sql
-- Get churn prediction for user
SELECT 
    USER_ID,
    PREDICTED_CHURN_PROBABILITY,
    PREDICTED_CHURN_LABEL,
    RISK_SCORE,
    PREDICTION_DATE,
    MODEL_VERSION
FROM OML.CHURN_PREDICTIONS
WHERE USER_ID = :user_id
```

### 3. Dashboard Aggregations
```sql
-- Get summary statistics
SELECT 
    COUNT(*) AS TOTAL_USERS,
    SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS AT_RISK_COUNT,
    AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS AVG_RISK_SCORE,
    SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN RISK_SCORE ELSE 0 END) AS TOTAL_RISK
FROM OML.CHURN_PREDICTIONS
```

## Workflow

### Batch Scoring Process

1. **Load Features**:
   ```python
   features = load_from_user_profiles()
   ```

2. **Score with Model**:
   ```python
   predictions = model.predict_proba(features)
   churn_probabilities = predictions[:, 1]  # Probability of churn
   ```

3. **Store Predictions**:
   ```python
   save_to_churn_predictions_table(
       user_ids=user_ids,
       probabilities=churn_probabilities,
       model_version='v1.0',
       prediction_date=datetime.now()
   )
   ```

4. **API Returns Predictions**:
   ```python
   # API reads from CHURN_PREDICTIONS table
   prediction = get_from_churn_predictions(user_id)
   return prediction
   ```

## Data Flow Summary

```
┌─────────────────────┐
│  USER_PROFILES      │  (Input Features)
│  - Features only    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Trained Model      │  (From OML Datastore)
│  - XGBoost          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  CHURN_PREDICTIONS  │  (Output Predictions)
│  - Probabilities    │
│  - Labels           │
│  - Risk Scores      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  API Response       │  (Dashboard Display)
└─────────────────────┘
```

## Next Steps

1. Create table `OML.CHURN_PREDICTIONS` (Task 1.3)
2. Implement prediction storage in ML pipeline (Task 3.8)
3. Update API to read from CHURN_PREDICTIONS (Task 4.x)
