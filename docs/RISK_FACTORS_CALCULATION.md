# Top Churn Risk Factors - Calculation Methodology

## Overview

This document explains how to calculate the three key metrics for each risk factor:
1. **Impact Score** - How much the risk factor affects churn (percentage)
2. **Affected Customers** - Count of customers with this risk factor
3. **Primary Segment** - Which customer cohorts are most affected

## Calculation Methods

### 1. Affected Customers

**Definition**: Count of customers who meet the risk factor criteria.

**Calculation**: Simple COUNT(*) with WHERE clause filtering for the risk factor.

**Example**:
```sql
-- Email Engagement Decay: Customers with low email open rate
SELECT COUNT(*) as affected_customers
FROM OML.USER_PROFILES up
JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
WHERE up.EMAIL_OPEN_RATE < 20  -- Threshold: <20% open rate
```

### 2. Impact Score

**Definition**: A percentage (0-100%) indicating how strongly the risk factor correlates with churn.

**Three Possible Calculation Methods**:

#### Method A: Average Churn Probability of Affected Customers (Recommended)
**Formula**: Average `PREDICTED_CHURN_PROBABILITY` for customers with the risk factor, multiplied by 100.

**Rationale**: Shows the average churn risk for customers with this factor.

```sql
-- Example: Email Engagement Decay
SELECT 
  ROUND(AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score
FROM OML.USER_PROFILES up
JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
WHERE up.EMAIL_OPEN_RATE < 20
```

**Pros**: 
- Directly shows churn risk level
- Easy to understand
- Uses existing prediction data

**Cons**: 
- Doesn't show relative impact vs. baseline

#### Method B: Percentage of Affected Customers Who Are At-Risk
**Formula**: (Count of at-risk customers with factor / Total customers with factor) × 100

**Rationale**: Shows what percentage of affected customers are predicted to churn.

```sql
-- Example: Email Engagement Decay
SELECT 
  ROUND(
    (SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) * 100.0) / 
    COUNT(*), 
    1
  ) as impact_score
FROM OML.USER_PROFILES up
JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
WHERE up.EMAIL_OPEN_RATE < 20
```

**Pros**: 
- Shows binary impact (churn vs. no churn)
- Easy to interpret

**Cons**: 
- Less granular than probability-based method

#### Method C: Relative Impact vs. Baseline (Most Sophisticated)
**Formula**: 
```
Impact Score = ((Avg Churn Prob of Affected - Avg Churn Prob of All) / Avg Churn Prob of All) × 100
```

**Rationale**: Shows how much higher the churn risk is for affected customers compared to the overall average.

```sql
-- Example: Email Engagement Decay
WITH baseline AS (
  SELECT AVG(PREDICTED_CHURN_PROBABILITY) as avg_all
  FROM OML.CHURN_PREDICTIONS
),
affected AS (
  SELECT AVG(cp.PREDICTED_CHURN_PROBABILITY) as avg_affected
  FROM OML.USER_PROFILES up
  JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
  WHERE up.EMAIL_OPEN_RATE < 20
)
SELECT 
  ROUND(
    ((a.avg_affected - b.avg_all) / b.avg_all) * 100, 
    1
  ) as impact_score
FROM affected a, baseline b
```

**Pros**: 
- Shows relative impact
- Normalizes across different baseline churn rates

**Cons**: 
- More complex
- Can produce negative scores if factor reduces churn

**Recommendation**: Use **Method A** (Average Churn Probability) for simplicity and clarity.

### 3. Primary Segment

**Definition**: The customer cohorts (VIP, Regular, New, Dormant) most affected by the risk factor.

**Calculation Steps**:
1. Assign each customer to a cohort using existing cohort logic
2. Count affected customers per cohort
3. Identify the top 1-2 cohorts with the most affected customers
4. Format as comma-separated list (e.g., "VIP, Regular")

