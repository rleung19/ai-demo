# Hybrid Mapping Strategy: Best of Both Worlds

## The Idea

**Split the dataset into two parts**:

1. **User Profiles Dataset (4,142 rows)**: 
   - Table: `OML.USER_PROFILES`
   - Stratified sample mapped to real ADMIN.USERS
   - Used for churn prediction on actual users
   - Used for API responses (real user predictions)
   - Used for model scoring

2. **Training Dataset (~45,858 rows)**:
   - Remaining rows WITHOUT user mapping
   - Used for model training and testing
   - More data = better model performance

## Why This is Better

### Advantages

1. ✅ **More training data**: 45,858 rows vs 4,142 rows
   - Better model performance
   - More robust training
   - Better generalization

2. ✅ **Real users for API**: 4,142 rows mapped to real users
   - API can return predictions for actual users
   - Demo shows real user data
   - Business value

3. ✅ **No wasted data**: Uses all 50,000 rows
   - Maximum data utilization
   - Better model training

4. ✅ **Clear separation**:
   - Training data: No user mapping needed
   - API data: Mapped to real users

### How It Works

```
50,000 rows total
├── 4,142 rows → Mapped to ADMIN.USERS (stratified)
│   └── Used for: API responses, demo, real user predictions
│
└── 45,858 rows → No user mapping
    └── Used for: Model training, testing, validation
```

## Implementation

### Step 1: Create User Profiles Dataset

- Stratified sample of 4,142 rows
- Map to real ADMIN.USERS.ID
- Maintains exact churn rate (28.90%)
- File: `data/processed/churn_dataset_mapped.csv`
- Target Table: `OML.USER_PROFILES`
- Purpose: Churn prediction for actual users

### Step 2: Create Training Dataset

- Remaining 45,858 rows
- No user mapping (or use placeholder IDs)
- Used for model training
- File: `data/processed/churn_dataset_training.csv`

## Usage

### For Model Training:
```python
# Use training dataset (45,858 rows)
df_train = pd.read_csv('data/processed/churn_dataset_training.csv')
# Train model on this
```

### For API/Demo:
```python
# Use mapped dataset (4,142 rows with real USER_IDs)
df_mapped = pd.read_csv('data/processed/churn_dataset_mapped.csv')
# Return predictions for real users
```

## Benefits Summary

| Aspect | Old Approach | New Approach |
|--------|--------------|--------------|
| **Training Data** | 4,142 rows | 45,858 rows ✅ |
| **API Data** | 4,142 rows | 4,142 rows ✅ |
| **Data Utilization** | 8.3% | 100% ✅ |
| **Model Performance** | Good | Better ✅ |
| **Real User Mapping** | Yes | Yes ✅ |

## Recommendation

✅ **Use this hybrid approach** - Best of both worlds!
