# Data Mapping Document: Source Dataset → OML Schema

## Purpose

This document maps the source dataset (dhairyajeetsingh ecommerce customer behavior dataset) to the OML schema tables in Oracle ADB.

## Source Dataset

**Dataset**: Ecommerce Customer Behavior Dataset (dhairyajeetsingh)  
**File**: `data/processed/churn_dataset_cleaned.csv`  
**Rows**: 50,000  
**Columns**: 25 features + Churned label

## Target: OML Schema Tables

### Table 1: `OML.CHURN_DATASET_TRAINING`

**Purpose**: Store training data (45,858 rows) for model training

**Columns**:

| Source Column | Target Column | Data Type | Notes |
|---------------|---------------|-----------|-------|
| USER_ID (placeholder) | USER_ID | VARCHAR2(36) | Placeholder ID (TRAIN_1, TRAIN_2, etc.) |
| Age | AGE | NUMBER(5,2) | Customer age |
| Gender | GENDER | VARCHAR2(20) | Male/Female/Other |
| Country | COUNTRY | VARCHAR2(50) | Country name |
| City | CITY | VARCHAR2(50) | City name |
| Membership_Years | MEMBERSHIP_YEARS | NUMBER(5,2) | Years as member |
| Login_Frequency | LOGIN_FREQUENCY | NUMBER(5,2) | Logins per period |
| Session_Duration_Avg | SESSION_DURATION_AVG | NUMBER(5,2) | Average session duration |
| Pages_Per_Session | PAGES_PER_SESSION | NUMBER(5,2) | Pages viewed per session |
| Cart_Abandonment_Rate | CART_ABANDONMENT_RATE | NUMBER(5,2) | Cart abandonment percentage |
| Wishlist_Items | WISHLIST_ITEMS | NUMBER(5,2) | Items in wishlist |
| Total_Purchases | TOTAL_PURCHASES | NUMBER(10) | Total purchase count |
| Average_Order_Value | AVERAGE_ORDER_VALUE | NUMBER(10,2) | Average order value |
| Days_Since_Last_Purchase | DAYS_SINCE_LAST_PURCHASE | NUMBER(5) | Days since last purchase |
| Discount_Usage_Rate | DISCOUNT_USAGE_RATE | NUMBER(5,2) | Discount usage percentage |
| Returns_Rate | RETURNS_RATE | NUMBER(5,2) | Return rate percentage |
| Email_Open_Rate | EMAIL_OPEN_RATE | NUMBER(5,2) | Email open rate percentage |
| Customer_Service_Calls | CUSTOMER_SERVICE_CALLS | NUMBER(5) | Support calls count |
| Product_Reviews_Written | PRODUCT_REVIEWS_WRITTEN | NUMBER(5) | Reviews written count |
| Social_Media_Engagement_Score | SOCIAL_MEDIA_ENGAGEMENT_SCORE | NUMBER(5,2) | Social engagement score |
| Mobile_App_Usage | MOBILE_APP_USAGE | NUMBER(5,2) | Mobile app usage percentage |
| Payment_Method_Diversity | PAYMENT_METHOD_DIVERSITY | NUMBER(2) | Number of payment methods |
| Lifetime_Value | LIFETIME_VALUE | NUMBER(10,2) | Customer lifetime value |
| Credit_Balance | CREDIT_BALANCE | NUMBER(10,2) | Credit balance |
| Signup_Quarter | SIGNUP_QUARTER | VARCHAR2(10) | Q1, Q2, Q3, Q4 |
| Churned | CHURNED | NUMBER(1) | 0 = retained, 1 = churned |

---

### Table 2: `OML.USER_PROFILES`

**Purpose**: Store **input features** (4,142 rows) for churn prediction on actual users

**Columns**: Same as above, but:
- `USER_ID` contains real UUIDs from `ADMIN.USERS.ID`
- **Contains features only** (input to the model)
- **NOT** where predictions are stored (see `CHURN_PREDICTIONS` table)
- Used for:
  - **Model scoring** (provides features to the model)
  - **Input to prediction pipeline**

**Note**: The `CHURNED` column in this table is the **historical label** (for reference), not the prediction.

---

