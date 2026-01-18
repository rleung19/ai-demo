# Cohort Definitions and Data Sources

## Overview

Cohorts are customer segments used for churn risk analysis. They are calculated from data in the `OML.USER_PROFILES` table combined with predictions from `OML.CHURN_PREDICTIONS`.

## Data Sources

### Primary Tables

1. **`OML.USER_PROFILES`** - Contains customer features:
   - `LIFETIME_VALUE` - Customer lifetime value (USD)
   - `MEMBERSHIP_YEARS` - Years as a member
   - `DAYS_SINCE_LAST_PURCHASE` - Days since last purchase
   - `LOGIN_FREQUENCY` - Login frequency per period
   - `TOTAL_PURCHASES` - Total number of purchases
   - `AVERAGE_ORDER_VALUE` - Average order value

2. **`OML.CHURN_PREDICTIONS`** - Contains model predictions:
   - `PREDICTED_CHURN_PROBABILITY` - Churn probability (0-1)
   - `PREDICTED_CHURN_LABEL` - Binary prediction (0/1)
   - `RISK_SCORE` - Risk score (0-100)

## Cohort Definitions

### 1. VIP Cohort

**Definition**: High-value customers with significant lifetime value or loyalty card membership

**Criteria** (Updated based on actual data):
- `LIFETIME_VALUE > 5000` OR
- `AFFINITY_CARD = 1` (from `ADMIN.USERS`)

**Note**: This definition focuses on high-value customers (LTV > $5,000) or customers with loyalty cards, representing premium customers.

**Data Source**:
- `OML.USER_PROFILES.LIFETIME_VALUE`
- `ADMIN.USERS.AFFINITY_CARD` (requires join)

**Current Distribution** (from actual data):
- Users with LTV > $5,000: 20 (0.40%)
- Users with AFFINITY_CARD = 1: 962 (19.22%)
- Total VIP users: 976 (19.5% of all users)
- At-risk VIP users: 248 (25.4% of VIPs)
- Average churn probability: 27.78%

**SQL Example**:
```sql
SELECT 
  'VIP' AS cohort,
  COUNT(*) AS customer_count,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
JOIN ADMIN.USERS au ON up.USER_ID = au.ID
WHERE up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1;
```

### 2. Regular Cohort

**Definition**: Active customers with normal engagement patterns

