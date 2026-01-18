# OML4Py Training Workflow

## Visual Workflow

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Open OML Notebooks                            │
│  Oracle Cloud Console → ADB → OML Notebooks           │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Create Notebook                               │
│  New Notebook → Python → Name: churn_model_training    │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 3: Copy Cells from                               │
│  oml-notebooks/train_churn_model_notebook.py           │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 4: Run Cells Sequentially                        │
│                                                         │
│  Cell 1: Import oml                                    │
│  Cell 2: Load data (oml.sync)                          │
│  Cell 3: Split data                                    │
│  Cell 4: Train model (oml.xgb().fit())                 │
│         └─→ Training happens IN ADB                    │
│  Cell 5: Evaluate model                                │
│  Cell 6: Save model (oml.ds.save())                   │
│         └─→ Model saved to OML Datastore               │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 5: Model Ready!                                   │
│  - Model trained in ADB                                │
│  - Model saved in OML Datastore                         │
│  - Ready for scoring                                    │
└─────────────────────────────────────────────────────────┘
```

## Key OML4Py Functions Used

### 1. Data Loading
```python
# Load from database view
train_data_oml = oml.sync(view='CHURN_TRAINING_DATA')
train_data_pd = train_data_oml.pull()  # Convert to pandas
```

### 2. Data Pushing
```python
# Push pandas DataFrame to database
train_oml = oml.push(train_combined_pd)
```

### 3. Model Creation
```python
# Create XGBoost classifier
xgb_model = oml.xgb('classification')
```

### 4. Model Training
```python
# Train model (happens IN ADB)
xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
```

### 5. Model Prediction
```python
# Generate predictions (happens IN ADB)
y_pred_proba = xgb_model.predict_proba(X_test_oml)
y_pred_proba_pd = y_pred_proba.pull()  # Convert to pandas
```

### 6. Model Saving
```python
# Save to OML Datastore
oml.ds.save(
    {'model': xgb_model},
    'churn_xgboost_v1',
    description='Churn model',
    overwrite=True
)
```

## Where Training Happens

```
┌─────────────────────────────────────────────────────────┐
│  OML Notebooks UI (Web Browser)                        │
│  - You run Python cells                                 │
│  - OML4Py sends commands to ADB                         │
└────────────────────┬──────────────────────────────────┘
                     │
                     │ SQL/OML API calls
                     │
┌────────────────────▼──────────────────────────────────┐
│  Oracle ADB (Remote Database)                          │
│                                                         │
│  ┌─────────────────────────────────────────────┐     │
│  │  OML Engine                                  │     │
│  │  - XGBoost training happens HERE            │     │
│  │  - Data processing happens HERE               │     │
│  │  - Model stored in OML Datastore             │     │
│  └─────────────────────────────────────────────┘     │
│                                                         │
│  ┌─────────────────────────────────────────────┐     │
│  │  Database Tables/Views                       │     │
│  │  - CHURN_TRAINING_DATA (view)                │     │
│  │  - CHURN_USER_FEATURES (view)                │     │
│  │  - CHURN_PREDICTIONS (table)                 │     │
│  └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Complete Example

See **`oml-notebooks/train_churn_model_notebook.py`** for all cells ready to copy-paste.

## Next Steps

After training:
1. **Score users**: Run `scripts/score_churn_model.py` in OML Notebooks
2. **Check predictions**: Query `OML.CHURN_PREDICTIONS` table
3. **Build API**: Read from `CHURN_PREDICTIONS` table for your dashboard

## Documentation

- **Quick Start**: `docs/OML4PY_QUICK_START.md`
- **Complete Guide**: `docs/HOW_TO_USE_OML4PY.md`
- **How It Works**: `docs/OML4PY_EXPLAINED.md`
