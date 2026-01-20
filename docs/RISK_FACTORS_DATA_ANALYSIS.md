# Top Churn Risk Factors - Data Availability Analysis

## Required Data for Risk Factors Table

The table needs 4 columns:
1. **RISK FACTOR** - Name of the risk factor
2. **IMPACT SCORE** - Percentage impact on churn
3. **AFFECTED CUSTOMERS** - Count of customers affected
4. **PRIMARY SEGMENT** - Which cohorts are most affected

## Current Risk Factors (from UI)

1. **Size/Fit Issues (2+ returns)**
   - Impact: 92%
   - Affected: 89 customers
   - Segment: VIP, Regular

2. **Email Engagement Decay**
   - Impact: 78%
   - Affected: 156 customers
   - Segment: All segments

3. **No Purchase in 45+ Days**
   - Impact: 65%
   - Affected: 203 customers
   - Segment: Regular, Dormant

4. **Negative Review Sentiment**
   - Impact: 54%
   - Affected: 42 customers
   - Segment: VIP

5. **Price Sensitivity (cart abandons)**
   - Impact: 38%
   - Affected: 118 customers
   - Segment: New, Regular

## Available Database Columns

### From `OML.USER_PROFILES`:
- ✅ `RETURNS_RATE` (NUMBER(5,2)) - Returns rate percentage
- ✅ `EMAIL_OPEN_RATE` (NUMBER(5,2)) - Email open rate percentage
- ✅ `DAYS_SINCE_LAST_PURCHASE` (NUMBER(5)) - Days since last purchase
- ✅ `CART_ABANDONMENT_RATE` (NUMBER(5,2)) - Cart abandonment rate
- ✅ `PRODUCT_REVIEWS_WRITTEN` (NUMBER(5)) - Count of reviews written
- ✅ `TOTAL_PURCHASES` (NUMBER(10)) - Total purchase count
- ✅ `LIFETIME_VALUE` (NUMBER(10,2)) - For segment identification
- ✅ `MEMBERSHIP_YEARS` (NUMBER(5,2)) - For segment identification
- ✅ `LOGIN_FREQUENCY` (NUMBER(5,2)) - For segment identification

### From `OML.CHURN_PREDICTIONS`:
- ✅ `PREDICTED_CHURN_LABEL` (NUMBER(1)) - Binary churn prediction
- ✅ `PREDICTED_CHURN_PROBABILITY` (NUMBER(5,4)) - Churn probability

### From `ADMIN.USERS`:
- ✅ `AFFINITY_CARD` (NUMBER(1)) - For VIP segment identification

## Data Availability Assessment

### ✅ **Fully Available:**

1. **Email Engagement Decay**
   - ✅ `EMAIL_OPEN_RATE` available
   - ✅ Can identify customers with low email engagement
   - ✅ Can calculate impact by correlating with churn predictions
   - ✅ Can determine primary segments using cohort logic

2. **No Purchase in 45+ Days**
   - ✅ `DAYS_SINCE_LAST_PURCHASE` available
   - ✅ Can identify customers with >45 days since purchase
   - ✅ Can calculate impact and affected customers
   - ✅ Can determine primary segments

3. **Price Sensitivity (cart abandons)**
   - ✅ `CART_ABANDONMENT_RATE` available
   - ✅ Can identify customers with high cart abandonment
   - ✅ Can calculate impact and affected customers
   - ✅ Can determine primary segments

### ⚠️ **Partially Available:**

4. **Size/Fit Issues (2+ returns)**
   - ⚠️ `RETURNS_RATE` is available (percentage), but NOT actual return count
   - ❌ Cannot directly identify "2+ returns" without return count
   - ✅ Can use `RETURNS_RATE` as a proxy (e.g., high returns rate)
   - ✅ Can calculate impact and affected customers
   - ✅ Can determine primary segments
   - **Workaround**: Use `RETURNS_RATE > threshold` (e.g., >20%) as proxy for "2+ returns"

### ❌ **Not Available:**

5. **Negative Review Sentiment**
   - ✅ `PRODUCT_REVIEWS_WRITTEN` available (count only)
   - ❌ **NO review sentiment data** in database
   - ❌ Cannot identify negative sentiment without sentiment analysis
   - **Options**:
     - Use `PRODUCT_REVIEWS_WRITTEN = 0` as proxy (customers who don't review might be unhappy)
     - Use `CUSTOMER_SERVICE_CALLS` as proxy (high support calls might indicate issues)
     - **Requires**: Additional table with review sentiment data or sentiment analysis

## Recommended Implementation Approach

### Phase 1: Implement Available Risk Factors (3-4 factors)

1. **Email Engagement Decay**
   ```sql
   SELECT 
     COUNT(*) as affected_customers,
     AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 as avg_churn_prob,
     -- Calculate impact score based on correlation
   FROM OML.USER_PROFILES up
   JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
   WHERE up.EMAIL_OPEN_RATE < 20  -- Low engagement threshold
   ```

2. **No Purchase in 45+ Days**
   ```sql
   SELECT 
     COUNT(*) as affected_customers,
     AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 as avg_churn_prob
   FROM OML.USER_PROFILES up
   JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
   WHERE up.DAYS_SINCE_LAST_PURCHASE > 45
   ```

3. **Price Sensitivity (cart abandons)**
   ```sql
   SELECT 
     COUNT(*) as affected_customers,
     AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 as avg_churn_prob
   FROM OML.USER_PROFILES up
   JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
   WHERE up.CART_ABANDONMENT_RATE > 50  -- High abandonment threshold
   ```

4. **Size/Fit Issues (using RETURNS_RATE as proxy)**
   ```sql
   SELECT 
     COUNT(*) as affected_customers,
     AVG(cp.PREDICTED_CHURN_PROBABILITY) * 100 as avg_churn_prob
   FROM OML.USER_PROFILES up
   JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
   WHERE up.RETURNS_RATE > 20  -- High returns rate threshold
   ```

### Phase 2: Calculate Impact Scores

Impact score can be calculated as:
- **Option 1**: Average churn probability of affected customers
- **Option 2**: Correlation coefficient between risk factor and churn
- **Option 3**: Percentage of at-risk customers who have this factor

### Phase 3: Determine Primary Segments

Use existing cohort logic to assign customers to segments, then count which segments are most affected by each risk factor.

## Conclusion

**Available Data: 3-4 out of 5 risk factors**

- ✅ Email Engagement Decay - **Fully available**
- ✅ No Purchase in 45+ Days - **Fully available**
- ✅ Price Sensitivity (cart abandons) - **Fully available**
- ⚠️ Size/Fit Issues - **Partially available** (can use RETURNS_RATE as proxy)
- ❌ Negative Review Sentiment - **Not available** (requires additional data source)

**Recommendation**: Implement the 3-4 available risk factors first, and either:
1. Use a proxy for "Negative Review Sentiment" (e.g., high customer service calls)
2. Add a new data source for review sentiment
3. Keep it as static/synthetic data until review sentiment data is available
