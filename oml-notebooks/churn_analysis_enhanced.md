# Churn Analysis - Enhanced Model Notebook

This is a text-based reference for the enhanced model workflow. Import this into OML Notebooks by copying each cell into a new paragraph.

## Step 1: Create Enhanced Features View

```sql
-- Create enhanced features view with interaction and composite features
CREATE OR REPLACE VIEW OML.CHURN_FEATURES_ENHANCED AS
SELECT 
    cf.*,
    
    -- ============================================
    -- INTERACTION FEATURES (Top 3 features)
    -- ============================================
    -- Months since purchase * Login count (captures inactivity + disengagement)
    cf.MONTHS_SINCE_LAST_PURCHASE * COALESCE(cf.LOGIN_COUNT_30D, 0) AS MONTHS_X_LOGIN,
    
    -- Months since purchase * Cart abandonments (captures purchase delay + price sensitivity)
    cf.MONTHS_SINCE_LAST_PURCHASE * COALESCE(cf.CART_ABANDONMENTS_30D, 0) AS MONTHS_X_ABANDON,
    
    -- Login count * Cart abandonments (captures engagement vs price sensitivity)
    COALESCE(cf.LOGIN_COUNT_30D, 0) * COALESCE(cf.CART_ABANDONMENTS_30D, 0) AS LOGIN_X_ABANDON,
    
    -- Months since purchase * Email open rate (captures purchase delay + email engagement)
    cf.MONTHS_SINCE_LAST_PURCHASE * COALESCE(cf.EMAIL_OPEN_RATE_30D, 0) AS MONTHS_X_EMAIL,
    
    -- Login count * Email open rate (captures overall engagement)
    COALESCE(cf.LOGIN_COUNT_30D, 0) * COALESCE(cf.EMAIL_OPEN_RATE_30D, 0) AS LOGIN_X_EMAIL,
    
    -- ============================================
    -- RATIO FEATURES
    -- ============================================
    -- Purchase frequency (orders per month since last purchase)
    CASE 
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE > 0 THEN 
            COALESCE(cf.ORDER_COUNT_24M, 0) / NULLIF(cf.MONTHS_SINCE_LAST_PURCHASE, 0)
        ELSE 0
    END AS PURCHASE_FREQUENCY,
    
    -- Cart abandonment rate
    CASE 
        WHEN COALESCE(cf.CART_ADDITIONS_30D, 0) > 0 THEN 
            COALESCE(cf.CART_ABANDONMENTS_30D, 0) / NULLIF(cf.CART_ADDITIONS_30D, 0)
        ELSE 0
    END AS CART_ABANDON_RATE,
    
    -- Login frequency (logins per month)
    COALESCE(cf.LOGIN_COUNT_30D, 0) / 30.0 AS LOGIN_FREQUENCY,
    
    -- Return rate
    CASE 
        WHEN COALESCE(cf.ORDER_COUNT_24M, 0) > 0 THEN 
            COALESCE(cf.TOTAL_RETURNS_COUNT, 0) / NULLIF(cf.ORDER_COUNT_24M, 0)
        ELSE 0
    END AS RETURN_RATE,
    
    -- ============================================
    -- COMPOSITE ENGAGEMENT SCORES
    -- ============================================
    -- Overall engagement score (weighted combination)
    (COALESCE(cf.EMAIL_OPEN_RATE_30D, 0) * 0.3 + 
     LEAST(COALESCE(cf.LOGIN_COUNT_30D, 0) / 30.0, 1.0) * 0.3 +
     CASE 
         WHEN COALESCE(cf.CART_ADDITIONS_30D, 0) > 0 THEN 
             1 - LEAST(COALESCE(cf.CART_ABANDONMENTS_30D, 0) / NULLIF(cf.CART_ADDITIONS_30D, 0), 1.0)
         ELSE 0
     END * 0.2 +
     CASE 
         WHEN cf.MONTHS_SINCE_LAST_PURCHASE > 0 THEN 
             LEAST(1.0 / NULLIF(cf.MONTHS_SINCE_LAST_PURCHASE, 0), 1.0)
         ELSE 0
     END * 0.2) AS ENGAGEMENT_SCORE,
    
    -- Purchase engagement score
    (CASE 
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE <= 0.5 THEN 1.0
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE <= 1.0 THEN 0.7
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE <= 1.5 THEN 0.4
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE <= 2.0 THEN 0.2
        ELSE 0.1
     END * 
     LEAST(COALESCE(cf.ORDER_COUNT_24M, 0) / 10.0, 1.0)) AS PURCHASE_ENGAGEMENT,
    
    -- ============================================
    -- RISK INDICATORS (Binary flags)
    -- ============================================
    -- High risk: inactive + low engagement
    CASE 
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 1.5 
             AND COALESCE(cf.LOGIN_COUNT_30D, 0) <= 3 THEN 1 
        ELSE 0 
    END AS HIGH_RISK_INACTIVE,
    
    -- Disengagement: cart abandons + low email
    CASE 
        WHEN COALESCE(cf.CART_ABANDONMENTS_30D, 0) >= 3 
             AND COALESCE(cf.EMAIL_OPEN_RATE_30D, 0) < 0.2 THEN 1 
        ELSE 0 
    END AS HIGH_RISK_DISENGAGED,
    
    -- Price sensitivity: high abandons + low purchases
    CASE 
        WHEN COALESCE(cf.CART_ABANDONMENTS_30D, 0) >= 3 
             AND cf.MONTHS_SINCE_LAST_PURCHASE >= 1.0 THEN 1 
        ELSE 0 
    END AS HIGH_RISK_PRICE_SENSITIVE,
    
    -- ============================================
    -- TEMPORAL TRENDS
    -- ============================================
    -- Recent activity decline (last 30 days vs 24 months)
    CASE 
        WHEN COALESCE(cf.ORDER_COUNT_24M, 0) > 0 THEN 
            (COALESCE(cf.ORDER_COUNT_24M, 0) / 24.0) - (COALESCE(cf.LOGIN_COUNT_30D, 0) / 30.0)
        ELSE 0
    END AS ACTIVITY_DECLINE,
    
    -- Customer lifecycle stage (based on age and purchase frequency)
    CASE 
        WHEN cf.CUSTOMER_AGE_MONTHS < 3 THEN 'New'
        WHEN cf.CUSTOMER_AGE_MONTHS < 12 AND COALESCE(cf.ORDER_COUNT_24M, 0) >= 5 THEN 'Growing'
        WHEN cf.CUSTOMER_AGE_MONTHS >= 12 AND COALESCE(cf.ORDER_COUNT_24M, 0) >= 10 THEN 'Mature'
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 2 THEN 'Dormant'
        ELSE 'Active'
    END AS LIFECYCLE_STAGE
    
FROM OML.CHURN_FEATURES cf;
```

