# Task 3.8: Model Scoring - Complete

## Status

✅ **Completed**: Local model scoring script created and organized

## What Was Created

### 1. Script Reorganization

Scripts are now organized into clear directories:

```
scripts/
├── oml4py/              # OML4Py scripts (preserved)
│   ├── train_churn_model.py
│   └── score_churn_model.py
├── local/               # Local model scripts (production)
│   ├── train_churn_model_local.py
│   ├── score_churn_model_local.py  ← NEW
│   ├── train_models_local_comparison.py
│   └── ml_pipeline.py
└── shared/              # Shared utilities
    └── store_predictions.py  ← NEW
```

### 2. New Local Scoring Script

**File**: `scripts/local/score_churn_model_local.py`

**Features**:
- ✅ Loads model from pickle file (finds latest automatically)
- ✅ Connects to ADB as **OML user**
- ✅ Loads user features from `OML.CHURN_USER_FEATURES` view (SQL query)
- ✅ Scores users with local model (XGBoost)
- ✅ Stores predictions in `OML.CHURN_PREDICTIONS` table
- ✅ Uses shared `store_predictions()` function

**Key Functions**:
- `find_latest_model()` - Finds most recent model file
- `load_model_from_pickle()` - Loads model + metadata
- `load_user_features_from_db()` - SQL query to get features
- `score_users_local()` - Local model prediction
- `store_predictions()` - Shared utility (from `scripts/shared/`)

### 3. Shared Utility Module

**File**: `scripts/shared/store_predictions.py`

**Purpose**: Shared function for storing predictions in database
- Used by both OML4Py and local scoring scripts
- Handles truncation, insertion, verification, statistics
- Avoids code duplication

## Usage

### Basic Usage (Latest Model)
```bash
python scripts/local/score_churn_model_local.py
```

### Specify Model Path
```bash
python scripts/local/score_churn_model_local.py \
  --model-path models/churn_model_xgboost_20260118_184459.pkl
```

### Override Threshold
```bash
python scripts/local/score_churn_model_local.py --threshold 0.4
```

## Workflow

```
1. Load Model
   ↓
   - Find latest .pkl file in models/
   - Load model object
   - Load metadata JSON (feature cols, threshold, performance)
   
2. Connect to ADB (as OML user)
   ↓
   - Uses ADB_USERNAME=OML (default)
   - Wallet-based authentication
   
3. Load User Features
   ↓
   - SQL: SELECT * FROM OML.CHURN_USER_FEATURES
   - Clean data (NaN, infinity)
   - Extract USER_ID and feature columns
   
4. Score Users
   ↓
   - Align features with training order
   - model.predict_proba(X_users)
   - Extract churn probabilities
   
5. Store Predictions
   ↓
   - Truncate OML.CHURN_PREDICTIONS
   - Insert predictions (USER_ID, probability, label, risk score)
   - Verify row counts
   - Generate summary statistics
```

## Connection Details

**All scripts connect as OML user**:
- Username: `OML` (from `ADB_USERNAME`, defaults to 'OML')
- Accesses: `OML.CHURN_USER_FEATURES` view
- Stores in: `OML.CHURN_PREDICTIONS` table

**Environment Variables Required**:
```bash
ADB_WALLET_PATH=/path/to/wallet
ADB_CONNECTION_STRING=your_connection_string
ADB_USERNAME=OML
ADB_PASSWORD=your_password
```

## Integration with Pipeline

The scoring script is integrated into the automated pipeline:

```bash
# Complete pipeline: train → score
python scripts/local/ml_pipeline.py
```

This runs:
1. `train_churn_model_local.py` - Train model
2. `score_churn_model_local.py` - Score users

## Benefits of This Approach

1. ✅ **Clear Separation**: OML4Py and local scripts in separate directories
2. ✅ **Preserved OML4Py**: Can revisit OML4Py approach later
3. ✅ **Shared Utilities**: No code duplication
4. ✅ **ADB Integration**: Stores predictions in database (not just local)
5. ✅ **Production Ready**: Uses best performing model (XGBoost, AUC 0.9269)

## Next Steps

1. ✅ **Task 3.8 Complete**: Local scoring script created
2. ⏳ **Task 3.12**: Test pipeline end-to-end
3. ⏳ **Task 4**: Backend API development (uses predictions from `OML.CHURN_PREDICTIONS`)

## Related Files

- `scripts/local/score_churn_model_local.py` - Main scoring script
- `scripts/shared/store_predictions.py` - Shared utility
- `scripts/local/ml_pipeline.py` - Automated pipeline
- `docs/TASK_3.8_EXPLANATION.md` - Detailed explanation of approach
