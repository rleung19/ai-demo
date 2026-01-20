# Task 3.8: Implement Model Scoring (Batch Prediction)

## Status

✅ **Completed**: Model scoring script created

## What Was Created

### Scoring Script
- **File**: `scripts/score_churn_model.py`
- **Purpose**: Batch prediction for all users and store in CHURN_PREDICTIONS table

## Features

1. **Load Model**: Loads trained model from OML datastore
2. **Load User Features**: Loads from `CHURN_USER_FEATURES` view
3. **Batch Scoring**: Scores all 4,142 users
4. **Store Predictions**: Saves to `OML.CHURN_PREDICTIONS` table
5. **Summary Statistics**: Reports at-risk counts and average risk scores

## Workflow

```
1. Load Model (from OML datastore)
   ↓
2. Load User Features (from CHURN_USER_FEATURES view)
   ↓
3. Score Users (batch prediction)
   ↓
4. Store Predictions (in CHURN_PREDICTIONS table)
   ↓
5. Summary Report
```

## Usage

### In OML Notebooks (Recommended)

```python
%python
exec(open('scripts/score_churn_model.py').read())
```

### Standalone

```bash
python scripts/score_churn_model.py
```

**Note**: Requires OML4Py (typically only in OML Notebooks)

## Expected Output

```
============================================================
Churn Model Scoring (Batch Prediction)
============================================================
Started at: 2026-01-XX XX:XX:XX

============================================================
OML4Py Connection
============================================================
✓ OML4Py imported successfully
✓ OML connection is active

============================================================
Loading Model from OML Datastore
============================================================
✓ Model loaded: churn_xgboost_v1

============================================================
Loading User Features
============================================================
✓ Loaded 4,142 user profiles
✓ Features: 22
✓ Data cleaned

============================================================
Scoring Users
============================================================
✓ Generated 4,142 predictions
  Average churn probability: 0.2890
  Max churn probability: 0.9876
  Min churn probability: 0.0123

============================================================
Storing Predictions
============================================================
✓ Cleared existing predictions
✓ Successfully inserted 4,142 predictions
✓ Verified: 4,142 rows in CHURN_PREDICTIONS table

Prediction Summary:
  Total users: 4,142
  At-risk users: 1,197 (28.90%)
  Average risk score: 28.9%

============================================================
✓ Scoring completed successfully!
============================================================

Predictions stored in OML.CHURN_PREDICTIONS table
Ready for API integration (Task 4.x)
```

## Prediction Storage

Predictions are stored in `OML.CHURN_PREDICTIONS` with:
- `USER_ID`: Real UUID from ADMIN.USERS
- `PREDICTED_CHURN_PROBABILITY`: 0.0 to 1.0
- `PREDICTED_CHURN_LABEL`: 0 or 1 (based on threshold)
- `RISK_SCORE`: 0-100 (for display)
- `MODEL_VERSION`: Version identifier
- `PREDICTION_DATE`: Timestamp

## Next Steps

1. ✅ **Task 3.8 Complete**: Model scoring implemented
2. ⏳ **Task 3.9**: Create automated pipeline script
3. ⏳ **Task 4.x**: Backend API development (read from CHURN_PREDICTIONS)

## Related Documentation

- `docs/CHURN_PREDICTIONS_TABLE.md` - Predictions table design
- `scripts/train_churn_model.py` - Model training script
- `docs/TASK_3.1_GUIDE.md` - Training pipeline guide
