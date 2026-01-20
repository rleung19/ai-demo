# Scripts Directory Structure

This directory contains all scripts organized by approach (OML4Py vs Local).

## Directory Structure

```
scripts/
├── oml4py/              # OML4Py-based scripts (in-database ML)
│   ├── train_churn_model.py
│   └── score_churn_model.py
├── local/               # Local model scripts (pickle files)
│   ├── train_churn_model_local.py
│   ├── score_churn_model_local.py
│   ├── train_models_local_comparison.py
│   └── ml_pipeline.py
├── shared/              # Shared utilities
│   └── store_predictions.py
└── [other scripts]      # Data preparation, validation, etc.
```

## OML4Py Scripts (`scripts/oml4py/`)

**Purpose**: Train and score models using Oracle Machine Learning (OML4Py) in-database.

### `train_churn_model.py`
- Trains model using OML4Py (in-database)
- Saves model to OML datastore
- Requires OML Notebooks environment

### `score_churn_model.py`
- Loads model from OML datastore
- Scores users using OML4Py
- Stores predictions in `OML.CHURN_PREDICTIONS`
- Uses shared `store_predictions()` function

**Usage**:
```bash
# In OML Notebooks:
%python
exec(open('scripts/oml4py/train_churn_model.py').read())
```

## Local Model Scripts (`scripts/local/`)

**Purpose**: Train and score models locally using pickle files.

### `train_churn_model_local.py`
- Trains model locally (XGBoost, CatBoost, etc.)
- Saves model as pickle file + metadata JSON
- Connects to ADB as OML user to load training data
- **Model**: XGBoost (AUC 0.9269)

**Usage**:
```bash
python scripts/local/train_churn_model_local.py
```

### `score_churn_model_local.py`
- Loads model from pickle file (finds latest automatically)
- Connects to ADB as OML user
- Loads user features from `OML.CHURN_USER_FEATURES` view
- Scores users with local model
- Stores predictions in `OML.CHURN_PREDICTIONS` (uses shared function)

**Usage**:
```bash
# Use latest model:
python scripts/local/score_churn_model_local.py

# Use specific model:
python scripts/local/score_churn_model_local.py --model-path models/churn_model_xgboost_20260118_184459.pkl

# Override threshold:
python scripts/local/score_churn_model_local.py --threshold 0.4
```

### `train_models_local_comparison.py`
- Compares multiple local models (XGBoost, CatBoost, LightGBM, etc.)
- Identifies best performing model
- Used for model selection

**Usage**:
```bash
python scripts/local/train_models_local_comparison.py
```

### `ml_pipeline.py`
- Orchestrates complete pipeline: train → score
- Uses local training and scoring scripts
- Automated workflow

**Usage**:
```bash
python scripts/local/ml_pipeline.py
```

## Shared Utilities (`scripts/shared/`)

### `store_predictions.py`
- Shared function for storing predictions in `OML.CHURN_PREDICTIONS` table
- Used by both OML4Py and local scoring scripts
- Handles:
  - Truncating table
  - Inserting predictions
  - Verification
  - Summary statistics

**Function Signature**:
```python
def store_predictions(connection, user_ids, churn_probabilities, 
                     model_version='v1.0', threshold=0.5):
    """Store predictions in CHURN_PREDICTIONS table"""
```

## Connection Details

### OML User Connection
All scripts connect to ADB as **OML user** by default:
- Username: `OML` (from `ADB_USERNAME` env var, defaults to 'OML')
- Password: From `ADB_PASSWORD` env var
- Connection String: From `ADB_CONNECTION_STRING` env var
- Wallet: From `ADB_WALLET_PATH` env var

### Required Environment Variables
```bash
ADB_WALLET_PATH=/path/to/wallet
ADB_CONNECTION_STRING=your_connection_string
ADB_USERNAME=OML
ADB_PASSWORD=your_password
```

## Model Files

Local models are saved to `models/` directory:
- **Model**: `churn_model_{model_name}_{timestamp}.pkl`
- **Metadata**: `churn_model_{model_name}_{timestamp}_metadata.json`

Example:
- `churn_model_xgboost_20260118_184459.pkl`
- `churn_model_xgboost_20260118_184459_metadata.json`

## Why Two Approaches?

1. **OML4Py**: In-database ML, good for Oracle-native workflows
2. **Local**: Better performance (AUC 0.9269 vs 0.50), more control, easier automation

**Current Recommendation**: Use **local approach** (better performance).

## Migration Notes

- OML4Py scripts preserved in `scripts/oml4py/` for future reference
- Local scripts in `scripts/local/` for production use
- Shared utilities in `scripts/shared/` to avoid duplication
