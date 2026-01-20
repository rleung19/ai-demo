# Mapping Strategy Explained: Multiple vs Sequential

## The Problem

- **Dataset**: 50,000 rows (each row is a customer record with features + churn label)
- **Your Users**: 4,142 active users (each has a UUID)
- **Mismatch**: We have 50k dataset rows but only 4,142 users

## Strategy Comparison

### Strategy 1: Multiple Rows Per User (Current)

**What it does**:
- Maps ~12 dataset rows to each user
- Same USER_ID appears 12 times with different feature values
- Uses all 50,000 rows

**Example**:
```
USER_ID                                  | Churned | Total_Purchases | ...
-----------------------------------------|---------|-----------------|----
0003c291-4e31-4439-81ac-14d5fc498e79    | 0       | 9               | ...
0003c291-4e31-4439-81ac-14d5fc498e79    | 1       | 15              | ...
0003c291-4e31-4439-81ac-14d5fc498e79    | 0       | 12              | ...
... (9 more rows for same user)
```

**Problems**:
1. ❌ **Same user has different churn labels** - User appears as both churned (1) and not churned (0)
2. ❌ **Data leakage risk** - Same user in train/test split
3. ❌ **API confusion** - Which row represents the user's actual churn risk?
4. ❌ **Unrealistic** - One user can't have multiple churn states simultaneously

**When it's OK**:
- ✅ If each row represents a different time period (time-series data)
- ✅ If you're doing time-based churn prediction
- ❌ **NOT OK for static churn prediction** (one snapshot per user)

---

### Strategy 2: Sequential (1:1 Mapping) - RECOMMENDED

**What it does**:
- Maps first 4,142 dataset rows to 4,142 users (1:1)
- Each user appears exactly once
- Uses only 4,142 rows (discards 45,858 rows)

**Example**:
```
USER_ID                                  | Churned | Total_Purchases | ...
-----------------------------------------|---------|-----------------|----
0003c291-4e31-4439-81ac-14d5fc498e79    | 0       | 9               | ...
00185265-8280-4db0-86e5-8ba73ab9e54b    | 1       | 15              | ...
001c7a7a-efa4-4ea1-ab3e-adda66ed09d6    | 0       | 12              | ...
... (each user appears once)
```

**Advantages**:
- ✅ **One churn label per user** - Realistic
- ✅ **No data leakage** - Each user in train OR test, not both
- ✅ **Clear API response** - One churn risk per user
- ✅ **Matches real-world** - One user = one churn prediction

**Trade-offs**:
- ⚠️ Uses only 4,142 rows (smaller dataset)
- ⚠️ Still enough for good model (4k+ rows is sufficient)

---

## Which Strategy to Use?

### For Churn Prediction: **Sequential (1:1)** ✅

**Why**:
- Churn is a **binary state per user** (churned or not)
- Each user should have **one churn prediction**
- API needs to return **one risk score per user**
- Model training needs **one label per user**

### When Multiple Makes Sense:

- **Time-series churn**: If rows represent different time periods
- **Historical data**: If you're tracking churn over time
- **Not for static prediction**: If you want one prediction per user

---

## Recommended Solution

### Use Sequential (1:1) Mapping

**Reasons**:
1. ✅ **Realistic**: One user = one churn state
2. ✅ **No data leakage**: Clean train/test split
3. ✅ **Clear API**: One prediction per user
4. ✅ **4,142 rows is enough**: Good for model training

**Implementation**:
```python
# Map first 4,142 rows to 4,142 users (1:1)
python scripts/map_dataset_to_users.py \
    data/processed/churn_dataset_cleaned.csv \
    data/processed/churn_dataset_mapped.csv \
    sequential
```

---

## Potential Problems with Multiple Strategy

### 1. Model Training Issues

**Problem**: Same user in both train and test sets
```python
# Train set has user X with churn=0
# Test set has user X with churn=1
# Model "learns" user X, but sees conflicting labels
```

**Impact**: 
- Overfitting to specific users
- Inflated accuracy (model memorizes users, not patterns)
- Poor generalization

### 2. API Response Confusion

**Problem**: Which row represents the user's actual state?
```python
# API query: "What's churn risk for user X?"
# Database has 12 rows for user X with different values
# Which one to return?
```

**Impact**:
- Inconsistent API responses
- Unclear which prediction is "current"
- Business confusion

### 3. Data Leakage

**Problem**: Same user in train and test
```python
# Train: user X with features [A, B, C] → churn=0
# Test:  user X with features [D, E, F] → churn=1
# Model has "seen" user X before
```

**Impact**:
- Unrealistic performance metrics
- Model doesn't generalize to new users
- Production performance will be worse

---

## Recommendation

**Switch to Sequential (1:1) mapping**:

1. ✅ More realistic (one user = one churn state)
2. ✅ No data leakage
3. ✅ Clear API responses
4. ✅ 4,142 rows is sufficient for good model

**Action**:
```bash
# Re-map using sequential strategy
python scripts/map_dataset_to_users.py \
    data/processed/churn_dataset_cleaned.csv \
    data/processed/churn_dataset_mapped.csv \
    sequential
```

This will:
- Map first 4,142 rows to 4,142 users
- Each user appears exactly once
- Ready for model training and API

---

## Summary

| Aspect | Multiple Strategy | Sequential Strategy |
|--------|------------------|---------------------|
| **Rows used** | 50,000 | 4,142 |
| **Rows per user** | ~12 | 1 |
| **Data leakage** | ❌ Yes | ✅ No |
| **Realistic** | ❌ No | ✅ Yes |
| **API clarity** | ❌ Confusing | ✅ Clear |
| **Model training** | ⚠️ Problematic | ✅ Clean |
| **Recommendation** | ❌ Don't use | ✅ **Use this** |

**Conclusion**: Use **Sequential (1:1)** mapping for churn prediction.
