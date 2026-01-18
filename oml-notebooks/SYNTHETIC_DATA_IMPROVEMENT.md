# Improving Synthetic Data for Churn Prediction

## Why Synthetic Data Quality Matters

**Current Issue**: AUC ~50% suggests the model can't find meaningful patterns. This could be because:
1. **Synthetic data lacks realistic correlations** between features
2. **Churn patterns don't match real-world behavior**
3. **Feature distributions are unrealistic** (e.g., too uniform, no outliers)
4. **Temporal patterns are missing** (e.g., seasonal trends, customer lifecycle)

## Key Areas to Improve in Synthetic Data

### 1. **Realistic Feature Correlations** ⚠️ CRITICAL

**Problem**: In real data, features are correlated. For example:
- High-spending customers login more frequently
- Customers with many returns have lower satisfaction
- Email engagement correlates with purchase frequency

**What to Fix**:
```python
# Example: Ensure correlations exist
# High spenders should have:
- More logins (positive correlation ~0.6)
- Higher email engagement (positive correlation ~0.5)
- Fewer returns (negative correlation ~-0.3)

# Customers with many returns should have:
- Lower review ratings (negative correlation ~-0.7)
- More cart abandonments (positive correlation ~0.5)
```

### 2. **Realistic Churn Patterns** ⚠️ CRITICAL

**Problem**: Current churn definition might not match synthetic data patterns.

**What to Fix**:
- **Churners should have clear patterns**:
  - Decreasing purchase frequency over time
  - Declining login activity
  - Increasing cart abandonments
  - Decreasing email engagement
  
- **Non-churners should have stable/improving patterns**:
  - Consistent or increasing purchases
  - Regular logins
  - Low cart abandonment
  - High email engagement

**Example Pattern**:
```python
# Churners (should be ~15% of data):
- MONTHS_SINCE_LAST_PURCHASE: Increasing trend (0.5 → 1.5 → 3.0)
- LOGIN_COUNT_30D: Decreasing (15 → 7 → 2)
- EMAIL_OPEN_RATE: Decreasing (0.8 → 0.4 → 0.1)
- CART_ABANDONMENTS: Increasing (0 → 2 → 5)

# Non-churners (should be ~85%):
- MONTHS_SINCE_LAST_PURCHASE: Stable (0.1 → 0.2 → 0.1)
- LOGIN_COUNT_30D: Stable or increasing (10 → 12 → 15)
- EMAIL_OPEN_RATE: Stable (0.6 → 0.65 → 0.7)
- CART_ABANDONMENTS: Low and stable (0 → 1 → 0)
```

### 3. **Realistic Distributions** 🔄 IMPORTANT

**Problem**: Synthetic data often has uniform or normal distributions, but real data is skewed.

**What to Fix**:
- **Purchase behavior**: Power-law distribution (few high-value customers, many low-value)
- **Login frequency**: Bimodal (active users login daily, inactive rarely)
- **Email engagement**: Beta distribution (most people have moderate engagement)
- **Cart abandonments**: Poisson distribution (most have 0-2, few have many)

**Example**:
```python
# Realistic distributions:
ORDER_COUNT_24M: 
  - 40% have 1-2 orders
  - 30% have 3-5 orders
  - 20% have 6-10 orders
  - 10% have 11+ orders

LOGIN_COUNT_30D:
  - 20% have 0-2 logins (inactive)
  - 30% have 3-7 logins (occasional)
  - 30% have 8-15 logins (regular)
  - 20% have 16+ logins (very active)
```

### 4. **Temporal Patterns** 🔄 IMPORTANT

**Problem**: Real customer behavior changes over time, but synthetic data might be static.

**What to Fix**:
- **Customer lifecycle**: New → Growing → Mature → At-Risk → Churned
- **Seasonal patterns**: Holiday shopping spikes, summer lulls
- **Engagement decay**: Natural decline after initial excitement
- **Recovery patterns**: Some churners return after intervention

**Example Timeline**:
```
Month 0-3: New customer (high engagement, first purchases)
Month 4-12: Growing (increasing purchases, stable engagement)
Month 13-24: Mature (stable patterns)
Month 25+: At-risk (declining engagement, fewer purchases)
```

### 5. **Segment-Specific Patterns** 🔄 IMPORTANT

**Problem**: Different customer segments behave differently.

**What to Fix**:
- **VIP customers**: 
  - Higher purchase frequency
  - More logins
  - Lower churn rate (~5% vs 15%)
  - Higher email engagement
  
- **New customers**:
  - High initial engagement
  - First purchase within 30 days
  - Higher churn risk if no second purchase
  
- **Dormant customers**:
  - No purchases in 2+ months
  - Very low logins
  - High churn probability

### 6. **Missing Data Patterns** 🔄 IMPORTANT

**Problem**: Real data has missing values that follow patterns.

**What to Fix**:
- **Inactive customers**: More missing login/email data
- **New customers**: Missing historical features (24-month windows)
- **Missing data should correlate with churn risk**