**Criteria**:
- NOT VIP (doesn't meet VIP criteria)
- AND `TOTAL_PURCHASES >= 2` (has made at least 2 purchases)
- AND `DAYS_SINCE_LAST_PURCHASE <= 90` (active in last 90 days)
- AND `LOGIN_FREQUENCY > 0` (has logged in)

**Data Source**:
- `OML.USER_PROFILES.TOTAL_PURCHASES`
- `OML.USER_PROFILES.DAYS_SINCE_LAST_PURCHASE`
- `OML.USER_PROFILES.LOGIN_FREQUENCY`
- Excludes VIP customers

**SQL Example**:
```sql
SELECT 
  'Regular' AS cohort,
  COUNT(*) AS customer_count,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
JOIN ADMIN.USERS au ON up.USER_ID = au.ID
WHERE NOT (up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1)
  AND up.TOTAL_PURCHASES >= 2
  AND up.DAYS_SINCE_LAST_PURCHASE <= 90
  AND up.LOGIN_FREQUENCY > 0;
```

### 3. New Cohort

**Definition**: Recently acquired customers

**Criteria**:
- NOT VIP (doesn't meet VIP criteria)
- AND `MEMBERSHIP_YEARS < 1` (less than 1 year as member)

**Data Source**:
- `OML.USER_PROFILES.MEMBERSHIP_YEARS`
- Excludes VIP customers

**SQL Example**:
```sql
SELECT 
  'New' AS cohort,
  COUNT(*) AS customer_count,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
JOIN ADMIN.USERS au ON up.USER_ID = au.ID
WHERE NOT (up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1)
  AND up.MEMBERSHIP_YEARS < 1;
```

### 4. Dormant Cohort

**Definition**: Customers with no recent activity

**Criteria**:
- NOT VIP (doesn't meet VIP criteria)
- AND NOT New (membership >= 1 year)
- AND (`DAYS_SINCE_LAST_PURCHASE > 90` OR `LOGIN_FREQUENCY = 0`)

**Data Source**:
- `OML.USER_PROFILES.DAYS_SINCE_LAST_PURCHASE`
- `OML.USER_PROFILES.LOGIN_FREQUENCY`
- Excludes VIP and New customers

**SQL Example**:
```sql
SELECT 
  'Dormant' AS cohort,
  COUNT(*) AS customer_count,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score,
  SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
JOIN ADMIN.USERS au ON up.USER_ID = au.ID
WHERE NOT (up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1)
  AND up.MEMBERSHIP_YEARS >= 1
  AND (up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0);
```

### 5. At-Risk Cohort

**Definition**: Customers with high churn probability (regardless of other segments)

**Criteria**:
- `PREDICTED_CHURN_PROBABILITY > 0.41` (optimal threshold)
- OR `PREDICTED_CHURN_LABEL = 1`

**Data Source**:
- `OML.CHURN_PREDICTIONS.PREDICTED_CHURN_PROBABILITY`
- `OML.CHURN_PREDICTIONS.PREDICTED_CHURN_LABEL`

**Note**: This cohort can overlap with other cohorts. A customer can be both "VIP" and "At-Risk".

**SQL Example**:
```sql
SELECT 
  'At-Risk' AS cohort,
  COUNT(*) AS customer_count,
  COUNT(*) AS at_risk_count,  -- All are at-risk by definition
  100.0 AS at_risk_percentage,  -- 100% by definition
  AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score,
  SUM(up.LIFETIME_VALUE) AS ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
WHERE cp.PREDICTED_CHURN_PROBABILITY > 0.41;
```

## Cohort Calculation Priority

Cohorts are calculated in this order (mutually exclusive except for At-Risk):

1. **VIP** - Highest priority (checked first)
2. **New** - If not VIP and membership < 1 year
3. **Dormant** - If not VIP/New and inactive
4. **Regular** - If not VIP/New/Dormant and active
5. **At-Risk** - Can overlap with any cohort (based on prediction only)

## Complete SQL Query for All Cohorts

```sql
WITH cohort_assignments AS (
  SELECT 
    cp.USER_ID,
    cp.PREDICTED_CHURN_PROBABILITY,
    cp.PREDICTED_CHURN_LABEL,
    up.LIFETIME_VALUE,
    up.MEMBERSHIP_YEARS,
    up.TOTAL_PURCHASES,
    up.DAYS_SINCE_LAST_PURCHASE,
    up.LOGIN_FREQUENCY,
    CASE 
      WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
      WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
      WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
      WHEN up.TOTAL_PURCHASES >= 2 AND up.DAYS_SINCE_LAST_PURCHASE <= 90 AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
      ELSE 'Other'
    END AS cohort
  FROM OML.CHURN_PREDICTIONS cp
  JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
  JOIN ADMIN.USERS au ON up.USER_ID = au.ID
)
SELECT 
  cohort,
  COUNT(*) AS customer_count,
  SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
  ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
  SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
FROM cohort_assignments
WHERE cohort != 'Other'
GROUP BY cohort
ORDER BY 
  CASE cohort
    WHEN 'VIP' THEN 1
    WHEN 'Regular' THEN 2
    WHEN 'New' THEN 3
    WHEN 'Dormant' THEN 4
    ELSE 5
  END;
```

## Field Availability

All required fields are available in `OML.USER_PROFILES`:

| Field | Available | Type | Notes |
|-------|-----------|------|-------|
| `LIFETIME_VALUE` | ✅ Yes | NUMBER(10,2) | For VIP calculation |
| `MEMBERSHIP_YEARS` | ✅ Yes | NUMBER(5,2) | For VIP and New |
| `TOTAL_PURCHASES` | ✅ Yes | NUMBER(10) | For Regular |
| `DAYS_SINCE_LAST_PURCHASE` | ✅ Yes | NUMBER(5) | For Dormant and Regular |
| `LOGIN_FREQUENCY` | ✅ Yes | NUMBER(5,2) | For Dormant and Regular |

## Implementation Notes

1. **Cohorts are calculated on-the-fly** - No separate cohort table needed
2. **Join required** - Must join `CHURN_PREDICTIONS` with `USER_PROFILES`
3. **At-Risk is separate** - Can overlap with other cohorts
4. **Threshold from model** - Use optimal threshold (0.41) from `MODEL_REGISTRY`

## API Implementation

The `/api/kpi/churn/cohorts` endpoint will:
1. Query `OML.CHURN_PREDICTIONS` joined with `OML.USER_PROFILES`
2. Calculate cohort for each customer using CASE statement
3. Aggregate by cohort (count, at-risk count, avg risk, LTV at risk)
4. Return JSON array of cohort data

## Related Documentation

- `docs/API_ENDPOINT_DESIGN.md` - API endpoint specifications
- `docs/API_DATA_CONTRACTS.md` - Request/response schemas
- `sql/create_churn_tables.sql` - Database schema
- `docs/DATA_MAPPING_DOCUMENT.md` - Field mappings