## Step 2: Create Enhanced Training Data View

```sql
-- Create enhanced training data view
CREATE OR REPLACE VIEW OML.CHURN_TRAINING_DATA_ENHANCED AS
SELECT 
    cfe.*,
    ctd.CHURNED_60_90D
FROM OML.CHURN_FEATURES_ENHANCED cfe
INNER JOIN OML.CHURN_TRAINING_DATA ctd ON cfe.USER_ID = ctd.USER_ID
WHERE ctd.CUSTOMER_AGE_MONTHS >= 3
    AND ctd.ORDER_COUNT_24M > 0;
```

## Step 3: Verify Enhanced Views

```sql
-- Verify enhanced views
SELECT COUNT(*) AS ENHANCED_FEATURES_COUNT FROM OML.CHURN_FEATURES_ENHANCED;
SELECT COUNT(*) AS ENHANCED_TRAINING_COUNT FROM OML.CHURN_TRAINING_DATA_ENHANCED;

-- Check new feature columns
SELECT COLUMN_NAME 
FROM ALL_TAB_COLUMNS 
WHERE OWNER = 'OML' 
  AND TABLE_NAME = 'CHURN_FEATURES_ENHANCED'
  AND (COLUMN_NAME LIKE 'MONTHS_X_%' 
       OR COLUMN_NAME LIKE 'LOGIN_X_%'
       OR COLUMN_NAME LIKE '%_RATE'
       OR COLUMN_NAME LIKE '%_SCORE'
       OR COLUMN_NAME LIKE 'HIGH_RISK_%'
       OR COLUMN_NAME LIKE 'PURCHASE_%'
       OR COLUMN_NAME LIKE 'ACTIVITY_%'
       OR COLUMN_NAME LIKE 'LIFECYCLE_%'
       OR COLUMN_NAME LIKE 'ENGAGEMENT_%')
ORDER BY COLUMN_NAME;
```

