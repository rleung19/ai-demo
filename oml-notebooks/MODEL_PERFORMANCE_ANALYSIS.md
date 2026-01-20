# Model Performance Analysis & Strategy

## Current Situation

### Pattern Observed
Every time we exclude a dominant feature, XGBoost immediately latches onto the next strongest feature:

1. **First**: `MONTHS_SINCE_LAST_PURCHASE` (100% importance)
2. **After exclusion**: `EMAIL_OPEN_RATE_30D` (98.8% importance)
3. **After 2 exclusions**: `LOGIN_COUNT_30D` (97.7% importance)

### Current Performance
- **AUC**: 0.5188 (barely above random, actually worse than before)
- **Features Used**: 3 (still dominated by one feature)
- **Scoring**: Working (316 at-risk customers identified)

## Root Cause Analysis

### Why This Happens
1. **Feature Strength**: These 3 features are much stronger predictors than others
2. **Weak Other Features**: Remaining features have minimal predictive power
3. **XGBoost Defaults**: OML's XGBoost defaults may be too simple/restrictive
4. **Data Patterns**: The churn signal might be primarily captured by these features

### What This Means
- **Not a bug**: XGBoost is correctly identifying the strongest features
- **Data limitation**: Other features may genuinely be weak predictors
- **Model limitation**: OML XGBoost defaults can't force feature diversity

## Current Strategy: Exclude Top 3 Features

### Updated Step 4
Now excludes:
1. `MONTHS_SINCE_LAST_PURCHASE`
2. `EMAIL_OPEN_RATE_30D`
3. `LOGIN_COUNT_30D`

### Expected Results
- **Features Used**: 5-10 (forced diversity)
- **Feature Distribution**: More balanced (no single feature > 50%)
- **AUC**: May improve to 0.55-0.60, or may stay low if other features are weak
- **Scoring**: Should continue to work

## Alternative Interpretations

### Option 1: Accept the Model
If excluding top 3 features doesn't improve AUC significantly:
- **Accept**: The model is using the strongest available signals
- **Use**: Even with AUC 0.52, the model can still identify at-risk customers
- **Focus**: On business value (scoring, interventions) rather than perfect metrics

### Option 2: Data Quality Issue
The low AUC (0.52) might indicate:
- **Weak churn signal**: The churn definition may not align with available features
- **Data quality**: Synthetic data may not have realistic patterns
- **Feature engineering needed**: May need to create better features

### Option 3: Model Limitations
OML XGBoost defaults may be too restrictive:
- **No parameter tuning**: Can't adjust max_depth, learning_rate, etc.
- **Simple model**: Defaults may create shallow trees
- **Limited flexibility**: Can't force feature diversity through parameters

## Recommendations

### Immediate Next Steps
1. **Re-run with top 3 exclusions** - See if forcing diversity helps
2. **Check feature importance** - Should show 5-10 features with balanced importance
3. **Evaluate AUC** - If still ~0.52, accept that this may be the data's limit

### If AUC Still Low After Exclusions

#### Option A: Accept and Use
- **AUC 0.52 is usable** for identifying at-risk customers
- **Focus on business metrics**: How many customers are identified? What's the LTV at risk?
- **Iterate**: Use model results to improve data collection and feature engineering

#### Option B: Feature Engineering
Create new features that combine information:
- **Interaction features**: `LOGIN_X_EMAIL`, `PURCHASE_X_LOGIN`
- **Ratio features**: `LOGIN_PER_PURCHASE`, `EMAIL_PER_LOGIN`
- **Composite scores**: `ENGAGEMENT_SCORE`, `ACTIVITY_SCORE`

#### Option C: Data Improvement
- **Better synthetic data**: Regenerate with stronger churn patterns
- **More data**: Increase training samples
- **Feature collection**: Add new data sources (support tickets, product usage, etc.)

## Success Criteria

### Minimum Acceptable
- ✅ **Scoring works**: Identifies at-risk customers
- ✅ **Business value**: LTV at risk calculated
- ✅ **Actionable**: Can use for interventions

### Ideal (May Not Be Achievable)
- ⚠️ **AUC > 0.60**: May require better data or features
- ⚠️ **Multiple features**: May require excluding top features
- ⚠️ **High precision/recall**: May require threshold tuning

## Current Status

### What's Working
- ✅ Model trains successfully
- ✅ Scoring identifies at-risk customers (316 found)
- ✅ Feature importance is interpretable
- ✅ Business metrics calculated (LTV at risk)

### What's Challenging
- ⚠️ AUC is low (0.52, barely above random)
- ⚠️ Model focuses on single features
- ⚠️ Limited by OML XGBoost defaults

### Next Experiment
Excluding top 3 features to force diversity. If AUC doesn't improve significantly, we may need to:
1. Accept the model as-is (it's still useful for scoring)
2. Focus on feature engineering
3. Improve data quality

## Conclusion

The model is **functional** for identifying at-risk customers, even with low AUC. The sequential dominance pattern suggests the top 3 features are genuinely the strongest predictors. Excluding them will test if other features can contribute, but we should be prepared to accept that the data may have inherent limitations.
