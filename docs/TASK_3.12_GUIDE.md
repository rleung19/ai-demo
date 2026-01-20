# Task 3.12: End-to-End Pipeline Testing

## Status

✅ **Completed**: End-to-end test script created

## What Was Created

### Test Script

**File**: `scripts/local/test_pipeline_end_to_end.py`

**Purpose**: Comprehensive end-to-end testing of the complete ML pipeline

## Test Coverage

### Test 1: Data Availability
- Verifies training data exists
- Verifies user profiles exist
- Verifies feature views exist
- Checks row counts

### Test 2: Model Training
- Runs complete training pipeline
- Verifies model is saved
- Verifies metadata is saved

### Test 3: Model Scoring
- Runs scoring pipeline
- Verifies all users are scored
- Verifies predictions are generated

### Test 4: Predictions in Database
- Verifies predictions stored in `OML.CHURN_PREDICTIONS`
- Validates row counts match user profiles
- Checks data quality (NULLs, ranges, etc.)
- Validates probability ranges [0, 1]

### Test 5: Model Registry
- Verifies `MODEL_REGISTRY` table exists
- Checks latest model is registered
- Validates registry data

## Usage

### Run Complete Test

```bash
python scripts/local/test_pipeline_end_to_end.py
```

### Expected Output

```
============================================================
End-to-End Pipeline Test
============================================================
Started at: 2026-01-18 20:00:00

============================================================
Test 1: Data Availability
============================================================
✓ Training data: 45,858 rows
✓ User profiles: 4,142 rows
✓ Training view: 45,858 rows
✓ All data sources available

============================================================
Test 2: Model Training
============================================================
Running training pipeline...
[Training output...]
✓ Model training completed

============================================================
Test 3: Model Scoring
============================================================
Running scoring pipeline...
[Scoring output...]
✓ User scoring completed

============================================================
Test 4: Predictions in Database
============================================================
✓ Predictions stored: 4,142 rows
✓ User profiles: 4,142 rows
✓ All 4,142 users have predictions

Data Quality:
  Total predictions: 4,142
  NULL probabilities: 0
  NULL labels: 0
  Probability range: 0.0040 - 0.9854
  Average probability: 0.2876
✓ Data quality checks passed

============================================================
Test 5: Model Registry
============================================================
✓ Latest model in registry:
  ID: 20260118_200000
  Name: XGBoost
  AUC: 0.9269
  Training Date: 2026-01-18 20:00:00
  Status: ACTIVE

============================================================
Test Summary
============================================================
DATA            ✓ PASS
TRAINING        ✓ PASS
SCORING         ✓ PASS
PREDICTIONS     ✓ PASS
REGISTRY        ✓ PASS

✓ All tests passed! Pipeline is working correctly.
```

## What Gets Tested

1. **Data Pipeline**: Training data → Views → Features
2. **Training Pipeline**: Data → Model → Save → Registry
3. **Scoring Pipeline**: Model → Features → Predictions → Database
4. **Data Integrity**: Predictions match users, no NULLs, valid ranges
5. **Registry**: Models tracked correctly

## Validation Checks

- ✅ Row counts match between tables and views
- ✅ All users have predictions
- ✅ No NULL values in predictions
- ✅ Probabilities in valid range [0, 1]
- ✅ Model registered in database
- ✅ Performance metrics stored

## Troubleshooting

### Test 1 Fails: Data Availability
- **Issue**: Missing training data or views
- **Fix**: Run data ingestion scripts (Task 2.5, 2.7)

### Test 2 Fails: Model Training
- **Issue**: Training script errors
- **Fix**: Check dependencies, database connection, data quality

### Test 3 Fails: Model Scoring
- **Issue**: Scoring script errors
- **Fix**: Verify model file exists, check feature alignment

### Test 4 Fails: Predictions Quality
- **Issue**: NULL values, invalid ranges
- **Fix**: Check scoring script, model output format

### Test 5 Fails: Model Registry
- **Issue**: Table doesn't exist or model not registered
- **Fix**: Run `create_model_registry_table.py`, check training script

## Integration with CI/CD

This test script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Test ML Pipeline
  run: python scripts/local/test_pipeline_end_to_end.py
```

## Related Files

- `scripts/local/test_pipeline_end_to_end.py` - Test script
- `scripts/local/train_churn_model_local.py` - Training pipeline
- `scripts/local/score_churn_model_local.py` - Scoring pipeline
- `docs/TASK_3.10_GUIDE.md` - Model registry documentation
