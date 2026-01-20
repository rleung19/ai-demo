# Data Validation Results - Synthetic Data Issues

## Current Data Analysis

**Query Results**:
```
CHURNED_60_90D      COUNT AVG_MONTHS AVG_LOGINS AVG_EMAIL_RATE AVG_ABANDONS
-------------- ---------- ---------- ---------- -------------- ------------
             0       3240         .3       9.28              1           .7
             1        799          1       8.95            .99          .89
```

## Critical Issues Found

### 1. **Churners Have MORE Logins** ❌ BACKWARDS!
- **Current**: Churners = 8.95, Non-churners = 9.28
- **Expected**: Churners should have FEWER logins (2-5 vs 10-20)
- **Impact**: Model can't learn that low logins = churn risk

### 2. **Email Engagement Nearly Identical** ❌ NO SIGNAL
- **Current**: Churners = 0.99, Non-churners = 1.0
- **Expected**: Churners should have LOWER engagement (0.2-0.4 vs 0.6-0.8)
- **Impact**: No predictive signal from email engagement

### 3. **Months Since Purchase Too Similar** ⚠️ WEAK SIGNAL
- **Current**: Churners = 1.0, Non-churners = 0.3
- **Expected**: Churners should have MUCH higher (1.5-3.0 vs 0.1-0.5)
- **Impact**: Weak signal, model struggles to distinguish

### 4. **Cart Abandons Too Similar** ⚠️ WEAK SIGNAL
- **Current**: Churners = 0.89, Non-churners = 0.7
- **Expected**: Churners should have MORE (3-8 vs 0-2)
- **Impact**: Weak signal

## Why Model Fails (AUC ~50%)

The model can't learn because:
1. **Features don't distinguish churners**: Churners and non-churners look almost identical
2. **Backwards patterns**: Churners have MORE logins (should be less)
3. **No clear signals**: Differences are too small to learn from

## Required Data Regeneration

### Target Patterns for Churners (CHURNED_60_90D = 1)

```sql
-- Churners should have:
AVG_MONTHS_SINCE_LAST_PURCHASE: 1.5 - 3.0 (not 1.0)
AVG_LOGIN_COUNT_30D: 2 - 5 (not 8.95 - should be LOWER!)
AVG_EMAIL_OPEN_RATE_30D: 0.2 - 0.4 (not 0.99 - should be LOWER!)
AVG_CART_ABANDONMENTS_30D: 3 - 8 (not 0.89 - should be HIGHER!)
```

### Target Patterns for Non-Churners (CHURNED_60_90D = 0)

```sql
-- Non-churners should have:
AVG_MONTHS_SINCE_LAST_PURCHASE: 0.1 - 0.5 (current 0.3 is OK)
AVG_LOGIN_COUNT_30D: 10 - 20 (current 9.28 is close, but should be HIGHER than churners)
AVG_EMAIL_OPEN_RATE_30D: 0.6 - 0.8 (current 1.0 is too high, but should be HIGHER than churners)
AVG_CART_ABANDONMENTS_30D: 0 - 2 (current 0.7 is OK, but should be LOWER than churners)
```

## Specific Fixes Needed in Data Generation

### Fix 1: Login Count (CRITICAL - Currently Backwards!)
```python
# Current (WRONG):
churners_login = random(5, 15)  # Too high!
non_churners_login = random(8, 12)  # Similar to churners

# Should be:
churners_login = random(2, 5)  # LOW for churners
non_churners_login = random(10, 20)  # HIGH for non-churners
```

### Fix 2: Email Engagement (CRITICAL - No Signal)
```python
# Current (WRONG):
churners_email = random(0.95, 1.0)  # Too high!
non_churners_email = random(0.98, 1.0)  # Identical!

# Should be:
churners_email = random(0.2, 0.4)  # LOW for churners
non_churners_email = random(0.6, 0.8)  # HIGH for non-churners
```

### Fix 3: Months Since Purchase (IMPORTANT - Too Similar)
```python
# Current:
churners_months = random(0.5, 1.5)  # Too low!
non_churners_months = random(0.1, 0.5)  # OK

# Should be:
churners_months = random(1.5, 3.0)  # HIGH for churners
non_churners_months = random(0.1, 0.5)  # Keep as is
```

### Fix 4: Cart Abandons (IMPORTANT - Too Similar)
```python
# Current:
churners_abandons = random(0.5, 1.5)  # Too low!
non_churners_abandons = random(0.3, 1.0)  # Too similar

# Should be:
churners_abandons = random(3, 8)  # HIGH for churners
non_churners_abandons = random(0, 2)  # LOW for non-churners
```

## Expected Results After Fix

After regenerating with correct patterns, you should see:

```
CHURNED_60_90D      COUNT AVG_MONTHS AVG_LOGINS AVG_EMAIL_RATE AVG_ABANDONS
-------------- ---------- ---------- ---------- -------------- ------------
             0       3240        0.3      15.2           0.72          1.2
             1        799        2.1       3.5           0.32          5.8
```

**Key Differences**:
- ✅ Months: 2.1 vs 0.3 (7x difference - clear signal)
- ✅ Logins: 3.5 vs 15.2 (churners have FEWER - correct direction)
- ✅ Email: 0.32 vs 0.72 (churners have LOWER - correct direction)
- ✅ Abandons: 5.8 vs 1.2 (churners have MORE - correct direction)

## Model Performance After Fix

With realistic patterns:
- **AUC should improve from 0.50 to 0.65-0.75**
- **Feature importance will make sense** (MONTHS_SINCE_LAST_PURCHASE should be top)
- **Model predictions will align with business logic**

## Action Items

1. ✅ **Fix data generation script** with patterns above
2. ✅ **Regenerate all tables** (ORDERS, LOGIN_EVENTS, EMAIL_ENGAGEMENT, CART_EVENTS, etc.)
3. ✅ **Re-run validation query** to confirm patterns
4. ✅ **Re-train model** and check AUC improvement

## Validation Query to Run After Regeneration

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

**Success Criteria**:
- ✅ Churners have HIGHER months (≥1.5 vs ≤0.5)
- ✅ Churners have LOWER logins (≤5 vs ≥10)
- ✅ Churners have LOWER email rate (≤0.4 vs ≥0.6)
- ✅ Churners have HIGHER abandons (≥3 vs ≤2)
