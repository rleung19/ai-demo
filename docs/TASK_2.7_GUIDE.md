# Task 2.7: Create Feature Engineering Views

## Status

✅ **Completed**: Feature engineering views created successfully

## What Was Created

### SQL Views Script
- **File**: `sql/create_feature_views.sql`
- **Purpose**: Creates feature engineering views for model training and scoring

### Python Script
- **File**: `scripts/create_feature_views.py`
- **Purpose**: Executes SQL script and verifies views

## Views Created

### 1. `OML.CHURN_TRAINING_FEATURES`
- **Purpose**: Feature columns only (for model training)
- **Source**: `OML.CHURN_DATASET_TRAINING`
- **Rows**: 45,858
- **Excludes**: 
  - `USER_ID` (identifier)
  - `CHURNED` (target label)
  - `COUNTRY`, `CITY` (categorical, would need encoding)
- **Features**: 22 numeric features
  - Demographics: AGE, GENDER_CODE, SIGNUP_QUARTER_CODE
  - Membership: MEMBERSHIP_YEARS
  - Engagement: LOGIN_FREQUENCY, SESSION_DURATION_AVG, PAGES_PER_SESSION, EMAIL_OPEN_RATE, SOCIAL_MEDIA_ENGAGEMENT_SCORE, MOBILE_APP_USAGE
  - Purchase: TOTAL_PURCHASES, AVERAGE_ORDER_VALUE, DAYS_SINCE_LAST_PURCHASE, LIFETIME_VALUE
  - Cart: CART_ABANDONMENT_RATE, WISHLIST_ITEMS
  - Service: CUSTOMER_SERVICE_CALLS, RETURNS_RATE, PRODUCT_REVIEWS_WRITTEN
  - Financial: DISCOUNT_USAGE_RATE, PAYMENT_METHOD_DIVERSITY, CREDIT_BALANCE

### 2. `OML.CHURN_TRAINING_DATA`
- **Purpose**: Features + target label for training
- **Source**: `OML.CHURN_DATASET_TRAINING`
- **Rows**: 45,858
- **Includes**: 
  - All features from `CHURN_TRAINING_FEATURES`
  - `USER_ID` (for tracking)
  - `CHURNED` (target label: 0 = retained, 1 = churned)

### 3. `OML.CHURN_USER_FEATURES`
- **Purpose**: Features for scoring actual users
- **Source**: `OML.USER_PROFILES`
- **Rows**: 4,142
- **Includes**: 
  - All features (same as training)
  - `USER_ID` (for joining with predictions)
- **Excludes**: 
  - `CHURNED` (historical label, not used for prediction)

## Feature Engineering

### Categorical Encoding
- **GENDER**: Encoded as numeric (Male=1, Female=2, Other=0)
- **SIGNUP_QUARTER**: Encoded as numeric (Q1=1, Q2=2, Q3=3, Q4=4)

### Feature Selection
- All numeric features included
- Categorical features (COUNTRY, CITY) excluded (would need one-hot encoding)
- Target label (CHURNED) excluded from feature views

## Usage

### For Model Training
```python
# Load training data with features and target
import oml
train_data = oml.sync(view='CHURN_TRAINING_DATA')
train_df = train_data.pull()

# Separate features and target
feature_cols = [col for col in train_df.columns 
                if col not in ['USER_ID', 'CHURNED']]
X = train_df[feature_cols]
y = train_df['CHURNED']
```

### For Model Scoring
```python
# Load user features for scoring
user_features = oml.sync(view='CHURN_USER_FEATURES')
user_df = user_features.pull()

# Get features only (exclude USER_ID for model input)
feature_cols = [col for col in user_df.columns if col != 'USER_ID']
X_users = user_df[feature_cols]
```

## Verification

All views verified:
- ✓ CHURN_TRAINING_FEATURES: 45,858 rows
- ✓ CHURN_TRAINING_DATA: 45,858 rows
- ✓ CHURN_USER_FEATURES: 4,142 rows

## Next Steps

1. ✅ **Task 2.7 Complete**: Feature engineering views created
2. ⏳ **Task 2.8**: Validate dataset produces reasonable model performance (AUC > 0.70)
3. ⏳ **Task 3.x**: Train model using these views

## Related Documentation

- `docs/DATA_MAPPING_DOCUMENT.md` - Column mappings
- `sql/create_churn_tables.sql` - Base table schema
- `oml-notebooks/QUICK_REFERENCE.md` - OML4Py usage patterns
