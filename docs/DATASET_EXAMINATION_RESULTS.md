# Dataset Examination Results: dhairyajeetsingh

## ✅ Dataset Quality: EXCELLENT

### Basic Information
- **Size**: 50,000 rows × 25 columns ✅ (Perfect match!)
- **File Size**: 19.79 MB
- **Memory Usage**: Reasonable

### Churn Label: ✅ FOUND

- **Column Name**: `Churned`
- **Type**: Binary (0 = retained, 1 = churned)
- **Churn Rate**: 28.9% (14,450 churned, 35,550 retained)
- **Balance**: Good (not too imbalanced)

### Data Quality: ✅ GOOD

- **Missing Values**: 3.93% (49,081 out of 1,250,000 cells)
- **Overall Quality**: Good (low missing value rate)

**Columns with Missing Values** (need attention):
- `Social_Media_Engagement_Score`: 12.0% missing (6,000)
- `Credit_Balance`: 11.0% missing (5,500)
- `Mobile_App_Usage`: 10.0% missing (5,000)
- `Returns_Rate`: 9.0% missing (4,491)
- `Wishlist_Items`: 8.0% missing (4,000)
- `Discount_Usage_Rate`: 7.0% missing (3,500)
- `Product_Reviews_Written`: 7.0% missing (3,500)
- `Session_Duration_Avg`: 6.8% missing (3,399)
- `Pages_Per_Session`: 6.0% missing (3,000)
- `Days_Since_Last_Purchase`: 6.0% missing (3,000)
- `Email_Open_Rate`: 5.1% missing (2,528)
- `Age`: 5.0% missing (2,495)
- `Payment_Method_Diversity`: 5.0% missing (2,500)
- `Customer_Service_Calls`: 0.3% missing (168)

### Features: ✅ RICH

**Numeric Features (21)**:
- Age, Membership_Years, Login_Frequency
- Session_Duration_Avg, Pages_Per_Session
- Cart_Abandonment_Rate, Wishlist_Items
- Total_Purchases, Average_Order_Value
- Days_Since_Last_Purchase, Discount_Usage_Rate
- Returns_Rate, Email_Open_Rate
- Customer_Service_Calls, Product_Reviews_Written
- Social_Media_Engagement_Score, Mobile_App_Usage
- Payment_Method_Diversity, Lifetime_Value
- Credit_Balance, Churned

**Categorical Features (4)**:
- Gender (3 unique values)
- Country (8 unique values)
- City (40 unique values)
- Signup_Quarter (4 unique values: Q1-Q4)

### Ecommerce Relevance: ✅ EXCELLENT

Found 6+ ecommerce-relevant features:
- Login_Frequency
- Total_Purchases
- Average_Order_Value
- Days_Since_Last_Purchase
- Payment_Method_Diversity
- Cart_Abandonment_Rate
- Email_Open_Rate
- Returns_Rate
- And more!

---

## ⚠️ Issues to Address

### 1. Missing Values (3.93% overall)

**Strategy**: 
- For columns with <10% missing: Use median/mean imputation
- For columns with >10% missing: Consider dropping or advanced imputation
- Or create "missing" indicator features

### 2. Data Anomalies

- `Total_Purchases` has negative values (min: -13.0) - **Data quality issue!**
- `Age` max is 200 - likely outlier
- Some columns have very high max values (e.g., `Average_Order_Value` max: 9666.38)

**Strategy**:
- Handle negative purchases (set to 0 or remove)
- Cap outliers (e.g., Age > 100, very high order values)
- Validate data ranges

### 3. Feature Engineering Opportunities

Since we have rich features, we can create:
- RFM features (Recency, Frequency, Monetary)
- Engagement score (combine email, social, app usage)
- Customer lifetime stage (based on membership years)
- Risk indicators (high returns + low purchases)

---

## ✅ Decision: Use This Dataset

**Reasons**:
1. ✅ Perfect size (50k rows, 25 columns)
2. ✅ Churn label exists and is well-balanced
3. ✅ Good data quality (low missing values)
4. ✅ Rich ecommerce features
5. ✅ Proven performance (91% accuracy from notebooks)

**Next Steps**:
1. Handle missing values (imputation strategy)
2. Fix data anomalies (negative purchases, outliers)
3. Map to your USER_ID structure
4. Load into OML schema
5. Create feature engineering views

---

## Data Cleaning Plan

### Step 1: Handle Missing Values
```python
# Columns with <10% missing: median/mean imputation
# Columns with >10% missing: consider dropping or advanced imputation
```

### Step 2: Fix Anomalies
```python
# Fix negative Total_Purchases
# Cap Age outliers (e.g., > 100)
# Cap extreme order values
```

### Step 3: Feature Engineering
```python
# Create RFM features
# Create engagement scores
# Create risk indicators
```

---

## Mapping to USER_ID

**Strategy**: Sequential or random mapping to `ADMIN.USERS.ID`

```sql
-- Map dataset rows to existing users
-- Option 1: Sequential (if same count)
-- Option 2: Random sampling (if dataset is larger)
-- Option 3: Feature-based matching (if demographics match)
```

---

## Summary

✅ **Dataset is EXCELLENT for your use case!**

- Size: Perfect (50k rows)
- Churn label: Exists and balanced
- Features: Rich ecommerce features
- Quality: Good (low missing values)
- Performance: Proven (91% accuracy)

**Minor cleaning needed**:
- Handle missing values (3.93%)
- Fix data anomalies (negative purchases, outliers)
- Feature engineering opportunities

**Ready to proceed to Section 2.2-2.3** (evaluate and prepare dataset)!
