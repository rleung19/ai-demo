# Model Training Guide

## Recommended Approach: OML4Py ✅

**Use OML4Py in OML Notebooks** - This is the recommended approach for training churn models.

### Quick Start
1. See **`docs/OML4PY_QUICK_START.md`** for a 5-step guide
2. See **`docs/HOW_TO_USE_OML4PY.md`** for complete documentation
3. Use **`oml-notebooks/train_churn_model_notebook.py`** for notebook cells

### Why OML4Py?
- ✅ Trains **in your database** (faster, more efficient)
- ✅ Stores models in **OML Datastore** (integrated)
- ✅ Keeps data **in database** (no data movement)
- ✅ Uses **in-database XGBoost** (optimized)

## Files

### For OML Notebooks (Recommended)

- **`oml-notebooks/train_churn_model_notebook.py`**: Notebook cells (copy-paste ready)
- **`scripts/train_churn_model.py`**: Complete script (can exec in notebook)
- **`scripts/score_churn_model.py`**: Scoring script (for OML Notebooks)

### Alternative Approach (Not Recommended)

- **`scripts/alternatives/train_churn_model_local.py`**: Local training (if OML4Py unavailable)

## Documentation

- **`docs/OML4PY_QUICK_START.md`**: Quick 5-step guide
- **`docs/HOW_TO_USE_OML4PY.md`**: Complete OML4Py guide
- **`docs/OML4PY_EXPLAINED.md`**: How OML4Py works
- **`docs/TASK_3.1_GUIDE.md`**: OML4Py connection guide
- **`docs/TASK_3.8_GUIDE.md`**: Model scoring guide

## Workflow

```
1. Open OML Notebooks (Oracle Cloud Console)
   ↓
2. Create new Python notebook
   ↓
3. Copy cells from train_churn_model_notebook.py
   ↓
4. Run cells sequentially
   ↓
5. Model trained and saved in ADB!
   ↓
6. Run score_churn_model.py to generate predictions
   ↓
7. Predictions stored in CHURN_PREDICTIONS table
```

## Need Help?

- **OML4Py not working?** See `docs/OML4PY_EXPLAINED.md`
- **View not found?** Run `scripts/create_feature_views.py`
- **Data not loaded?** Run `scripts/ingest_churn_data.py`
- **Scoring?** See `docs/TASK_3.8_GUIDE.md`
