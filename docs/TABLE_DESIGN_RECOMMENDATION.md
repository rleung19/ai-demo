# Table Design Recommendation for KPI #1

## Summary

**Recommendation**: Design **one additional table now** (`CHURN_PREDICTIONS_HISTORY`), and defer the rest until API design.

## Essential Tables (Design Now)

### ✅ Already Designed:
1. **`OML.CHURN_DATASET_TRAINING`** - Training data
2. **`OML.USER_PROFILES`** - Input features
3. **`OML.CHURN_PREDICTIONS`** - Current predictions

### ⚠️ **NEW: Design Now**
4. **`OML.CHURN_PREDICTIONS_HISTORY`** - Historical predictions for trends
   - **Why now**: Essential for KPI #1 trends ("↑ 12 from last week", "↓ 3% improved")
   - **Why now**: Needed for 7-week chart data
   - **Why now**: Schema won't change based on API design

## Can Wait Until API Design

### Defer These Decisions:

1. **Cohort Assignment Strategy**
   - **Option A**: Derive from `USER_PROFILES` features (e.g., `TOTAL_PURCHASES`, `DAYS_SINCE_LAST_PURCHASE`)
   - **Option B**: Store in separate `USER_COHORTS` table
   - **Decision**: Wait until API design to see query patterns

2. **Risk Factors Table**
   - **Option A**: Calculate from model feature importance (on-the-fly)
   - **Option B**: Pre-compute and store in `RISK_FACTORS` table
   - **Decision**: Wait until API design to see if pre-computation is needed

3. **Aggregation Views**
   - **Option A**: Calculate aggregations in API (SQL queries)
   - **Option B**: Create materialized views for performance
   - **Decision**: Wait until API design to see performance needs

4. **Additional Analytics Tables**
   - Any other tables needed for advanced analytics
   - **Decision**: Wait until API design reveals requirements

## Rationale

### Why Design `CHURN_PREDICTIONS_HISTORY` Now:

✅ **Clear requirement**: KPI #1 needs trend data  
✅ **Stable schema**: Won't change based on API implementation  
✅ **Blocking**: Needed for Task 1.3 (database schema design)  
✅ **Simple**: Straightforward time-series table  

### Why Defer Everything Else:

⏳ **Query patterns unknown**: Don't know exact API query patterns yet  
⏳ **Performance unknown**: Don't know if views/optimizations needed  
⏳ **Flexibility**: Can add tables/views during API development  
⏳ **Iterative**: Better to design based on actual API needs  

## Action Plan

### Now (Task 1.3):
1. ✅ Design `CHURN_PREDICTIONS_HISTORY` table
2. ✅ Add to SQL schema creation script
3. ✅ Document in data mapping document

### During API Design (Task 4.x):
1. ⏳ Decide cohort assignment strategy
2. ⏳ Design risk factors approach
3. ⏳ Create aggregation views if needed
4. ⏳ Optimize based on query patterns

## Updated Table List

1. `OML.CHURN_DATASET_TRAINING` - Training data (45,858 rows)
2. `OML.USER_PROFILES` - Input features (4,142 rows)
3. `OML.CHURN_PREDICTIONS` - Current predictions (4,142 rows)
4. `OML.CHURN_PREDICTIONS_HISTORY` - Historical predictions (time-series)

**Total**: 4 tables for initial implementation