### 7. **Outliers and Edge Cases** 🔄 LOW PRIORITY

**Problem**: Real data has outliers that are meaningful.

**What to Fix**:
- **Whales**: 1-2% of customers with very high spending
- **Power users**: Customers who login 50+ times per month
- **Problem customers**: High returns, low satisfaction, but still active

## Validation Queries to Check Data Realism

### Check Feature Correlations
```sql
-- Should see positive correlations:
SELECT 
    CORR(TOTAL_SPENT_24M, LOGIN_COUNT_30D) as spend_login_corr,
    CORR(TOTAL_SPENT_24M, EMAIL_OPEN_RATE_30D) as spend_email_corr,
    CORR(ORDER_COUNT_24M, LOGIN_COUNT_30D) as orders_login_corr
FROM OML.CHURN_FEATURES;

-- Should see negative correlations:
SELECT 
    CORR(TOTAL_RETURNS_COUNT, AVG_REVIEW_RATING) as returns_rating_corr,
    CORR(CART_ABANDONMENTS_30D, EMAIL_OPEN_RATE_30D) as abandon_email_corr
FROM OML.CHURN_FEATURES;
```

### Check Churn Patterns
```sql
-- Churners should have different patterns than non-churners
SELECT 
    CHURNED_60_90D,
    AVG(MONTHS_SINCE_LAST_PURCHASE) as avg_months,
    AVG(LOGIN_COUNT_30D) as avg_logins,
    AVG(EMAIL_OPEN_RATE_30D) as avg_email,
    AVG(CART_ABANDONMENTS_30D) as avg_abandons,
    AVG(TOTAL_SPENT_24M) as avg_spent
FROM OML.CHURN_TRAINING_DATA
GROUP BY CHURNED_60_90D;
-- Expected: Churners should have higher months, lower logins, lower email, higher abandons
```

### Check Distributions
```sql
-- Check if distributions are realistic (not uniform)
SELECT 
    CASE 
        WHEN ORDER_COUNT_24M = 0 THEN '0'
        WHEN ORDER_COUNT_24M BETWEEN 1 AND 2 THEN '1-2'
        WHEN ORDER_COUNT_24M BETWEEN 3 AND 5 THEN '3-5'
        WHEN ORDER_COUNT_24M BETWEEN 6 AND 10 THEN '6-10'
        ELSE '11+'
    END as order_bucket,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM OML.CHURN_FEATURES), 2) as percentage
FROM OML.CHURN_FEATURES
GROUP BY 
    CASE 
        WHEN ORDER_COUNT_24M = 0 THEN '0'
        WHEN ORDER_COUNT_24M BETWEEN 1 AND 2 THEN '1-2'
        WHEN ORDER_COUNT_24M BETWEEN 3 AND 5 THEN '3-5'
        WHEN ORDER_COUNT_24M BETWEEN 6 AND 10 THEN '6-10'
        ELSE '11+'
    END
ORDER BY order_bucket;
```

## Recommended Regeneration Strategy

### Phase 1: Identify Current Issues (Do First)
1. Run validation queries above
2. Check if correlations exist
3. Check if churners have different patterns
4. Check if distributions are realistic

### Phase 2: Regenerate with Realistic Patterns
1. **Start with churners**: Generate clear churn patterns first
2. **Add correlations**: Ensure features are correlated realistically
3. **Add temporal patterns**: Include customer lifecycle
4. **Add segment differences**: VIP vs Regular vs New

### Phase 3: Validate and Iterate
1. Run validation queries again
2. Check if patterns match expectations
3. Train model and check if AUC improves
4. Iterate if needed

## Expected Improvements

If you regenerate data with realistic patterns:
- **AUC should improve to 0.60-0.75** (from current 0.50)
- **Feature importance should make sense** (e.g., MONTHS_SINCE_LAST_PURCHASE should be top)
- **Model predictions should align with business logic**

## Red Flags in Current Data

If you see these, regenerate:
- ✅ Correlations near 0 (features are independent)
- ✅ Churners and non-churners have similar feature values
- ✅ Uniform distributions (everything is equally likely)
- ✅ No temporal patterns (all customers look the same over time)
- ✅ Segment differences are minimal

## Quick Check: Is Your Data Realistic?

Run this query to see if churners are different:
```sql
SELECT 
    CHURNED_60_90D,
    COUNT(*) as count,
    ROUND(AVG(MONTHS_SINCE_LAST_PURCHASE), 2) as avg_months,
    ROUND(AVG(LOGIN_COUNT_30D), 2) as avg_logins,
    ROUND(AVG(EMAIL_OPEN_RATE_30D), 2) as avg_email_rate,
    ROUND(AVG(CART_ABANDONMENTS_30D), 2) as avg_abandons
FROM OML.CHURN_TRAINING_DATA
GROUP BY CHURNED_60_90D;
```

**Expected Result**:
- Churners (1): Higher months, lower logins, lower email rate, higher abandons
- Non-churners (0): Lower months, higher logins, higher email rate, lower abandons

**If they're similar**: Your synthetic data needs regeneration!
