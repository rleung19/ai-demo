# Task 3.10: Model Versioning and Performance Tracking

## Status

✅ **Completed**: Model registry table created and integrated into training pipeline

## What Was Created

### 1. Model Registry Table

**File**: `sql/create_model_registry_table.sql`

**Table**: `OML.MODEL_REGISTRY`

**Purpose**: Track all trained models with versioning, performance metrics, and metadata

**Key Columns**:
- `MODEL_ID` - Unique identifier (timestamp-based)
- `MODEL_NAME` - Model name (e.g., XGBoost, CatBoost)
- `MODEL_VERSION` - Version identifier
- `MODEL_FILE_PATH` - Path to pickle file
- `METADATA_FILE_PATH` - Path to metadata JSON
- Performance metrics (AUC, Accuracy, Precision, Recall, F1)
- Training information (date, duration, samples, features)
- Status (ACTIVE, DEPRECATED, ARCHIVED)
- `IS_PRODUCTION` - Flag for production models

### 2. Table Creation Script

**File**: `scripts/create_model_registry_table.py`

**Usage**:
```bash
python scripts/create_model_registry_table.py
```

### 3. Training Script Integration

**File**: `scripts/local/train_churn_model_local.py`

**Changes**:
- Added `register_model_in_db()` function
- Updated `save_model()` to register models automatically
- Tracks training duration, sample counts, and all metadata

## Usage

### Create Registry Table

```bash
python scripts/create_model_registry_table.py
```

### Automatic Registration

Models are automatically registered when training completes:

```bash
python scripts/local/train_churn_model_local.py
```

The training script will:
1. Save model to disk (pickle + metadata JSON)
2. Register model in `OML.MODEL_REGISTRY` table
3. Store all performance metrics and metadata

### Query Registry

```sql
-- Get all models
SELECT MODEL_ID, MODEL_NAME, AUC_SCORE, TRAINING_DATE, STATUS
FROM OML.MODEL_REGISTRY
ORDER BY TRAINING_DATE DESC;

-- Get best performing model
SELECT * FROM OML.MODEL_REGISTRY
WHERE AUC_SCORE = (SELECT MAX(AUC_SCORE) FROM OML.MODEL_REGISTRY);

-- Get production model
SELECT * FROM OML.MODEL_REGISTRY
WHERE IS_PRODUCTION = 1;

-- Get model history
SELECT MODEL_ID, MODEL_NAME, AUC_SCORE, TRAINING_DATE
FROM OML.MODEL_REGISTRY
WHERE MODEL_NAME = 'XGBoost'
ORDER BY TRAINING_DATE DESC;
```

### Set Production Model

```sql
-- Mark a model as production
UPDATE OML.MODEL_REGISTRY
SET IS_PRODUCTION = 1, STATUS = 'ACTIVE'
WHERE MODEL_ID = '20260118_184459';

-- Unmark other models
UPDATE OML.MODEL_REGISTRY
SET IS_PRODUCTION = 0
WHERE MODEL_ID != '20260118_184459';
```

### Deprecate Model

```sql
UPDATE OML.MODEL_REGISTRY
SET STATUS = 'DEPRECATED'
WHERE MODEL_ID = 'old_model_id';
```

## Benefits

1. ✅ **Version Tracking**: All models tracked with unique IDs
2. ✅ **Performance History**: Compare models over time
3. ✅ **Model Lineage**: Track which models were used when
4. ✅ **Production Management**: Flag production models
5. ✅ **Rollback Support**: Easy to revert to previous models
6. ✅ **Audit Trail**: Complete history of model training

## Related Files

- `sql/create_model_registry_table.sql` - Table schema
- `scripts/create_model_registry_table.py` - Table creation script
- `scripts/local/train_churn_model_local.py` - Training script (with registration)
