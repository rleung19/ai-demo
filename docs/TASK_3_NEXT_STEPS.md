# Task 3: Next Steps

## Current Status

✅ **Completed**: Tasks 3.1-3.7, 3.9, 3.11
- Model training pipeline (XGBoost, AUC 0.9269)
- Model evaluation and threshold optimization
- Model saving (pickle files)
- Automated pipeline script
- Model comparison report

## Remaining Tasks

### ⏳ Task 3.8: Update Model Scoring for Local Model

**Status**: Needs update  
**Current**: Uses OML4Py to load model from datastore  
**Needed**: Update to load pickle file and score users

**What needs to be done**:
1. Update `scripts/score_churn_model.py` to:
   - Load model from pickle file (instead of OML datastore)
   - Use local model for predictions (instead of OML4Py model)
   - Keep database storage of predictions (already works)

2. Alternative: Create `scripts/score_churn_model_local.py`:
   - New script specifically for local model scoring
   - Loads latest model from `models/` directory
   - Scores users and stores in `OML.CHURN_PREDICTIONS`

**Files to update**:
- `scripts/score_churn_model.py` - Update for local model
- OR create `scripts/score_churn_model_local.py` - New local scoring script

### ⏳ Task 3.10: Model Versioning and Performance Tracking

**Status**: Basic versioning exists, needs enhancement  
**Current**: Timestamped files with metadata JSON  
**Needed**: Enhanced tracking in database

**What needs to be done**:
1. Create model registry table in database:
   - Model ID, version, timestamp
   - Performance metrics (AUC, accuracy, etc.)
   - Model file path
   - Training parameters

2. Update training script to:
   - Register model in database after training
   - Track model lineage and versions
   - Support model rollback

**Optional enhancements**:
- Model comparison dashboard
- Performance tracking over time
- A/B testing support

### ⏳ Task 3.12: Test Pipeline End-to-End

**Status**: Training tested, scoring needs update first  
**Needed**: Full pipeline test after Task 3.8 update

**What needs to be done**:
1. Run complete pipeline:
   - Train model (`train_churn_model_local.py`)
   - Score users (updated `score_churn_model.py`)
   - Verify predictions in database
   - Check data quality

2. Validate:
   - Model performance matches expectations
   - Predictions stored correctly
   - All users scored
   - Data integrity maintained

## Recommended Order

1. **Task 3.8** (Priority 1) - Update scoring script
   - Enables full pipeline testing
   - Required for API integration (Task 4)

2. **Task 3.12** (Priority 2) - End-to-end testing
   - Validates complete workflow
   - Ensures everything works together

3. **Task 3.10** (Priority 3) - Enhanced versioning
   - Nice to have for production
   - Can be done in parallel with Task 4

## Quick Start: Task 3.8

To update the scoring script:

1. **Load model from pickle**:
   ```python
   import pickle
   model_path = 'models/churn_model_xgboost_YYYYMMDD_HHMMSS.pkl'
   with open(model_path, 'rb') as f:
       model = pickle.load(f)
   ```

2. **Load metadata**:
   ```python
   import json
   metadata_path = 'models/churn_model_xgboost_YYYYMMDD_HHMMSS_metadata.json'
   with open(metadata_path, 'r') as f:
       metadata = json.load(f)
   feature_cols = metadata['feature_cols']
   optimal_threshold = metadata['optimal_threshold']
   ```

3. **Score users**:
   ```python
   # Load user features from view
   # Use model.predict_proba() locally
   # Store predictions in database
   ```

## Related Documentation

- `docs/TASK_3_SUMMARY.md` - Current Task 3 status
- `docs/TASK_3_LOCAL_TRAINING.md` - Local training approach
- `scripts/train_churn_model_local.py` - Training script (reference)
- `scripts/score_churn_model.py` - Scoring script (needs update)