### Table 3: `OML.CHURN_PREDICTIONS`

**Purpose**: Store **predicted churn scores** produced by the ML model

**Columns**:

| Column | Data Type | Description |
|--------|-----------|-------------|
| USER_ID | VARCHAR2(36) | Foreign key to ADMIN.USERS.ID |
| PREDICTED_CHURN_PROBABILITY | NUMBER(5,4) | Churn probability (0.0 to 1.0) |
| PREDICTED_CHURN_LABEL | NUMBER(1) | Binary prediction (0 = retained, 1 = churned) |
| RISK_SCORE | NUMBER(3) | Risk score (0-100) for display |
| MODEL_VERSION | VARCHAR2(50) | Version of model used |
| PREDICTION_DATE | TIMESTAMP | When prediction was made |
| LAST_UPDATED | TIMESTAMP | Last update timestamp |

**Used for**:
- **API responses** (returns predictions for users)
- **Dashboard display** (KPI #1 data)
- **Model output storage** (predictions from scoring)

---

## Data Type Mappings

| Source Type | Oracle Type | Notes |
|-------------|-------------|-------|
| float64 | NUMBER(10,2) | Numeric with decimals |
| int64 | NUMBER(10) | Integer values |
| object (string) | VARCHAR2(n) | Text values (adjust size as needed) |

---

## Column Name Transformations

**Pattern**: Convert to UPPER_CASE with underscores

- `Age` → `AGE`
- `Membership_Years` → `MEMBERSHIP_YEARS`
- `Cart_Abandonment_Rate` → `CART_ABANDONMENT_RATE`
- etc.

---

## Data Quality Considerations

### Missing Values
- All missing values have been imputed (median for numeric, mode for categorical)
- No NULL values expected in loaded data

### Data Anomalies Fixed
- Negative `Total_Purchases` → Set to 0
- Age outliers (>100) → Capped at 100
- Extreme `Average_Order_Value` → Capped at 99th percentile

---

## Mapping Strategy

### Training Dataset
- **Source**: `data/processed/churn_dataset_training.csv`
- **Rows**: 45,858
- **USER_ID**: Placeholder (TRAIN_1, TRAIN_2, etc.)
- **Purpose**: Model training

### User Profiles Dataset (Input Features)
- **Source**: `data/processed/churn_dataset_mapped.csv`
- **Target Table**: `OML.USER_PROFILES`
- **Rows**: 4,142
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Purpose**: 
  - **Input features** for model scoring
  - Provides features to the model for prediction
  - **NOT** where predictions are stored

### Predictions Table (Model Output)
- **Target Table**: `OML.CHURN_PREDICTIONS`
- **Rows**: One per user (matches USER_PROFILES)
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **Purpose**: 
  - **Store predicted churn scores** from the model
  - API responses (returns predictions)
  - Dashboard display (KPI #1 data)
  - Updated when model scores users

---

## SQL Table Creation

✅ **Schema Created**: See `sql/create_churn_tables.sql` for table creation scripts.

**Tables created**:
1. `OML.CHURN_DATASET_TRAINING` - Training data (45,858 rows)
2. `OML.USER_PROFILES` - Input features for actual users (4,142 rows)
3. `OML.CHURN_PREDICTIONS` - Model predictions/output (4,142 rows)

**To create tables**: Run `sql/create_churn_tables.sql` as OML user in ADB.

---

## Data Flow Summary

```
Training:
  CHURN_DATASET_TRAINING → Train Model → Save Model

Prediction:
  USER_PROFILES (features) → Model → CHURN_PREDICTIONS (predictions) → API
```

**Key Points**:
- `USER_PROFILES` = **Input** (features for model)
- `CHURN_PREDICTIONS` = **Output** (predictions from model)
- API reads from `CHURN_PREDICTIONS`, not `USER_PROFILES`

---

## Next Steps

1. ✅ Review this mapping document
2. ⏳ Create SQL table creation scripts (Task 1.3)
3. ⏳ Create data ingestion script (Task 2.5)
4. ⏳ Load data into OML schema
5. ⏳ Validate data loaded correctly (Task 2.6)
6. ⏳ Implement prediction storage (Task 3.8)
