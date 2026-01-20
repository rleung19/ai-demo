# Dataset Source and Preparation

This document summarizes the churn dataset used in the demo and how it is prepared for Oracle Autonomous Database (ADB) and the ML pipeline.

## 1. Dataset Source

- **Primary source**: Kaggle churn dataset by `dhairyajeetsingh` (telecom-style customer churn).
- The raw dataset includes:
  - Customer demographics
  - Usage metrics
  - Contract information
  - Binary churn label

The raw data is downloaded and then transformed to match the ADB schema used by this project.

## 2. High-Level Preparation Steps

From the project root:

```bash
cd /Users/rleung/Projects/aiworkshop2026/ai-demo

# 1. Download and inspect the dataset
python scripts/download_kaggle_dataset.py
python scripts/examine_dataset.py

# 2. Map dataset to the unified user schema
python scripts/prepare_dataset_for_oml.py
python scripts/map_dataset_to_users.py

# 3. Create and populate tables in ADB
python scripts/create_tables.py
python scripts/ingest_churn_data.py
python scripts/create_feature_views.py
```

## 3. Target Tables in ADB

The preparation scripts populate these key tables in the `OML` schema:

- `OML.CHURN_DATASET_TRAINING`
  - Normalized training dataset with churn label and engineered features.
- `OML.USER_PROFILES`
  - Denormalized customer profile table used by the dashboard and risk factors.
- Feature views (created by `create_feature_views.py`)
  - Training/validation views for the ML pipeline.

Customer identities are aligned with:

- `ADMIN.USERS` – master user table for the demo app.
- All `ADMIN.USERS.ID` values are mapped to `OML.USER_PROFILES.USER_ID`.

## 4. Data Quality & Validation

After ingestion and mapping, run:

```bash
python scripts/validate_churn_data.py
python scripts/validate_model_performance.py
```

These scripts verify:

- Reasonable row counts for training and user profile tables.
- All `USER_PROFILES.USER_ID` values:
  - Exist in `ADMIN.USERS.ID`.
  - Cover every `ADMIN.USERS.ID` (no unmapped users).
- Churn rates and basic feature ranges are sane.
- ML performance threshold (AUC > 0.70) is met.

## 5. Relationship to Risk Factors

The risk factor queries in:

- `server/routes/churn/risk-factors.ts`
- `app/api/kpi/churn/risk-factors/route.ts`

depend on:

- `OML.USER_PROFILES` (behavioral/engagement metrics)
- `OML.CHURN_PREDICTIONS` (model outputs)
- `ADMIN.USERS` (VIP/segment flags)

See:

- `docs/RISK_FACTORS_DATA_ANALYSIS.md`
- `docs/RISK_FACTORS_CALCULATION.md`

for detailed reasoning and SQL examples behind the risk factor logic.