## Step 4: Prepare Features and Split Data (with categorical features)

```python
%python
# Prepare features and split data (including categorical features)
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

# Load training data
train_data = oml.sync(view='CHURN_TRAINING_DATA_ENHANCED')
train_data_pd = train_data.pull()

print("=" * 60)
print("Preparing Features and Splitting Data (Enhanced)")
print("=" * 60)
print("Training data shape: " + str(train_data_pd.shape))

# Identify categorical columns
categorical_cols = ['CUST_MARITAL_STATUS', 'CUST_INCOME_LEVEL', 'GENDER', 
                    'EDUCATION', 'OCCUPATION', 'HOUSEHOLD_SIZE', 'LOGIN_FREQUENCY_CATEGORY']

# Convert categorical features to numeric codes
for col in categorical_cols:
    if col in train_data_pd.columns:
        # Convert to category codes (numeric)
        train_data_pd[col + '_NUM'] = pd.Categorical(train_data_pd[col]).codes
        # Replace -1 (for NaN) with 0
        train_data_pd[col + '_NUM'] = train_data_pd[col + '_NUM'].replace(-1, 0)
        print("Converted " + col + " to " + col + "_NUM")

# Handle LIFECYCLE_STAGE if it exists
if 'LIFECYCLE_STAGE' in train_data_pd.columns:
    lifecycle_mapping = {'New': 0, 'Growing': 1, 'Mature': 2, 'Active': 3, 'Dormant': 4}
    train_data_pd['LIFECYCLE_STAGE_NUM'] = train_data_pd['LIFECYCLE_STAGE'].map(lifecycle_mapping).fillna(0)
    print("Converted LIFECYCLE_STAGE to LIFECYCLE_STAGE_NUM")

# Identify feature columns (exclude target, metadata, and original categorical columns)
exclude_cols = ['USER_ID', 'CUSTOMER_SEGMENT', 'ESTIMATED_LTV', 'CHURNED_60_90D', 'LIFECYCLE_STAGE']
# Also exclude original categorical columns (we'll use _NUM versions)
exclude_cols.extend(categorical_cols)

# Get all numeric columns (including converted categoricals)
feature_cols = [col for col in train_data_pd.columns 
                if col not in exclude_cols
                and pd.api.types.is_numeric_dtype(train_data_pd[col])]

print("\nTotal features: " + str(len(feature_cols)))
print("Features: " + ", ".join(feature_cols[:10]) + "...")

# Prepare X and y
X_enhanced_pd = train_data_pd[feature_cols].copy()
y_enhanced_pd = train_data_pd['CHURNED_60_90D']

# Clean data - replace NaN and infinity
for col in feature_cols:
    if pd.api.types.is_numeric_dtype(X_enhanced_pd[col]):
        X_enhanced_pd[col] = X_enhanced_pd[col].replace([np.inf, -np.inf], np.nan)
        X_enhanced_pd[col] = X_enhanced_pd[col].fillna(0)

# Stratified split
X_train_enhanced_pd, X_test_enhanced_pd, y_train_enhanced_pd, y_test_enhanced_pd = train_test_split(
    X_enhanced_pd, y_enhanced_pd, 
    test_size=0.2, 
    random_state=42, 
    stratify=y_enhanced_pd
)

print("\nSplit completed:")
print("  Train size: " + str(len(X_train_enhanced_pd)))
print("  Test size: " + str(len(X_test_enhanced_pd)))
print("  Train churn rate: " + str(round(y_train_enhanced_pd.mean() * 100, 2)) + "%")
print("  Test churn rate: " + str(round(y_test_enhanced_pd.mean() * 100, 2)) + "%")
print("  Total features: " + str(len(feature_cols)))
print("  Categorical features (converted): " + str(len([f for f in feature_cols if '_NUM' in f])))
```

