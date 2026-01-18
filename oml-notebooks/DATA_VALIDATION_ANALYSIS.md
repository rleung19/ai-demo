# Complete Data Validation Analysis

## Correlation Analysis

### Current Correlations (Too Weak)
```
SPEND_LOGIN_CORR:     0.159 (should be 0.4-0.6)
SPEND_EMAIL_CORR:     0.256 (should be 0.4-0.6)
ORDERS_LOGIN_CORR:    0.176 (should be 0.4-0.6)
RETURNS_RATING_CORR:  NULL  (should be -0.5 to -0.7)
ABANDON_EMAIL_CORR:   0.125 (should be -0.3 to -0.5, currently POSITIVE!)
```

### Issues Found
1. **All correlations are too weak** (< 0.3) - features are nearly independent
2. **RETURNS_RATING_CORR is NULL** - missing data or no variation
3. **ABANDON_EMAIL_CORR is positive** - should be NEGATIVE (more abandons = less email engagement)

## Churn Pattern Analysis

### Current Patterns
```
CHURNED_60_90D  AVG_MONTHS  AVG_LOGINS  AVG_EMAIL  AVG_ABANDONS  AVG_SPENT
--------------  ----------  ----------  ----------  ------------  ----------
             0        0.30        9.27       0.996          0.7      1183.50
             1        1.00        8.94       0.994          0.89     741.95
```

### Status by Feature

| Feature | Status | Current | Expected | Issue |
|---------|--------|---------|----------|-------|
| **Months** | ✅ IMPROVED | 1.00 vs 0.30 | 1.5-3.0 vs 0.1-0.5 | Still too close, but direction correct |
| **Logins** | ❌ BACKWARDS | 8.94 vs 9.27 | 2-5 vs 10-20 | Churners have MORE (should be less) |
| **Email** | ❌ NO SIGNAL | 0.994 vs 0.996 | 0.2-0.4 vs 0.6-0.8 | Nearly identical |
| **Abandons** | ⚠️ WEAK | 0.89 vs 0.7 | 3-8 vs 0-2 | Too similar |
| **Spent** | ✅ GOOD | 741 vs 1183 | Lower vs Higher | Direction correct! |

## Order Distribution Analysis

### Current Distribution
```
ORDE      COUNT PERCENTAGE
---- ---------- ----------
0            77       1.86%   (should be 10-20%)
1-2          13       0.31%   (should be 30-40%)
3-5         741      17.89%   (OK)
6-10       1093      26.39%   (OK)
11+        2218      53.55%  (TOO HIGH - should be 10-20%)
```

### Issues
- **Too many high-order customers** (53.55% have 11+ orders) - unrealistic
- **Too few low-order customers** (only 2.17% have 0-2 orders) - should be 30-40%
- **Distribution is inverted** - should be more customers with fewer orders

## Required Fixes in Data Generation

### Fix 1: Strengthen Correlations

```python
# Current correlations are too weak - need to enforce stronger relationships

# High spenders should have more logins (correlation ~0.5)
if total_spent > 1000:
    login_count = random(15, 25)  # High logins
elif total_spent > 500:
    login_count = random(10, 15)  # Medium logins
else:
    login_count = random(2, 10)   # Low logins

# High spenders should have better email engagement (correlation ~0.5)
if total_spent > 1000:
    email_rate = random(0.7, 0.9)  # High engagement
elif total_spent > 500:
    email_rate = random(0.5, 0.7)  # Medium engagement
else:
    email_rate = random(0.2, 0.5)  # Low engagement

# More returns should correlate with lower ratings (correlation ~-0.6)
if return_count > 2:
    avg_rating = random(2.0, 3.5)  # Lower ratings
elif return_count > 0:
    avg_rating = random(3.0, 4.0)  # Medium ratings
else:
    avg_rating = random(4.0, 5.0)  # Higher ratings

# More cart abandons should correlate with LOWER email engagement (correlation ~-0.4)
if cart_abandons > 3:
    email_rate = random(0.1, 0.3)  # LOW engagement
elif cart_abandons > 1:
    email_rate = random(0.3, 0.5)  # Medium engagement
else:
    email_rate = random(0.6, 0.8)  # HIGH engagement
```

### Fix 2: Fix Churn Patterns (CRITICAL)

```python
# CHURNERS (CHURNED_60_90D = 1)
if is_churner:
    months_since_purchase = random(1.5, 3.0)  # HIGH (currently 1.0 - too low)
    login_count = random(2, 5)               # LOW (currently 8.94 - too high!)
    email_rate = random(0.2, 0.4)             # LOW (currently 0.994 - way too high!)
    cart_abandons = random(3, 8)              # HIGH (currently 0.89 - too low)
    total_spent = random(300, 800)            # LOW (currently 741 - OK)

# NON-CHURNERS (CHURNED_60_90D = 0)
else:
    months_since_purchase = random(0.1, 0.5)  # LOW (currently 0.30 - OK)
    login_count = random(10, 20)              # HIGH (currently 9.27 - too low)
    email_rate = random(0.6, 0.8)             # HIGH (currently 0.996 - OK but too high)
    cart_abandons = random(0, 2)               # LOW (currently 0.7 - too high)
    total_spent = random(800, 2000)           # HIGH (currently 1183 - OK)
```

