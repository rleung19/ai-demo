# Table Design Summary

## Three Main Tables

### 1. `OML.CHURN_DATASET_TRAINING`

**Purpose**: Training data for model development

- **Rows**: 45,858
- **Contains**: Features + CHURNED label
- **USER_ID**: Placeholder IDs (TRAIN_1, TRAIN_2, etc.)
- **Usage**: Train the model

---

### 2. `OML.USER_PROFILES`

**Purpose**: **Input features** for churn prediction on actual users

- **Rows**: 4,142 (one per active user)
- **Contains**: **Features only** (input to model)
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Usage**: 
  - Provides features to model for scoring
  - **NOT** where predictions are stored
  - Historical CHURNED label (for reference only)

**Key Point**: This is the **input** to the model, not the output.

---

### 3. `OML.CHURN_PREDICTIONS`

**Purpose**: **Store predicted churn scores** from the model (current/latest)

- **Rows**: One per user (matches USER_PROFILES)
- **Contains**: 
  - PREDICTED_CHURN_PROBABILITY
  - PREDICTED_CHURN_LABEL
  - RISK_SCORE
  - MODEL_VERSION
  - PREDICTION_DATE
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Usage**: 
  - Store **current** model predictions
  - API responses (latest predictions)
  - Dashboard display (summary metrics)

**Key Point**: This is the **output** from the model (current snapshot).

---

### 4. `OML.CHURN_PREDICTIONS_HISTORY`

**Purpose**: **Store historical predictions** for trend analysis

- **Rows**: Multiple per user (weekly snapshots)
- **Contains**: 
  - Same as CHURN_PREDICTIONS
  - Plus: SNAPSHOT_DATE (weekly)
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Usage**: 
  - Trend calculations ("↑ 12 from last week")
  - 7-week historical charts
  - Comparison of current vs. historical metrics

**Key Point**: This is the **historical tracking** for trends.

---

## Data Flow

```
┌─────────────────────────┐
│ CHURN_DATASET_TRAINING  │
│ (45,858 rows)
│ Features + Labels       │
└───────────┬─────────────┘
            │
            ▼ Train Model
┌─────────────────────────┐
│   Trained Model         │
│   (Saved to OML         │
│    Datastore)           │
└───────────┬─────────────┘
            │
            │ Score Users
            ▼
┌─────────────────────────┐
│   USER_PROFILES         │  ← INPUT (Features)
│   (4,142 rows)          │
│   Features only         │
└───────────┬─────────────┘
            │
            ▼ Model Prediction
┌─────────────────────────┐
│   CHURN_PREDICTIONS     │  ← OUTPUT (Current)
│   (4,142 rows)          │
│   Latest predictions    │
└───────────┬─────────────┘
            │
            ├───► Weekly Snapshot
            │
            ▼
┌─────────────────────────┐
│ CHURN_PREDICTIONS_      │  ← HISTORICAL (Trends)
│ HISTORY                 │
│ (Time-series)           │
│ Weekly snapshots        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   API Response          │
│   - Current metrics     │
│   - Trend calculations  │
│   - Historical charts   │
└─────────────────────────┘
```

## Key Distinctions

| Table | Purpose | Contains | Updated When |
|-------|---------|----------|--------------|
| **CHURN_DATASET_TRAINING** | Model training | Features + Labels | Once (data load) |
| **USER_PROFILES** | Model input | Features only | When user data changes |
| **CHURN_PREDICTIONS** | Model output | Current predictions | When model scores users |
| **CHURN_PREDICTIONS_HISTORY** | Trend tracking | Historical predictions | Weekly snapshot |

## API Workflow

1. **User requests churn prediction**
2. **API reads from `CHURN_PREDICTIONS`** (not USER_PROFILES)
3. **If prediction missing/old**: 
   - Load features from `USER_PROFILES`
   - Score with model
   - Store in `CHURN_PREDICTIONS`
   - Return prediction
4. **Return prediction from `CHURN_PREDICTIONS`**

---

## Next Steps

1. Create all four tables (Task 1.3)
2. Load training data (Task 2.5)
3. Load user profiles (Task 2.5)
4. Implement prediction storage (Task 3.8)
5. Implement weekly snapshot process (Task 3.9)
6. Update API to use CHURN_PREDICTIONS + HISTORY (Task 4.x)

## Additional Tables (Design During API)

The following can be designed during API development based on actual query patterns:
- Cohort assignment strategy (derive vs. store)
- Risk factors table (if pre-computation needed)
- Aggregation views (if performance optimization needed)