## Step 5: Train Enhanced Model

```python
%python
# Train XGBoost model with enhanced features (including categorical features)
import pandas as pd
import numpy as np

print("=" * 60)
print("Training Enhanced XGBoost Model (with Categorical Features)")
print("=" * 60)

# Merge X_train and y_train for database push
train_enhanced_combined_pd = X_train_enhanced_pd.copy()
train_enhanced_combined_pd['CHURNED_60_90D'] = y_train_enhanced_pd.values

# Final check before pushing
print("Final data validation before push:")
print("  Shape: " + str(train_enhanced_combined_pd.shape))
print("  Columns: " + str(len(train_enhanced_combined_pd.columns)))
print("  NULL count: " + str(train_enhanced_combined_pd.isna().sum().sum()))

# Ensure all feature columns are numeric
for col in feature_cols:
    if col in train_enhanced_combined_pd.columns:
        train_enhanced_combined_pd[col] = pd.to_numeric(train_enhanced_combined_pd[col], errors='coerce').fillna(0)

# Push to database
print("\nPushing enhanced training data to database...")
try:
    train_enhanced_oml = oml.push(train_enhanced_combined_pd)
    print("Training data pushed: " + str(train_enhanced_oml.shape))
except Exception as e:
    print("Error pushing data: " + str(e))
    print("Trying with explicit data type conversion...")
    # Try converting all to float
    for col in train_enhanced_combined_pd.columns:
        if col != 'CHURNED_60_90D':
            train_enhanced_combined_pd[col] = train_enhanced_combined_pd[col].astype(float)
    train_enhanced_oml = oml.push(train_enhanced_combined_pd)
    print("Training data pushed after type conversion: " + str(train_enhanced_oml.shape))

# Get actual columns available in OML DataFrame
available_oml_cols = list(train_enhanced_oml.columns)
print("\nAvailable columns in OML DataFrame: " + str(len(available_oml_cols)))

# Define feature columns - use only features that exist in OML DataFrame
enhanced_feature_cols_clean = [col for col in feature_cols if col in available_oml_cols]

# Check for any missing features
missing_features = [col for col in feature_cols if col not in available_oml_cols]
if len(missing_features) > 0:
    print("\n⚠️  Warning: Some features missing from OML DataFrame:")
    print("  Missing: " + ", ".join(missing_features[:5]) + "...")
    print("  Using " + str(len(enhanced_feature_cols_clean)) + " available features")

print("\nFeatures for training: " + str(len(enhanced_feature_cols_clean)))
categorical_count = len([f for f in enhanced_feature_cols_clean if '_NUM' in f])
print("  - Categorical features (converted): " + str(categorical_count))
print("  - Numeric features: " + str(len(enhanced_feature_cols_clean) - categorical_count))
print("First 10 features: " + ", ".join(enhanced_feature_cols_clean[:10]))

# Create XGBoost model
xgb_model_enhanced = oml.xgb('classification')

# Get features and target from OML DataFrame
X_train_enhanced_oml = train_enhanced_oml[enhanced_feature_cols_clean]
y_train_enhanced_oml = train_enhanced_oml['CHURNED_60_90D']

print("\nX_train_enhanced_oml shape: " + str(X_train_enhanced_oml.shape))
print("Features: " + str(len(enhanced_feature_cols_clean)))
print("Training started...")

# Fit the model
try:
    xgb_model_enhanced = xgb_model_enhanced.fit(X_train_enhanced_oml, y_train_enhanced_oml)
    print("Training completed!")
except Exception as e:
    print("Training failed: " + str(e))
    import traceback
    traceback.print_exc()
```

## Step 6: Evaluate Enhanced Model