**SQL Example**:
```sql
WITH cohort_assignments AS (
  SELECT 
    up.USER_ID,
    CASE 
      WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
      WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
      WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
      WHEN up.TOTAL_PURCHASES >= 2 
           AND up.DAYS_SINCE_LAST_PURCHASE <= 90 
           AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
      ELSE 'Other'
    END AS cohort
  FROM OML.USER_PROFILES up
  JOIN ADMIN.USERS au ON up.USER_ID = au.ID
),
affected_by_cohort AS (
  SELECT 
    ca.cohort,
    COUNT(*) as affected_count
  FROM cohort_assignments ca
  JOIN OML.USER_PROFILES up ON ca.USER_ID = up.USER_ID
  WHERE up.EMAIL_OPEN_RATE < 20  -- Risk factor criteria
    AND ca.cohort != 'Other'
  GROUP BY ca.cohort
  ORDER BY affected_count DESC
)
SELECT 
  LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY affected_count DESC) as primary_segment
FROM (
  SELECT cohort, affected_count
  FROM affected_by_cohort
  WHERE ROWNUM <= 2  -- Top 2 segments
)
```

**Alternative (Simpler)**: Count per cohort and select top segments:
```sql
-- Get top 2 segments
SELECT 
  cohort,
  COUNT(*) as affected_count
FROM (
  -- Cohort assignment + risk factor filter
  SELECT 
    CASE 
      WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
      WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
      WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
      WHEN up.TOTAL_PURCHASES >= 2 
           AND up.DAYS_SINCE_LAST_PURCHASE <= 90 
           AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
      ELSE 'Other'
    END AS cohort
  FROM OML.USER_PROFILES up
  JOIN ADMIN.USERS au ON up.USER_ID = au.ID
  WHERE up.EMAIL_OPEN_RATE < 20  -- Risk factor criteria
)
WHERE cohort != 'Other'
GROUP BY cohort
ORDER BY affected_count DESC
FETCH FIRST 2 ROWS ONLY
```

## Complete SQL Query Example

Here's a complete query that calculates all three metrics for one risk factor:

```sql
-- Email Engagement Decay Risk Factor
WITH cohort_assignments AS (
  SELECT 
    up.USER_ID,
    cp.PREDICTED_CHURN_PROBABILITY,
    cp.PREDICTED_CHURN_LABEL,
    CASE 
      WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
      WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
      WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
      WHEN up.TOTAL_PURCHASES >= 2 
           AND up.DAYS_SINCE_LAST_PURCHASE <= 90 
           AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
      ELSE 'Other'
    END AS cohort
  FROM OML.USER_PROFILES up
  JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
  JOIN ADMIN.USERS au ON up.USER_ID = au.ID
  WHERE up.EMAIL_OPEN_RATE < 20  -- Risk factor: Low email engagement
),
cohort_counts AS (
  SELECT 
    cohort,
    COUNT(*) as count
  FROM cohort_assignments
  WHERE cohort != 'Other'
  GROUP BY cohort
  ORDER BY count DESC
)
SELECT 
  'Email Engagement Decay' as risk_factor,
  COUNT(*) as affected_customers,
  ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) as impact_score,
  (
    SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY count DESC)
    FROM (
      SELECT cohort, count
      FROM cohort_counts
      WHERE ROWNUM <= 2
    )
  ) as primary_segment
FROM cohort_assignments
WHERE cohort != 'Other'
```

## Risk Factor Definitions & Thresholds

### 1. Email Engagement Decay
- **Criteria**: `EMAIL_OPEN_RATE < 20`
- **Threshold**: Less than 20% email open rate

### 2. No Purchase in 45+ Days
- **Criteria**: `DAYS_SINCE_LAST_PURCHASE > 45`
- **Threshold**: More than 45 days since last purchase

### 3. Price Sensitivity (Cart Abandons)
- **Criteria**: `CART_ABANDONMENT_RATE > 50`
- **Threshold**: More than 50% cart abandonment rate

### 4. Size/Fit Issues (High Returns)
- **Criteria**: `RETURNS_RATE > 20`
- **Threshold**: More than 20% returns rate (proxy for 2+ returns)

### 5. Negative Review Sentiment (Proxy: High Support Calls)
- **Criteria**: `CUSTOMER_SERVICE_CALLS > 2`
- **Threshold**: More than 2 customer service calls
- **Note**: This is a proxy since review sentiment is not available

## Implementation Notes

1. **Impact Score Format**: Display as percentage with 1 decimal place (e.g., "78.5%")

2. **Primary Segment Format**: 
   - If one segment dominates (>60% of affected): Show single segment
   - If two segments are significant: Show "Segment1, Segment2"
   - If evenly distributed: Show "All segments"

3. **Ordering**: Risk factors should be ordered by Impact Score (highest first)

4. **Performance**: Consider caching results since these calculations may be expensive

5. **Thresholds**: Thresholds may need tuning based on actual data distribution