### Fix 3: Fix Order Distribution

```python
# Current distribution is inverted - too many high-order customers

# Realistic distribution (power-law):
order_count_distribution = {
    0: 0.15,      # 15% have 0 orders (currently 1.86%)
    1: 0.20,      # 20% have 1 order
    2: 0.15,      # 15% have 2 orders
    3: 0.15,      # 15% have 3-5 orders (currently 17.89% - OK)
    4: 0.10,      # 10% have 6-10 orders (currently 26.39% - too high)
    5: 0.10,      # 10% have 11-15 orders
    6: 0.05,      # 5% have 16-20 orders
    7: 0.10       # 10% have 21+ orders (currently 53.55% - way too high!)
}

# Implementation:
import random
rand = random.random()
if rand < 0.15:
    order_count = 0
elif rand < 0.35:
    order_count = random(1, 2)
elif rand < 0.50:
    order_count = random(3, 5)
elif rand < 0.60:
    order_count = random(6, 10)
elif rand < 0.70:
    order_count = random(11, 15)
elif rand < 0.75:
    order_count = random(16, 20)
else:
    order_count = random(21, 30)
```

## Expected Results After Fixes

### Correlations (Target)
```
SPEND_LOGIN_CORR:     0.45 - 0.60 (currently 0.159)
SPEND_EMAIL_CORR:     0.45 - 0.60 (currently 0.256)
ORDERS_LOGIN_CORR:    0.45 - 0.60 (currently 0.176)
RETURNS_RATING_CORR: -0.50 to -0.70 (currently NULL)
ABANDON_EMAIL_CORR:  -0.30 to -0.50 (currently 0.125 - wrong direction!)
```

### Churn Patterns (Target)
```
CHURNED_60_90D  AVG_MONTHS  AVG_LOGINS  AVG_EMAIL  AVG_ABANDONS  AVG_SPENT
--------------  ----------  ----------  ----------  ------------  ----------
             0        0.25       15.0       0.72          1.2     1200.0
             1        2.10        3.5       0.32          5.5      650.0
```

### Order Distribution (Target)
```
ORDE      COUNT PERCENTAGE
---- ---------- ----------
0           620      15.0%  (currently 1.86%)
1-2        1450      35.0%  (currently 0.31%)
3-5         620      15.0%  (currently 17.89%)
6-10        415      10.0%  (currently 26.39%)
11+         415      10.0%  (currently 53.55%)
```

## Priority Fixes

### 🔴 CRITICAL (Fix First)
1. **Login count for churners** - Currently backwards (8.94 vs 9.27)
2. **Email engagement** - Currently identical (0.994 vs 0.996)
3. **Cart abandons** - Too similar (0.89 vs 0.7)

### 🟡 IMPORTANT (Fix Second)
4. **Strengthen correlations** - All too weak (< 0.3)
5. **Fix order distribution** - Too many high-order customers
6. **Months since purchase** - Increase gap (1.0 vs 0.3 → 2.1 vs 0.25)

### 🟢 NICE TO HAVE (Fix Third)
7. **Returns-rating correlation** - Currently NULL
8. **Abandon-email correlation** - Currently wrong direction (positive)

## Model Performance After Fixes

With these fixes:
- **AUC should improve from 0.50 to 0.70-0.80**
- **Feature importance will be meaningful**
- **Model predictions will align with business logic**
- **Correlations will reflect real-world patterns**

## Validation Queries After Regeneration

```sql
-- 1. Check correlations
SELECT 
    CORR(TOTAL_SPENT_24M, LOGIN_COUNT_30D) as spend_login_corr,
    CORR(TOTAL_SPENT_24M, EMAIL_OPEN_RATE_30D) as spend_email_corr,
    CORR(ORDER_COUNT_24M, LOGIN_COUNT_30D) as orders_login_corr,
    CORR(TOTAL_RETURNS_COUNT, AVG_REVIEW_RATING) as returns_rating_corr,
    CORR(CART_ABANDONMENTS_30D, EMAIL_OPEN_RATE_30D) as abandon_email_corr
FROM OML.CHURN_FEATURES;

-- 2. Check churn patterns
SELECT 
    CHURNED_60_90D,
    ROUND(AVG(MONTHS_SINCE_LAST_PURCHASE), 2) as avg_months,
    ROUND(AVG(LOGIN_COUNT_30D), 2) as avg_logins,
    ROUND(AVG(EMAIL_OPEN_RATE_30D), 2) as avg_email,
    ROUND(AVG(CART_ABANDONMENTS_30D), 2) as avg_abandons,
    ROUND(AVG(TOTAL_SPENT_24M), 2) as avg_spent
FROM OML.CHURN_TRAINING_DATA
GROUP BY CHURNED_60_90D;

-- 3. Check order distribution
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

## Success Criteria

After regeneration, you should see:
- ✅ Correlations > 0.4 (positive) or < -0.3 (negative)
- ✅ Churners have FEWER logins (≤5 vs ≥10)
- ✅ Churners have LOWER email engagement (≤0.4 vs ≥0.6)
- ✅ Churners have MORE abandons (≥3 vs ≤2)
- ✅ Order distribution: 30-40% have 0-2 orders, 10-20% have 11+ orders