```python
%python
# Evaluate enhanced model performance (with same features as training)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
import pandas as pd
import numpy as np

# Prepare test data - use same categorical conversion as training
print("Preparing test data...")
test_enhanced_combined_pd = X_test_enhanced_pd.copy()
test_enhanced_combined_pd['CHURNED_60_90D'] = y_test_enhanced_pd.values

# Convert categorical features to numeric codes (same as training)
categorical_cols = ['CUST_MARITAL_STATUS', 'CUST_INCOME_LEVEL', 'GENDER', 
                    'EDUCATION', 'OCCUPATION', 'HOUSEHOLD_SIZE', 'LOGIN_FREQUENCY_CATEGORY']

for col in categorical_cols:
    if col in test_enhanced_combined_pd.columns:
        # Convert to category codes (numeric) - use same categories as training
        # Get categories from training data to ensure consistency
        if col in X_train_enhanced_pd.columns:
            # Use the same categories from training
            train_categories = pd.Categorical(X_train_enhanced_pd[col]).categories
            test_enhanced_combined_pd[col + '_NUM'] = pd.Categorical(test_enhanced_combined_pd[col], categories=train_categories).codes
        else:
            test_enhanced_combined_pd[col + '_NUM'] = pd.Categorical(test_enhanced_combined_pd[col]).codes
        # Replace -1 (for NaN) with 0
        test_enhanced_combined_pd[col + '_NUM'] = test_enhanced_combined_pd[col + '_NUM'].replace(-1, 0)

# Handle LIFECYCLE_STAGE if it exists
if 'LIFECYCLE_STAGE' in test_enhanced_combined_pd.columns:
    lifecycle_mapping = {'New': 0, 'Growing': 1, 'Mature': 2, 'Active': 3, 'Dormant': 4}
    test_enhanced_combined_pd['LIFECYCLE_STAGE_NUM'] = test_enhanced_combined_pd['LIFECYCLE_STAGE'].map(lifecycle_mapping).fillna(0)

# Clean all numeric columns
for col in test_enhanced_combined_pd.columns:
    if col != 'CHURNED_60_90D':
        if pd.api.types.is_numeric_dtype(test_enhanced_combined_pd[col]):
            test_enhanced_combined_pd[col] = pd.to_numeric(test_enhanced_combined_pd[col], errors='coerce').fillna(0)

# Push to database
print("Pushing test data to database...")
test_enhanced_oml = oml.push(test_enhanced_combined_pd)

# Get actual columns available in OML DataFrame
available_test_cols = list(test_enhanced_oml.columns)

# Use only the features that were used in training (from Step 5)
features_for_prediction = [col for col in enhanced_feature_cols_clean if col in available_test_cols]

# Check for any missing features
missing_features = [col for col in enhanced_feature_cols_clean if col not in available_test_cols]
if len(missing_features) > 0:
    print("⚠️  Warning: Some training features missing in test data:")
    print("  Missing: " + ", ".join(missing_features))
    print("  Using " + str(len(features_for_prediction)) + " available features")

print("Features for prediction: " + str(len(features_for_prediction)))
print("  (Same features as training)")

# Get features for prediction
X_test_enhanced_oml = test_enhanced_oml[features_for_prediction]

print("X_test_enhanced_oml shape: " + str(X_test_enhanced_oml.shape))
print("Features: " + str(len(features_for_prediction)))

# Get predictions
print("\nGenerating predictions...")
y_pred_proba_enhanced_oml = xgb_model_enhanced.predict_proba(X_test_enhanced_oml)

# Convert to numpy array
y_pred_proba_enhanced_pd = y_pred_proba_enhanced_oml.pull()
if isinstance(y_pred_proba_enhanced_pd, pd.DataFrame):
    if 1 in y_pred_proba_enhanced_pd.columns:
        y_pred_proba_enhanced = y_pred_proba_enhanced_pd[1].values
    elif len(y_pred_proba_enhanced_pd.columns) == 2:
        y_pred_proba_enhanced = y_pred_proba_enhanced_pd.iloc[:, 1].values
    else:
        y_pred_proba_enhanced = y_pred_proba_enhanced_pd.values.flatten()
else:
    y_pred_proba_enhanced = np.array(y_pred_proba_enhanced_pd)

# Convert probabilities to binary predictions (threshold = 0.1)
y_pred_enhanced = (y_pred_proba_enhanced >= 0.1).astype(int)
y_test_enhanced_vals = y_test_enhanced_pd.values

# Calculate metrics
accuracy_enhanced = accuracy_score(y_test_enhanced_vals, y_pred_enhanced)
precision_enhanced = precision_score(y_test_enhanced_vals, y_pred_enhanced, zero_division=0)
recall_enhanced = recall_score(y_test_enhanced_vals, y_pred_enhanced, zero_division=0)
f1_enhanced = f1_score(y_test_enhanced_vals, y_pred_enhanced, zero_division=0)
auc_enhanced = roc_auc_score(y_test_enhanced_vals, y_pred_proba_enhanced)

# Confusion matrix
cm_enhanced = confusion_matrix(y_test_enhanced_vals, y_pred_enhanced)
tn_enhanced, fp_enhanced, fn_enhanced, tp_enhanced = cm_enhanced.ravel()

print("=" * 60)
print("ENHANCED MODEL EVALUATION METRICS")
print("=" * 60)
print("Accuracy:  " + str(round(accuracy_enhanced, 4)) + " (" + str(round(accuracy_enhanced*100, 2)) + "%)")
print("Precision: " + str(round(precision_enhanced, 4)) + " (" + str(round(precision_enhanced*100, 2)) + "%)")
print("Recall:    " + str(round(recall_enhanced, 4)) + " (" + str(round(recall_enhanced*100, 2)) + "%)")
print("F1 Score:  " + str(round(f1_enhanced, 4)))
print("AUC-ROC:   " + str(round(auc_enhanced, 4)))
print("Model Confidence: " + str(int(auc_enhanced * 100)) + "%")

print("\nConfusion Matrix:")
print("                Predicted")
print("              Non-Churn  Churn")
print("Actual Non-Churn   " + str(tn_enhanced) + "   " + str(fp_enhanced))
print("       Churn       " + str(fn_enhanced) + "   " + str(tp_enhanced))

# Compare with original model
if 'auc' in globals() and 'f1' in globals():
    print("\n" + "=" * 60)
    print("COMPARISON: Original vs Enhanced Model")
    print("=" * 60)
    print("Metric              Original    Enhanced    Improvement")
    print("-" * 60)
    
    acc_improvement = accuracy_enhanced - accuracy
    prec_improvement = precision_enhanced - precision
    rec_improvement = recall_enhanced - recall
    f1_improvement = f1_enhanced - f1
    auc_improvement = auc_enhanced - auc
    
    print("Accuracy:           " + str(round(accuracy, 4)) + "      " + str(round(accuracy_enhanced, 4)) + "      " + str(round(acc_improvement, 4)))
    print("Precision:          " + str(round(precision, 4)) + "      " + str(round(precision_enhanced, 4)) + "      " + str(round(prec_improvement, 4)))
    print("Recall:             " + str(round(recall, 4)) + "      " + str(round(recall_enhanced, 4)) + "      " + str(round(rec_improvement, 4)))
    print("F1 Score:           " + str(round(f1, 4)) + "      " + str(round(f1_enhanced, 4)) + "      " + str(round(f1_improvement, 4)))
    print("AUC-ROC:            " + str(round(auc, 4)) + "      " + str(round(auc_enhanced, 4)) + "      " + str(round(auc_improvement, 4)))
    
    improvement_pct = ((auc_enhanced - auc) / auc * 100) if auc > 0 else 0
    print("\nAUC Improvement: " + str(round(improvement_pct, 2)) + "%")
    
    if auc_improvement > 0.01:
        print("✓ Significant improvement! Feature engineering is working.")
    elif auc_improvement > 0:
        print("✓ Small improvement. May need more feature engineering or hyperparameter tuning.")
    else:
        print("⚠️  No improvement. Consider:")
        print("   - Different interaction features")
        print("   - Hyperparameter tuning")
        print("   - Trying other algorithms")
else:
    print("\n(Original model metrics not available for comparison)")
```

