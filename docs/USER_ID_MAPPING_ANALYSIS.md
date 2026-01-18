# USER_ID Mapping Analysis

## ADMIN.USERS Table Structure

### Key Findings

- **Total Users**: 5,003
- **Active Users**: 4,142
- **ID Column**: `ID` (VARCHAR2(36)) - UUID format
- **ID Format**: UUID (e.g., '0003c291-4e31-4439-81ac-14d5fc498e79')
- **All IDs are unique**: ✅

### Dataset vs Users

- **Dataset rows**: 50,000
- **Available users**: 5,003
- **Ratio**: ~10:1 (10 dataset rows per user)

## Mapping Strategy Options

### Option 1: Sequential Mapping (Recommended)

Map first 5,003 dataset rows to users sequentially:

```sql
-- Map dataset rows 1-5,003 to users 1-5,003
-- Each user gets ~10 dataset rows (if we want multiple rows per user)
-- Or map 1:1 (first 5,003 rows to 5,003 users)
```

**Pros**:
- Simple and deterministic
- Easy to reproduce
- Each user gets data

**Cons**:
- Only uses first 5,003 rows (loses 45,000 rows)
- Or need to repeat users (same user gets multiple rows)

### Option 2: Random Sampling

Randomly sample 5,003 rows from 50,000 and map to users:

```sql
-- Randomly select 5,003 rows from dataset
-- Map to 5,003 users
```

**Pros**:
- Uses random sample (more representative)
- Each user gets unique data

**Cons**:
- Loses 45,000 rows
- Not deterministic (different each time)

### Option 3: Multiple Rows Per User (Recommended for Training)

Map multiple dataset rows to each user (for training data):

```sql
-- Map 10 rows per user (50,000 / 5,003 ≈ 10)
-- Each user gets multiple training examples
```

**Pros**:
- Uses all 50,000 rows
- More training data per user
- Better for model training

**Cons**:
- Same user appears multiple times
- Need to handle this in model training

### Option 4: Feature-Based Matching

Match dataset rows to users based on demographics:

```sql
-- Match on: Age, Gender, Country, City
-- More realistic mapping
```

**Pros**:
- More realistic (demographics match)
- Better for demo purposes

**Cons**:
- Complex to implement
- May not find matches for all users
- May not use all dataset rows

## Recommendation: Option 3 (Multiple Rows Per User)

**For model training**, use **Option 3**:
- Map ~10 dataset rows to each user
- Each user gets multiple training examples
- Uses all 50,000 rows
- Better for model training

**For demo/display**, use **Option 1**:
- Map 1:1 (first 5,003 rows to 5,003 users)
- Each user gets one row
- Simpler for API display

## Implementation

See `scripts/map_dataset_to_users.py` for implementation.
