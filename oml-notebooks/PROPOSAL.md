# Churn Prediction Model Development Proposal

## Executive Summary

This proposal outlines the development of a customer churn prediction model using Oracle Machine Learning (OML) on Oracle Autonomous Database (ADB). The solution uses XGBoost classification to predict customers at risk of churning within 60-90 days, enabling proactive retention strategies.

## Business Objective

**Goal**: Identify customers at high risk of churning within 60-90 days to enable targeted retention campaigns and reduce customer lifetime value (LTV) loss.

**Success Metrics**:
- Model AUC-ROC > 0.70 (target: 0.80+)
- Identify 15-20% of customer base as at-risk
- Enable targeted interventions for high-value customers

## Technical Architecture

### Technology Stack
- **Database**: Oracle Autonomous Database (Serverless)
- **ML Framework**: OML4Py (Oracle Machine Learning for Python)
- **Algorithm**: XGBoost Binary Classification
- **Development Environment**: OML Notebooks UI
- **Frontend Integration**: Next.js/TypeScript (existing project)

### Data Sources
- **ADMIN Schema Tables**:
  - `USERS` - Customer demographics and profile data
  - `ORDERS` - Purchase history (24 months)
  - `ORDER_ITEMS` - Order line items
  - `LOGIN_EVENTS` - User login activity (30 days)
  - `PRODUCT_REVIEWS` - Review ratings and sentiment (24 months)
  - `EMAIL_ENGAGEMENT` - Email open/click rates (30 days)
  - `CART_EVENTS` - Shopping cart behavior (30 days)
  - `RETURNS` - Product return history (24 months)

### Database Schema
- **OML Schema**: Stores ML models and feature views
  - `CHURN_FEATURES` - Comprehensive feature view
  - `CHURN_TRAINING_DATA` - Training dataset with churn target
  - `CHURN_FEATURES_ENHANCED` - Enhanced features with interactions
  - `CHURN_TRAINING_DATA_ENHANCED` - Enhanced training dataset

## Model Development Phases

### Phase 1: Original Model (Baseline)
**Objective**: Establish baseline model performance

**Steps**:
1. Create feature engineering views (`CHURN_FEATURES`, `CHURN_TRAINING_DATA`)
2. Data exploration and validation
3. Train XGBoost model with 42 original features
4. Evaluate model performance
5. Feature importance analysis
6. Threshold optimization
7. Customer scoring and cohort analysis

**Expected Performance**: AUC-ROC ~0.52 (baseline, needs improvement)

### Phase 2: Enhanced Model (Feature Engineering)
**Objective**: Improve model performance through advanced feature engineering

**Enhancements**:
1. **Interaction Features**: 
   - `MONTHS_X_LOGIN`, `MONTHS_X_ABANDON`, `LOGIN_X_ABANDON`
   - `MONTHS_X_EMAIL`, `LOGIN_X_EMAIL`
   
2. **Ratio Features**:
   - `PURCHASE_FREQUENCY`, `CART_ABANDON_RATE`, `RETURN_RATE`
   
3. **Composite Scores**:
   - `ENGAGEMENT_SCORE`, `PURCHASE_ENGAGEMENT`
   
4. **Risk Indicators**:
   - `HIGH_RISK_INACTIVE`, `HIGH_RISK_DISENGAGED`, `HIGH_RISK_PRICE_SENSITIVE`
   
5. **Temporal Features**:
   - `ACTIVITY_DECLINE`, `LIFECYCLE_STAGE`

6. **Categorical Feature Encoding**:
   - Convert categorical features to numeric codes for model inclusion

**Expected Performance**: AUC-ROC improvement over baseline

## Churn Definition

Multi-factor risk-based approach:
- **Dormant Segment**: Automatically churned
- **High Risk**: 0.75+ months since last purchase
- **Medium Risk**: 0.5+ months + activity decline (low logins, email engagement, or cart abandons)
- **Low Activity**: ≤3 logins in 30 days

**Target Churn Rate**: 15% (balanced for model training)

## Customer Segmentation

- **VIP**: Has affinity card (`AFFINITY_CARD > 0`)
- **Regular**: 2+ orders OR $500+ spent in 24 months
- **New**: Exactly 1 order
- **Dormant**: No orders in 2+ months
- **At-Risk**: Everyone else

## Model Performance Metrics

### Evaluation Metrics
- **Accuracy**: Overall prediction correctness
- **Precision**: Of predicted churners, how many actually churn
- **Recall**: Of actual churners, how many did we catch
- **F1 Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Model's ability to distinguish between classes (primary metric)

### Current Performance (Original Model)
- Accuracy: ~76%
- Precision: ~19%
- Recall: ~19%
- F1 Score: ~0.19
- AUC-ROC: ~0.52 (needs improvement)

## Key Features (Top 3 by Importance)

1. **MONTHS_SINCE_LAST_PURCHASE** (77% importance)
2. **CART_ABANDONMENTS_30D** (11.9% importance)
3. **LOGIN_COUNT_30D** (10.8% importance)

## Next Steps for Improvement

1. **Hyperparameter Tuning**: Optimize XGBoost parameters (max_depth, learning_rate, n_estimators)
2. **Additional Feature Engineering**: Domain-specific features based on business insights
3. **Churn Definition Refinement**: Validate with actual churn data
4. **Alternative Algorithms**: Try Random Forest, GLM, or ensemble methods
5. **Class Imbalance Handling**: Adjust sampling strategies or class weights

## Deliverables

1. **OML Notebooks**:
   - `churn_analysis_original.json` - Complete original model workflow
   - `churn_analysis_enhanced.json` - Enhanced model with feature engineering

2. **Documentation**:
   - This proposal document
   - Step-by-step execution guide
   - Model performance reports

3. **Database Objects**:
   - Feature views (SQL)
   - Trained models (saved in OML datastore)

## Usage Instructions

1. **Prerequisites**:
   - Oracle ADB instance with OML enabled
   - ADMIN and OML schema access
   - Required tables populated with data

2. **Import Notebooks**:
   - Import JSON files into OML Notebooks UI
   - Run cells sequentially

3. **Execution Order**:
   - Start with original model to establish baseline
   - Run enhanced model to see improvements
   - Compare results and iterate

## Risk Factors Identified

Based on model analysis, top risk factors:
1. No purchase in 45+ days (1.5+ months)
2. High cart abandonments (3+)
3. Low login activity (≤3 logins in 30 days)
4. Email engagement decay
5. Size/fit issues (2+ returns)

## Business Impact

- **At-Risk Customers Identified**: ~815 customers (19.7% of base)
- **LTV at Risk**: $1.37M
- **Actionable Insights**: Cohort-level risk distribution enables targeted campaigns
- **Model Confidence**: Current 52%, target 80%+

## Conclusion

This proposal provides a complete framework for developing and deploying a churn prediction model using OML on Oracle ADB. The solution includes both baseline and enhanced models, with clear paths for further improvement through hyperparameter tuning and additional feature engineering.
