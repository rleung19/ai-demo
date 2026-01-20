# ML Pipeline Usage and Configuration

This document describes how to run the churn ML pipeline end-to-end using the scripts in the `scripts/` directory. It assumes you have already completed the ADB and wallet setup in `SETUP.md` and `docs/ADB_SETUP.md`.

## Overview

The pipeline has three main stages:

1. **Data ingestion & feature engineering** – Load the churn dataset into ADB and create feature views.
2. **Model training & evaluation** – Train an XGBoost model (OML4Py or local fallback) and validate performance.
3. **Scoring & model registry** – Score predictions for all customers and register the active model in `MODEL_REGISTRY`.

All scripts are designed to be idempotent where possible.

## 1. Data Ingestion & Preparation

From the project root:

```bash
cd /Users/rleung/Projects/aiworkshop2026/ai-demo

# 1.1 Download and prepare the raw dataset (if needed)
python scripts/download_kaggle_dataset.py
python scripts/prepare_dataset_for_oml.py

# 1.2 Create core tables and feature views in OML schema
python scripts/create_tables.py
python scripts/ingest_churn_data.py
python scripts/create_feature_views.py

# 1.3 Validate data quality and mapping
python scripts/validate_churn_data.py
```

After running these commands successfully, you should have:

- `OML.CHURN_DATASET_TRAINING` populated
- `OML.USER_PROFILES` populated and fully mapped to `ADMIN.USERS`
- Feature views created for training and analysis

## 2. Model Training & Evaluation

The primary local training pipeline lives under `scripts/local/`.

```bash
cd /Users/rleung/Projects/aiworkshop2026/ai-demo

# 2.1 Validate model performance on the current dataset
python scripts/validate_model_performance.py
```

This script:

- Loads data from the training view
- Splits into train/validation
- Trains an **XGBoost** model (local fallback if OML4Py is not available)
- Prints metrics:
  - AUC
  - Accuracy
  - Precision / Recall / F1

You should see AUC > 0.70 (current run ≈ 0.93).

## 3. End-to-End Pipeline (Train → Score → Register)

For a full end-to-end run:

```bash
cd /Users/rleung/Projects/aiworkshop2026/ai-demo

# 3.1 Run the end-to-end test pipeline
python scripts/local/test_pipeline_end_to_end.py
```

This orchestrates:

1. Data validation
2. Model training
3. Scoring predictions
4. Writing results into:
   - `OML.CHURN_PREDICTIONS`
   - `OML.MODEL_REGISTRY`

You can also run steps more manually:

```bash
# Train model locally and save artifacts
python scripts/local/train_churn_model_local.py

# Score customers using the trained model
python scripts/local/score_churn_model_local.py

# Store predictions into CHURN_PREDICTIONS
python scripts/shared/store_predictions.py
```

## 4. Configuration Notes

- All Python scripts rely on the same environment variables:
  - `ADB_WALLET_PATH`
  - `ADB_CONNECTION_STRING`
  - `ADB_USERNAME` / `ADB_PASSWORD`
  - `TNS_ADMIN` (usually same as wallet path)
- Oracle client initialization is handled inside each script via `oracledb` and the wallet path.

## 5. When to Re-Run the Pipeline

Re-run the pipeline when:

- You update the feature engineering logic or thresholds.
- You retrain the churn model with new data.
- You want to refresh predictions and risk factors ahead of a demo.

Typical refresh sequence:

```bash
python scripts/validate_churn_data.py
python scripts/validate_model_performance.py
python scripts/local/test_pipeline_end_to_end.py
```

