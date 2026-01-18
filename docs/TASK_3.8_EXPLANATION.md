# Task 3.8: Update vs Create New Script - Explanation

## Current Script Structure

The current `scripts/score_churn_model.py` has **3 main parts**:

### Part 1: Model Loading (Lines 41-90) - **NEEDS UPDATE**
```python
def connect_oml():
    # Uses OML4Py to connect
    
def load_model(oml, model_name='churn_xgboost_v1'):
    # Loads model from OML datastore using oml.ds.load()
    # ❌ This won't work with local pickle files
```

### Part 2: User Feature Loading (Lines 91-120) - **KEEP (mostly)**
```python
def load_user_features(oml):
    # Loads from CHURN_USER_FEATURES view
    # Uses OML4Py to sync view
    # ✅ Can keep, but needs to use oracledb instead of OML4Py
```

### Part 3: Scoring (Lines 122-156) - **NEEDS UPDATE**
```python
def score_users(oml, model, X_users, feature_cols):
    # Uses OML4Py to push data and get predictions
    # model.predict_proba() is OML4Py model method
    # ❌ This won't work with local pickle model
```

### Part 4: Database Storage (Lines 158-242) - **KEEP AS-IS** ✅
```python
def store_predictions(connection, user_ids, churn_probabilities, ...):
    # ✅ This function is PERFECT and already tested
    # - Truncates table
    # - Inserts predictions
    # - Verifies row counts
    # - Generates summary statistics
    # - Handles errors properly
    # This is the "database storage logic" I mentioned
```

## Option 1: Update Current Script

**What changes:**
- Replace `connect_oml()` → `get_connection()` (use oracledb)
- Replace `load_model(oml)` → `load_model_from_pickle()` (load .pkl file)
- Replace `load_user_features(oml)` → `load_user_features_from_db()` (use SQL query)
- Replace `score_users(oml, model)` → `score_users_local(model)` (use local model.predict_proba())
- **Keep `store_predictions()` exactly as-is** ✅

**Pros:**
- ✅ Reuses existing, tested database storage logic
- ✅ Single script to maintain
- ✅ Less code duplication

**Cons:**
- ⚠️ Script becomes a hybrid (no longer OML4Py-specific)
- ⚠️ Need to be careful not to break existing logic

## Option 2: Create New Script

**What to create:**
- New file: `scripts/score_churn_model_local.py`
- Start from scratch with:
  - `get_connection()` (from train_churn_model_local.py)
  - `load_model_from_pickle()` (new)
  - `load_user_features_from_db()` (new, SQL query)
  - `score_users_local()` (new, local model)
  - **Copy `store_predictions()` from current script** (reuse the good part)

**Pros:**
- ✅ Clean separation: OML4Py script vs Local script
- ✅ Original script remains for OML4Py users
- ✅ Clear naming: `_local` suffix

**Cons:**
- ⚠️ Code duplication (need to copy `store_predictions()`)
- ⚠️ Two scripts to maintain
- ⚠️ More files in project

## Recommendation: **Update Current Script**

**Why:**
1. The `store_predictions()` function is **already perfect** and tested
2. It's the most complex part (handles SQL, error handling, verification)
3. No need to duplicate it
4. The script is already designed to be modular (separate functions)

**What "keep database storage logic" means:**
- The `store_predictions()` function (lines 158-242) handles:
  - Truncating the `OML.CHURN_PREDICTIONS` table
  - Inserting predictions with proper data types
  - Verifying row counts
  - Generating summary statistics (at-risk count, avg risk)
  - Error handling and rollback
  - This is **already working** and doesn't need changes

**What needs to change:**
- Only the **model loading** and **scoring** parts (lines 41-156)
- Replace OML4Py calls with local model + oracledb calls
- Keep everything else the same

## Summary

| Aspect | Update Current | Create New |
|--------|---------------|------------|
| **Database Storage** | ✅ Keep existing | ⚠️ Copy/duplicate |
| **Code Reuse** | ✅ High | ❌ Low |
| **Maintenance** | ✅ Single file | ⚠️ Two files |
| **Clarity** | ⚠️ Hybrid script | ✅ Clear separation |
| **Risk** | ⚠️ Need to be careful | ✅ Clean slate |

**My recommendation**: Update the current script because the database storage logic is already perfect and tested. We just need to swap out the OML4Py parts for local model parts.
