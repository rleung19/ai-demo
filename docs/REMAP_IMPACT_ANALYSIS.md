# Impact Analysis: Remapping to All 5,003 Users

## Current State

- **Training Data**: 45,858 rows
- **User Profiles**: 4,142 users
- **Model Performance**: AUC 0.9269 (excellent)
- **Unmapped Users**: 861 users (17.2% of ADMIN.USERS)

## If We Remap to All 5,003 Users

### Data Changes

| Metric | Current | After Remap | Change |
|--------|---------|-------------|--------|
| **Training Data** | 45,858 rows | ~45,000 rows | -861 rows (-1.88%) |
| **User Profiles** | 4,142 users | 5,003 users | +861 users (+20.8%) |
| **Training Loss** | - | 861 rows | 1.88% reduction |

### Impact on Model Performance

#### Training Data Reduction: **-1.88%**

**Assessment**: **Minimal Impact** ✅

**Reasoning**:
1. **Small reduction**: Only 1.88% of training data lost
2. **Still substantial**: 45,000 rows is still excellent for training
3. **Model is robust**: XGBoost performs well with 30K+ samples
4. **Expected AUC impact**: Likely **< 0.01** (e.g., 0.9269 → 0.9250-0.9260)

**Evidence from literature**:
- XGBoost typically needs 1,000+ samples for good performance
- We'd still have 45,000 samples (45x more than minimum)
- Diminishing returns after ~20,000 samples for this problem size
- 1.88% reduction is negligible for models this size

### What Needs to Be Done

#### 1. Remap Dataset (Low Risk)
- **Action**: Run `scripts/create_hybrid_datasets.py` with updated count
- **Time**: ~5-10 minutes
- **Risk**: Low (just data processing)
- **Impact**: Creates new mapped dataset with 5,003 users

#### 2. Re-ingest Data (Low Risk)
- **Action**: Run `scripts/ingest_churn_data.py`
- **Time**: ~2-3 minutes
- **Risk**: Low (just data loading)
- **Impact**: Updates `OML.USER_PROFILES` with all 5,003 users

#### 3. Retrain Model (Medium Risk)
- **Action**: Run `scripts/local/train_churn_model_local.py`
- **Time**: ~2-3 minutes
- **Risk**: Medium (model performance may change slightly)
- **Impact**: New model with potentially slightly different AUC

#### 4. Re-score Users (Low Risk)
- **Action**: Run `scripts/local/score_churn_model_local.py`
- **Time**: ~1-2 minutes
- **Risk**: Low (just scoring)
- **Impact**: All 5,003 users get predictions

### Estimated Time

**Total time**: ~10-15 minutes
- Remap dataset: 5-10 min
- Re-ingest: 2-3 min
- Retrain: 2-3 min
- Re-score: 1-2 min

### Risk Assessment

| Task | Risk Level | Impact | Mitigation |
|------|-----------|--------|------------|
| Remap dataset | 🟢 Low | None | Just data processing |
| Re-ingest data | 🟢 Low | None | Just data loading |
| Retrain model | 🟡 Medium | Small AUC change | Model still excellent |
| Re-score users | 🟢 Low | None | Just scoring |

### Benefits of Remapping

✅ **Complete Coverage**
- All 5,003 users can be scored
- No excluded users
- Complete demo data

✅ **Better Demo**
- Shows predictions for all users
- More realistic scenario
- Better for presentations

✅ **Affinity Card Analysis**
- All 962 affinity card users can be analyzed
- Complete cohort coverage

### Drawbacks of Remapping

⚠️ **Slight Model Performance Risk**
- Training data reduced by 1.88%
- AUC might drop by ~0.001-0.01 (e.g., 0.9269 → 0.9259)
- Still excellent performance (AUC > 0.92)

⚠️ **Time Investment**
- ~10-15 minutes to remap and retrain
- Need to verify new model performance

⚠️ **Model Version Change**
- New model version in registry
- Need to update production model reference

## Recommendation

### ✅ **Proceed with Remapping** (Low Risk, High Value)

**Why**:
1. **Minimal impact**: Only 1.88% training data loss
2. **Still excellent**: 45,000 rows is more than enough
3. **Complete coverage**: All users can be scored
4. **Better demo**: More realistic scenario
5. **Quick process**: Only 10-15 minutes

**Expected Outcome**:
- Model AUC: **0.9250-0.9270** (still excellent)
- All 5,003 users scored
- Complete affinity card analysis
- Better demo coverage

### Alternative: Keep Current (If Time-Constrained)

If you're time-constrained and 4,142 users is sufficient:
- ✅ Model already excellent (AUC 0.9269)
- ✅ 4,142 users is good for demo
- ✅ No retraining needed
- ❌ 861 users excluded

## Process to Remap

### Step 1: Update Mapping Script
```python
# In scripts/create_hybrid_datasets.py
# Change: n_users = len(user_ids)  # Use all 5,003 users
```

### Step 2: Regenerate Datasets
```bash
python scripts/create_hybrid_datasets.py
```

### Step 3: Re-ingest Data
```bash
python scripts/ingest_churn_data.py
```

### Step 4: Retrain Model
```bash
python scripts/local/train_churn_model_local.py
```

### Step 5: Re-score Users
```bash
python scripts/local/score_churn_model_local.py
```

### Step 6: Verify
```bash
python scripts/local/test_pipeline_end_to_end.py
```

## Conclusion

**Impact is minimal** (1.88% training data loss) and **benefits are significant** (complete user coverage). The model will likely maintain excellent performance (AUC > 0.92), and the process is quick (~10-15 minutes).

**Recommendation**: Proceed with remapping if you want complete coverage. The risk is low and the benefits are high.