## Step 7: Feature Importance (Enhanced)

```python
%python
# Get feature importance for enhanced model
import pandas as pd

print("=" * 60)
print("Enhanced Model Feature Importance")
print("=" * 60)

# Get importance
importance_enhanced_result = xgb_model_enhanced.importance
importance_enhanced_df_raw = importance_enhanced_result.pull()

# Extract feature names and importance
if 'ATTRIBUTE_NAME' in importance_enhanced_df_raw.columns and 'GAIN' in importance_enhanced_df_raw.columns:
    importance_enhanced_df = importance_enhanced_df_raw[['ATTRIBUTE_NAME', 'GAIN']].copy()
    importance_enhanced_df.columns = ['FEATURE_NAME', 'IMPORTANCE_SCORE']
    importance_enhanced_df = importance_enhanced_df.sort_values('IMPORTANCE_SCORE', ascending=False)
    
    print("\nTop 20 Most Important Features (Enhanced Model):")
    print(importance_enhanced_df.head(20).to_string(index=False))
    
    # Check if new engineered features are in top features
    new_features_list = [
        'MONTHS_X_LOGIN', 'MONTHS_X_ABANDON', 'LOGIN_X_ABANDON', 
        'MONTHS_X_EMAIL', 'LOGIN_X_EMAIL',
        'PURCHASE_FREQUENCY', 'CART_ABANDON_RATE', 'RETURN_RATE',
        'ENGAGEMENT_SCORE', 'PURCHASE_ENGAGEMENT',
        'HIGH_RISK_INACTIVE', 'HIGH_RISK_DISENGAGED', 'HIGH_RISK_PRICE_SENSITIVE',
        'ACTIVITY_DECLINE'
    ]
    
    top_features = importance_enhanced_df.head(20)['FEATURE_NAME'].tolist()
    new_features_in_top = [f for f in top_features if f in new_features_list]
    
    print("\nNew engineered features in top 20: " + str(len(new_features_in_top)))
    if len(new_features_in_top) > 0:
        print("Features: " + ", ".join(new_features_in_top))
        print("\n✓ New engineered features are contributing to the model!")
    else:
        print("No new engineered features in top 20")
        print("(This may indicate the original features are still more predictive)")
```

