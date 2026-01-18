# KPI #1 Table Requirements Analysis

## KPI #1 Data Needs

### 1. Summary Metrics (Card Display)
- **At-Risk Customers**: Count of users with `PREDICTED_CHURN_LABEL = 1`
- **Avg Risk Score**: Average of `PREDICTED_CHURN_PROBABILITY`
- **LTV at Risk**: Sum of `LIFETIME_VALUE` for at-risk users
- **Model Confidence**: From model metadata (not stored in table)

**Source**: Can calculate from `CHURN_PREDICTIONS` + `USER_PROFILES.LIFETIME_VALUE`

### 2. Trend Data (Required for UI)
- **"↑ 12 from last week"**: Need historical at-risk customer counts
- **"↓ 3% improved"**: Need historical average risk scores
- **7-week chart data**: Historical trends for mini chart

**Source**: Need historical predictions (not just current)

### 3. Cohort Breakdown
- **Cohorts**: VIP, Regular, New, Dormant, At-Risk
- **Per Cohort**: Churn probability %, customer count, LTV

**Source**: 
- Can derive cohorts from `USER_PROFILES` features (e.g., `TOTAL_PURCHASES`, `DAYS_SINCE_LAST_PURCHASE`)
- Or store cohort assignment separately

### 4. Chart Data (Detail Modal)
- **Cohort chart**: Churn probability % by cohort
- **Time series**: 7 weeks of historical data

**Source**: Historical predictions + cohort assignments

### 5. Risk Factors Table
- **Risk Factor**: Name (e.g., "Size/Fit Issues")
- **Impact Score**: Percentage
- **Affected Customers**: Count
- **Primary Segment**: Cohort name

**Source**: 
- Can calculate from feature importance (model explainability)
- Or store separately if pre-computed

### 6. Model Metadata
- Model type, confidence, training data, last update
- **Source**: Model metadata (not in tables)

---

## Current Table Design

### ✅ Already Designed:
1. **`OML.USER_PROFILES`** - Input features (includes `LIFETIME_VALUE`)
2. **`OML.CHURN_PREDICTIONS`** - Current predictions

### ❓ Missing for Full KPI #1 Support:

#### Option A: Extend CHURN_PREDICTIONS (Recommended)
Add historical tracking to existing table:
- Keep current predictions (latest)
- Add `CHURN_PREDICTIONS_HISTORY` for trends

#### Option B: Add Separate History Table
Create `CHURN_PREDICTIONS_HISTORY` for time-series data

---

## Recommendation: Design Now (Minimal)

### Essential Tables to Design Now:

1. **`OML.CHURN_PREDICTIONS`** ✅ (Already designed)
   - Current predictions
   - Used for: Summary metrics, cohort breakdown

2. **`OML.CHURN_PREDICTIONS_HISTORY`** ⚠️ (NEW - Needed for trends)
   - Historical predictions (weekly snapshots)
   - Used for: Trend calculations, 7-week charts
   - **Columns**:
     - `USER_ID`
     - `PREDICTED_CHURN_PROBABILITY`
     - `PREDICTED_CHURN_LABEL`
     - `RISK_SCORE`
     - `SNAPSHOT_DATE` (weekly)
     - `MODEL_VERSION`

3. **Cohort Assignment** ⚠️ (Can derive or store)
   - **Option 1**: Derive from `USER_PROFILES` features (simpler)
   - **Option 2**: Store in separate table (more flexible)
   - **Recommendation**: Derive for now, add table later if needed

### Can Wait Until API Design:

- **Risk Factors Table**: Can calculate from feature importance
- **Cohort Metadata**: Can derive from features
- **Detailed Analytics**: Can aggregate on-the-fly

---

## Decision: Design Now or Later?

### ✅ **Design Now** (Minimal):
- `CHURN_PREDICTIONS_HISTORY` table
- Basic schema for trend tracking

### ⏳ **Design During API**:
- Cohort assignment strategy (derive vs. store)
- Risk factors calculation approach
- Aggregation views/optimizations

### 🎯 **Recommendation**: 
**Design `CHURN_PREDICTIONS_HISTORY` now** - it's essential for trends and won't change. Everything else can be designed during API development when we know exact query patterns.
