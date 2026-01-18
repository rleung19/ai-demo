# Why 5,003 ADMIN.USERS but Only 4,142 USER_PROFILES?

## The Numbers

- **ADMIN.USERS**: 5,003 total users (original demo data)
- **OML.USER_PROFILES**: 4,142 users (mapped from dataset)
- **Difference**: 861 users (5,003 - 4,142 = 861)

## Why This Happened

### The Hybrid Mapping Strategy

We used a **hybrid mapping strategy** that splits the dataset:

1. **4,142 rows** → Mapped to real `ADMIN.USERS` IDs
   - Used stratified sampling to maintain churn rate
   - These become `OML.USER_PROFILES`
   - Used for API responses and real user predictions

2. **45,858 rows** → Training data (no user mapping)
   - Remaining rows from the 50,000 row dataset
   - Used for model training
   - Better model performance with more data

### Why Only 4,142 Users?

The number 4,142 came from:
- **Stratified sampling** to maintain the exact churn rate (28.90%)
- We sampled 4,142 rows from the 50,000 row dataset
- This was enough to:
  - Map to a good subset of real users
  - Maintain statistical properties
  - Provide sufficient data for API/demo

### Could We Map All 5,003 Users?

**Yes, we could**, but we chose not to because:
1. We wanted to use the remaining 45,858 rows for training (better model)
2. 4,142 users is sufficient for demo/API purposes
3. The remaining 861 users don't have profile data, so they can't be scored

## Impact

### What This Means

- **861 ADMIN.USERS** have no corresponding `USER_PROFILES`
- These users **cannot be scored** by the model (no features)
- They **won't appear** in API responses
- They **won't be included** in cohort calculations

### For API Endpoints

The API will only return data for the **4,142 users** that have:
- `OML.USER_PROFILES` (input features)
- `OML.CHURN_PREDICTIONS` (model predictions)

### For Affinity Card Analysis

- **962 users** have `AFFINITY_CARD = 1` in `ADMIN.USERS`
- Only **some subset** of these are in `OML.USER_PROFILES`
- The API can only analyze affinity card users that are in `USER_PROFILES`

## Options

### Option 1: Keep Current (4,142 users)
- ✅ More training data (45,858 rows)
- ✅ Better model performance
- ❌ 861 users excluded from analysis

### Option 2: Map All 5,003 Users
- ✅ All users can be scored
- ✅ Complete coverage
- ❌ Less training data (would need to reduce training set)
- ❌ Would need to remap dataset

### Option 3: Map More Users (e.g., 5,000)
- ✅ More users for API
- ✅ Still have ~45,000 rows for training
- ⚠️ Would need to regenerate mapped dataset

## Recommendation

**Keep current (4,142 users)** because:
1. Model performance is excellent (AUC 0.9269)
2. 4,142 users is sufficient for demo
3. More training data = better model
4. The 861 excluded users don't have profile data anyway

If you need to include more users later, we can:
- Remap the dataset to include more users
- Or create additional user profiles from other sources

## Related Documentation

- `docs/HYBRID_MAPPING_STRATEGY.md` - Explains the hybrid approach
- `docs/DATA_MAPPING_DOCUMENT.md` - Data mapping details
- `scripts/create_hybrid_datasets.py` - Script that created the split