## Step 8: Summary and Next Steps

```python
%python
# Summary of feature engineering results
print("=" * 60)
print("FEATURE ENGINEERING SUMMARY")
print("=" * 60)

print("\n--- What Was Added ---")
print("1. Interaction Features:")
print("   - MONTHS_X_LOGIN, MONTHS_X_ABANDON, LOGIN_X_ABANDON")
print("   - MONTHS_X_EMAIL, LOGIN_X_EMAIL")
print("2. Ratio Features:")
print("   - PURCHASE_FREQUENCY, CART_ABANDON_RATE, RETURN_RATE")
print("3. Composite Scores:")
print("   - ENGAGEMENT_SCORE, PURCHASE_ENGAGEMENT")
print("4. Risk Indicators:")
print("   - HIGH_RISK_INACTIVE, HIGH_RISK_DISENGAGED, HIGH_RISK_PRICE_SENSITIVE")
print("5. Temporal Features:")
print("   - ACTIVITY_DECLINE, LIFECYCLE_STAGE")
print("6. Categorical Features:")
print("   - Converted to numeric codes for model inclusion")

print("\n--- Model Performance ---")
if 'auc_enhanced' in globals() and 'auc' in globals():
    print("Original Model AUC: " + str(round(auc, 4)) + " (" + str(int(auc * 100)) + "%)")
    print("Enhanced Model AUC: " + str(round(auc_enhanced, 4)) + " (" + str(int(auc_enhanced * 100)) + "%)")
    improvement = auc_enhanced - auc
    improvement_pct = (improvement / auc * 100) if auc > 0 else 0
    print("Improvement: " + str(round(improvement, 4)) + " (" + str(round(improvement_pct, 2)) + "%)")
    
    if improvement > 0.01:
        print("\n✓ Significant improvement! Feature engineering is working.")
    elif improvement > 0:
        print("\n✓ Small improvement. May need more feature engineering or hyperparameter tuning.")
    else:
        print("\n⚠️  No improvement. Consider:")
        print("   - Different interaction features")
        print("   - Hyperparameter tuning")
        print("   - Trying other algorithms")

print("\n--- Next Steps ---")
print("1. If improved: Save enhanced model and use for production")
print("2. If not improved: Try hyperparameter tuning")
print("3. Consider: Additional feature engineering based on domain knowledge")
print("4. Validate: Test on holdout set or cross-validation")

print("\n" + "=" * 60)
print("Feature engineering complete!")
print("=" * 60)
```
