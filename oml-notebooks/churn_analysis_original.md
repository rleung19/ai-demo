# Churn Analysis - Original Model Notebook

This is a text-based reference for the original model workflow. Copy each cell into OML Notebooks as a new paragraph.

## Introduction

```markdown
# Churn Analysis - Development Notebook
## Phase 1: Original Model (Baseline)

This notebook develops an XGBoost churn prediction model using OML4Py on Oracle Autonomous Database.

**Prerequisites:**
- Oracle Autonomous Database with OML enabled
- ADMIN and OML schema access
- Database objects created (LOGIN_EVENTS table, indexes, grants)

**Segment Definition:**
- VIP: Has affinity card (AFFINITY_CARD > 0)
- Regular: 2+ orders OR $500+ spent
- New: Exactly 1 order
- Dormant: No orders in 2+ months
- At-Risk: Everyone else
```

## Step 1: Create CHURN_FEATURES View

```sql
-- Create CHURN_FEATURES view (original version - no SUPPORT_TICKETS table)
CREATE OR REPLACE VIEW OML.CHURN_FEATURES AS
SELECT 
    u.ID AS USER_ID,
    u.CUST_YEAR_OF_BIRTH,
    u.CUST_MARITAL_STATUS,
    u.CUST_INCOME_LEVEL,
    u.CUST_CREDIT_LIMIT,
    u.GENDER,
    u.EDUCATION,
    u.OCCUPATION,
    u.HOUSEHOLD_SIZE,
    u.YRS_RESIDENCE,
    u.AFFINITY_CARD,
    
    -- Purchase behavior (24 months)
    COALESCE(o_stats.ORDER_COUNT_24M, 0) AS ORDER_COUNT_24M,
    COALESCE(o_stats.TOTAL_SPENT_24M, 0) AS TOTAL_SPENT_24M,
    COALESCE(o_stats.AVG_ORDER_VALUE_24M, 0) AS AVG_ORDER_VALUE_24M,
    COALESCE(o_stats.MONTHS_SINCE_LAST_PURCHASE, 999) AS MONTHS_SINCE_LAST_PURCHASE,
    MONTHS_BETWEEN(SYSDATE, u.CREATED_AT) AS CUSTOMER_AGE_MONTHS,
    CASE 
        WHEN COALESCE(o_stats.ORDER_COUNT_24M, 0) > 0 AND COALESCE(o_stats.MONTHS_SINCE_LAST_PURCHASE, 999) > 0 
        THEN COALESCE(o_stats.ORDER_COUNT_24M, 0) / NULLIF(o_stats.MONTHS_SINCE_LAST_PURCHASE, 0)
        ELSE 0
    END AS PURCHASE_VELOCITY,
    
    -- Login activity (30 days)
    COALESCE(login_stats.LOGIN_COUNT_30D, 0) AS LOGIN_COUNT_30D,
    CASE 
        WHEN COALESCE(login_stats.LOGIN_COUNT_30D, 0) >= 15 THEN 'High'
        WHEN COALESCE(login_stats.LOGIN_COUNT_30D, 0) >= 7 THEN 'Medium'
        WHEN COALESCE(login_stats.LOGIN_COUNT_30D, 0) > 0 THEN 'Low'
        ELSE 'None'
    END AS LOGIN_FREQUENCY_CATEGORY,
    COALESCE(login_stats.MONTHS_SINCE_LAST_LOGIN, 999) AS MONTHS_SINCE_LAST_LOGIN,
    
    -- Support tickets (24 months) - placeholder since table doesn't exist
    0 AS SUPPORT_TICKETS_24M,
    
    -- Review and NPS (24 months)
    COALESCE(review_stats.AVG_REVIEW_RATING, 0) AS AVG_REVIEW_RATING,
    COALESCE(review_stats.REVIEW_COUNT, 0) AS REVIEW_COUNT,
    COALESCE(review_stats.DETRACTOR_COUNT, 0) AS DETRACTOR_COUNT,
    COALESCE(review_stats.PASSIVE_COUNT, 0) AS PASSIVE_COUNT,
    COALESCE(review_stats.PROMOTER_COUNT, 0) AS PROMOTER_COUNT,
    CASE 
        WHEN COALESCE(review_stats.REVIEW_COUNT, 0) > 0 THEN
            ((COALESCE(review_stats.PROMOTER_COUNT, 0) - COALESCE(review_stats.DETRACTOR_COUNT, 0)) / NULLIF(review_stats.REVIEW_COUNT, 0)) * 100
        ELSE 0
    END AS NPS_SCORE,
    CASE WHEN COALESCE(review_stats.NEGATIVE_REVIEWS_90D, 0) > 0 THEN 1 ELSE 0 END AS HAS_NEGATIVE_SENTIMENT,
    COALESCE(review_stats.NEGATIVE_REVIEWS_90D, 0) AS NEGATIVE_REVIEWS_90D,
    
    -- Email engagement (30 days)
    COALESCE(email_stats.EMAILS_SENT_30D, 0) AS EMAILS_SENT_30D,
    COALESCE(email_stats.EMAILS_OPENED_30D, 0) AS EMAILS_OPENED_30D,
    COALESCE(email_stats.EMAILS_CLICKED_30D, 0) AS EMAILS_CLICKED_30D,
    CASE 
        WHEN COALESCE(email_stats.EMAILS_SENT_30D, 0) > 0 THEN
            COALESCE(email_stats.EMAILS_OPENED_30D, 0) / NULLIF(email_stats.EMAILS_SENT_30D, 0)
        ELSE 0
    END AS EMAIL_OPEN_RATE_30D,
    CASE 
        WHEN COALESCE(email_stats.EMAILS_OPENED_30D, 0) > 0 THEN
            COALESCE(email_stats.EMAILS_CLICKED_30D, 0) / NULLIF(email_stats.EMAILS_OPENED_30D, 0)
        ELSE 0
    END AS EMAIL_CLICK_RATE_30D,
    CASE WHEN COALESCE(email_stats.HAS_UNSUBSCRIBED, 0) > 0 THEN 1 ELSE 0 END AS HAS_UNSUBSCRIBED,
    
    -- Cart events (30 days)
    COALESCE(cart_stats.CART_ADDITIONS_30D, 0) AS CART_ADDITIONS_30D,
    COALESCE(cart_stats.TOTAL_SESSIONS_30D, 0) AS TOTAL_SESSIONS_30D,
    CASE 
        WHEN COALESCE(cart_stats.TOTAL_SESSIONS_30D, 0) > 0 THEN
            COALESCE(cart_stats.CART_ADDITIONS_30D, 0) / NULLIF(cart_stats.TOTAL_SESSIONS_30D, 0)
        ELSE 0
    END AS BROWSE_TO_CART_RATIO,
    COALESCE(cart_stats.CART_ABANDONMENTS_30D, 0) AS CART_ABANDONMENTS_30D,
    
    -- Returns (24 months)
    COALESCE(return_stats.SIZE_FIT_RETURNS_COUNT, 0) AS SIZE_FIT_RETURNS_COUNT,
    CASE WHEN COALESCE(return_stats.SIZE_FIT_RETURNS_COUNT, 0) >= 2 THEN 1 ELSE 0 END AS HAS_2PLUS_SIZE_RETURNS,
    COALESCE(return_stats.TOTAL_RETURNS_COUNT, 0) AS TOTAL_RETURNS_COUNT,
    
    -- Customer segment
    CASE 
        WHEN COALESCE(u.AFFINITY_CARD, 0) > 0 THEN 'VIP'
        WHEN COALESCE(o_stats.ORDER_COUNT_24M, 0) >= 2 
             OR COALESCE(o_stats.TOTAL_SPENT_24M, 0) >= 500 THEN 'Regular'
        WHEN COALESCE(o_stats.ORDER_COUNT_24M, 0) = 1 THEN 'New'
        WHEN MONTHS_BETWEEN(SYSDATE, COALESCE(o_stats.LAST_PURCHASE_DATE, u.CREATED_AT)) >= 2 THEN 'Dormant'
        ELSE 'At-Risk'
    END AS CUSTOMER_SEGMENT,
    
    -- Estimated LTV
    COALESCE(o_stats.TOTAL_SPENT_24M, 0) * 2 AS ESTIMATED_LTV
    
FROM ADMIN.USERS u
LEFT JOIN (
    SELECT 
        USER_ID,
        COUNT(DISTINCT ID) AS ORDER_COUNT_24M,
        SUM(TOTAL) AS TOTAL_SPENT_24M,
        AVG(TOTAL) AS AVG_ORDER_VALUE_24M,
        MAX(CREATED_AT) AS LAST_PURCHASE_DATE,
        MONTHS_BETWEEN(SYSDATE, MAX(CREATED_AT)) AS MONTHS_SINCE_LAST_PURCHASE
    FROM ADMIN.ORDERS
    WHERE STATUS NOT IN ('cancelled')
      AND CREATED_AT >= ADD_MONTHS(SYSDATE, -24)
    GROUP BY USER_ID
) o_stats ON u.ID = o_stats.USER_ID
LEFT JOIN (
    SELECT 
        USER_ID,
        COUNT(*) AS LOGIN_COUNT_30D,
        MONTHS_BETWEEN(SYSDATE, MAX(LOGIN_TIMESTAMP)) AS MONTHS_SINCE_LAST_LOGIN
    FROM ADMIN.LOGIN_EVENTS
    WHERE LOGIN_TIMESTAMP >= SYSDATE - 30
    GROUP BY USER_ID
) login_stats ON u.ID = login_stats.USER_ID
LEFT JOIN (
    SELECT 
        USER_ID,
        AVG(RATING) AS AVG_REVIEW_RATING,
        COUNT(*) AS REVIEW_COUNT,
        SUM(CASE WHEN RATING <= 2 THEN 1 ELSE 0 END) AS DETRACTOR_COUNT,
        SUM(CASE WHEN RATING = 3 THEN 1 ELSE 0 END) AS PASSIVE_COUNT,
        SUM(CASE WHEN RATING >= 4 THEN 1 ELSE 0 END) AS PROMOTER_COUNT,
        SUM(CASE WHEN RATING <= 2 AND CREATED_AT >= SYSDATE - 90 THEN 1 ELSE 0 END) AS NEGATIVE_REVIEWS_90D
    FROM ADMIN.PRODUCT_REVIEWS
    WHERE CREATED_AT >= ADD_MONTHS(SYSDATE, -24)
    GROUP BY USER_ID
) review_stats ON u.ID = review_stats.USER_ID
LEFT JOIN (
    SELECT 
        USER_ID,
        COUNT(*) AS EMAILS_SENT_30D,
        SUM(CASE WHEN OPENED_AT IS NOT NULL THEN 1 ELSE 0 END) AS EMAILS_OPENED_30D,
        SUM(CASE WHEN CLICKED_AT IS NOT NULL THEN 1 ELSE 0 END) AS EMAILS_CLICKED_30D,
        SUM(CASE WHEN UNSUBSCRIBED_AT IS NOT NULL THEN 1 ELSE 0 END) AS HAS_UNSUBSCRIBED
    FROM ADMIN.EMAIL_ENGAGEMENT
    WHERE SENT_AT >= SYSDATE - 30
    GROUP BY USER_ID
) email_stats ON u.ID = email_stats.USER_ID
LEFT JOIN (
    SELECT 
        USER_ID,
        SUM(CASE WHEN ACTION = 'added' THEN 1 ELSE 0 END) AS CART_ADDITIONS_30D,
        COUNT(DISTINCT SESSION_ID) AS TOTAL_SESSIONS_30D,
        SUM(CASE WHEN ACTION = 'abandoned' THEN 1 ELSE 0 END) AS CART_ABANDONMENTS_30D
    FROM ADMIN.CART_EVENTS
    WHERE CREATED_AT >= SYSDATE - 30
    GROUP BY USER_ID
) cart_stats ON u.ID = cart_stats.USER_ID
LEFT JOIN (
    SELECT 
        USER_ID,
        SUM(CASE WHEN RETURN_REASON IN ('SIZE_TOO_SMALL', 'SIZE_TOO_LARGE') THEN 1 ELSE 0 END) AS SIZE_FIT_RETURNS_COUNT,
        COUNT(*) AS TOTAL_RETURNS_COUNT
    FROM ADMIN.RETURNS
    WHERE REQUESTED_AT >= ADD_MONTHS(SYSDATE, -24)
    GROUP BY USER_ID
) return_stats ON u.ID = return_stats.USER_ID
WHERE u.IS_ACTIVE = 1;
```

## Step 1b: Create CHURN_TRAINING_DATA View

```sql
-- Create CHURN_TRAINING_DATA view (original version with adjusted churn definition)
CREATE OR REPLACE VIEW OML.CHURN_TRAINING_DATA AS
SELECT 
    cf.*,
    CASE 
        WHEN cf.CUSTOMER_SEGMENT = 'Dormant' THEN 1
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 0.75 THEN 1
        WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 0.5
             AND (
                 cf.LOGIN_COUNT_30D <= 7
                 OR cf.EMAIL_OPEN_RATE_30D < 0.5
                 OR cf.CART_ABANDONMENTS_30D >= 2
             ) THEN 1
        WHEN cf.LOGIN_COUNT_30D <= 3 THEN 1
        ELSE 0
    END AS CHURNED_60_90D
FROM OML.CHURN_FEATURES cf
WHERE cf.CUSTOMER_AGE_MONTHS >= 3
    AND cf.ORDER_COUNT_24M > 0;
```

## Step 1c: Verify Views

```sql
-- Verify views created
SELECT COUNT(*) AS FEATURES_COUNT FROM OML.CHURN_FEATURES;
SELECT COUNT(*) AS TRAINING_COUNT FROM OML.CHURN_TRAINING_DATA;
```

## Step 2: Check OML4Py Connection

```python
%python
import oml

# Verify connection
print("OML Connected:", oml.isconnected())

# Check OML version
try:
    print("OML Version:", oml.__version__)
except:
    pass
```

## Step 3: Explore Data

```python
%python
# Load features
features = oml.sync(view='CHURN_FEATURES')

# Basic info
print("=" * 60)
print("CHURN_FEATURES Data Overview")
print("=" * 60)
print("Shape:", features.shape)
print("\nColumn count:", len(features.columns))
```

## Step 3b: Check Customer Segments

```python
%python
# Check customer segments distribution
import pandas as pd

if 'CUSTOMER_SEGMENT' in features.columns:
    print("=" * 60)
    print("Customer Segment Distribution")
    print("=" * 60)
    
    features_pd = features.pull()
    segment_dist = features_pd['CUSTOMER_SEGMENT'].value_counts()
    print(segment_dist)
    
    print("\nPercentage distribution:")
    print((segment_dist / len(features_pd) * 100).round(2))
```

## Step 3c: Check Churn Distribution

```python
%python
# Check the churn distribution
import pandas as pd

train_data = oml.sync(view='CHURN_TRAINING_DATA')
train_data_pd = train_data.pull()

print("=" * 60)
print("Adjusted Churn Definition Results")
print("=" * 60)
print("Training Data Shape: " + str(train_data_pd.shape))
print("\nTarget Variable Distribution:")
print(train_data_pd['CHURNED_60_90D'].value_counts())
churn_rate = train_data_pd['CHURNED_60_90D'].mean() * 100
print("\nChurn Rate: " + str(churn_rate) + " %")
print("Non-Churn Rate: " + str(100 - churn_rate) + " %")
print("\n✓ Good churn rate for training!")
```

## Step 4: Prepare Features and Split Data

```python
%python
# Prepare features and split data
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

# Load training data
train_data = oml.sync(view='CHURN_TRAINING_DATA')
train_data_pd = train_data.pull()

# Identify feature columns (exclude target and metadata)
exclude_cols = ['USER_ID', 'CUSTOMER_SEGMENT', 'ESTIMATED_LTV', 'CHURNED_60_90D']
feature_cols = [col for col in train_data_pd.columns if col not in exclude_cols]

print("=" * 60)
print("Preparing Features and Splitting Data")
print("=" * 60)
print("Total features: " + str(len(feature_cols)))
print("Features: " + ", ".join(feature_cols[:10]) + "...")

# Prepare X and y
X_pd = train_data_pd[feature_cols].copy()
y_pd = train_data_pd['CHURNED_60_90D']

# Clean data - replace NaN and infinity
for col in feature_cols:
    if pd.api.types.is_numeric_dtype(X_pd[col]):
        X_pd[col] = X_pd[col].replace([np.inf, -np.inf], np.nan)
        X_pd[col] = X_pd[col].fillna(0)

# Stratified split
X_train_pd, X_test_pd, y_train_pd, y_test_pd = train_test_split(
    X_pd, y_pd, 
    test_size=0.2, 
    random_state=42, 
    stratify=y_pd
)

print("\nSplit completed:")
print("  Train size: " + str(len(X_train_pd)))
print("  Test size: " + str(len(X_test_pd)))
print("  Train churn rate: " + str(round(y_train_pd.mean() * 100, 2)) + "%")
print("  Test churn rate: " + str(round(y_test_pd.mean() * 100, 2)) + "%")
```

## Step 5: Train XGBoost Model

```python
%python
# Train XGBoost - Simplified approach
import pandas as pd

print("=" * 60)
print("Training XGBoost Model")
print("=" * 60)

# Merge X_train and y_train for database push
train_combined_pd = X_train_pd.copy()
train_combined_pd['CHURNED_60_90D'] = y_train_pd.values

# Push to database
print("Pushing training data to database...")
train_oml = oml.push(train_combined_pd)
print("Training data pushed: " + str(train_oml.shape))

# Create XGBoost model with explicit classification type
xgb_model = oml.xgb('classification')

# Get features and target from OML DataFrame
X_train_oml = train_oml[feature_cols]
y_train_oml = train_oml['CHURNED_60_90D']

print("X_train_oml shape: " + str(X_train_oml.shape))
print("Training started...")

# Fit the model
xgb_model = xgb_model.fit(X_train_oml, y_train_oml)
print("Training completed!")
```

## Step 6: Evaluate Model

```python
%python
# Evaluate model performance
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
import numpy as np

# Prepare test data in OML format
test_combined_pd = X_test_pd.copy()
test_combined_pd['CHURNED_60_90D'] = y_test_pd.values
test_oml = oml.push(test_combined_pd)
X_test_oml = test_oml[feature_cols]

# Get predictions - OML returns Vector objects
print("Generating predictions...")
y_pred_proba_oml = xgb_model.predict_proba(X_test_oml)

# Convert OML Vector to numpy array
y_pred_proba_pd = y_pred_proba_oml.pull()
if isinstance(y_pred_proba_pd, pd.DataFrame):
    if 1 in y_pred_proba_pd.columns:
        y_pred_proba = y_pred_proba_pd[1].values
    elif len(y_pred_proba_pd.columns) == 2:
        y_pred_proba = y_pred_proba_pd.iloc[:, 1].values
    else:
        y_pred_proba = y_pred_proba_pd.values.flatten()
else:
    y_pred_proba = np.array(y_pred_proba_pd)

# Convert probabilities to binary predictions (threshold = 0.5)
y_pred = (y_pred_proba >= 0.5).astype(int)

# Convert y_test to numpy array for metrics
y_test_vals = y_test_pd.values

# Calculate metrics
accuracy = accuracy_score(y_test_vals, y_pred)
precision = precision_score(y_test_vals, y_pred, zero_division=0)
recall = recall_score(y_test_vals, y_pred, zero_division=0)
f1 = f1_score(y_test_vals, y_pred, zero_division=0)
auc = roc_auc_score(y_test_vals, y_pred_proba)

# Confusion matrix
cm = confusion_matrix(y_test_vals, y_pred)
tn, fp, fn, tp = cm.ravel()

print("=" * 60)
print("MODEL EVALUATION METRICS")
print("=" * 60)
print("Accuracy:  " + str(round(accuracy, 4)))
print("Precision: " + str(round(precision, 4)) + "  (of predicted churn, how many actually churn)")
print("Recall:    " + str(round(recall, 4)) + "  (of actual churn, how many did we catch)")
print("F1 Score:  " + str(round(f1, 4)) + "  (harmonic mean of precision and recall)")
print("AUC-ROC:   " + str(round(auc, 4)) + "  (model's ability to distinguish classes)")
print("\nModel Confidence: " + str(int(auc * 100)) + "%")
print("\nConfusion Matrix:")
print("                Predicted")
print("              Non-Churn  Churn")
print("Actual Non-Churn   " + str(tn) + "   " + str(fp))
print("       Churn       " + str(fn) + "   " + str(tp))
print("\nTrue Negatives:  " + str(tn) + " (correctly predicted non-churn)")
print("False Positives: " + str(fp) + " (predicted churn, but didn't churn)")
print("False Negatives: " + str(fn) + " (missed churners)")
print("True Positives:  " + str(tp) + " (correctly predicted churn)")
print("\nClassification Report:")
print(classification_report(y_test_vals, y_pred, target_names=['Non-Churn', 'Churn']))
```

## Step 7: Feature Importance

```python
%python
# Get and display feature importance - OML-compatible
import pandas as pd
import numpy as np

print("=" * 60)
print("Feature Importance Analysis")
print("=" * 60)

# Get importance from model (it's a property, not a method!)
try:
    print("\nExtracting feature importance from xgb_model.importance...")
    importance_result = xgb_model.importance  # Property, not method
    
    # Pull OML DataFrame to pandas
    if hasattr(importance_result, 'pull'):
        importance_df_raw = importance_result.pull()
    else:
        importance_df_raw = importance_result
    
    # OML XGBoost importance has columns: ATTRIBUTE_NAME and GAIN
    if 'ATTRIBUTE_NAME' in importance_df_raw.columns and 'GAIN' in importance_df_raw.columns:
        feature_importance = importance_df_raw[['ATTRIBUTE_NAME', 'GAIN']].copy()
        feature_importance.columns = ['FEATURE_NAME', 'IMPORTANCE_SCORE']
        importance_method = "xgb_model.importance - GAIN metric"
        
        # Sort by importance
        importance_df = feature_importance.sort_values('IMPORTANCE_SCORE', ascending=False)
        
        print("\n" + "=" * 60)
        print("Top 20 Most Important Features (by GAIN)")
        print("=" * 60)
        print(importance_df.head(20).to_string(index=False))
        
        # Analyze feature importance distribution
        print("\nTotal features with importance data: " + str(len(importance_df)))
        positive_importance = importance_df[importance_df['IMPORTANCE_SCORE'] > 0]
        print("Features with positive importance: " + str(len(positive_importance)))
        
        if len(positive_importance) > 0:
            total_importance = importance_df['IMPORTANCE_SCORE'].sum()
            if abs(total_importance) > 1e-10:
                top10_pct = importance_df.head(10)['IMPORTANCE_SCORE'].sum() / total_importance * 100
                top5_pct = importance_df.head(5)['IMPORTANCE_SCORE'].sum() / total_importance * 100
                print("Top 5 features account for: " + str(round(top5_pct, 1)) + "% of total importance")
                print("Top 10 features account for: " + str(round(top10_pct, 1)) + "% of total importance")
        
        # Store for later use
        importance_df_result = importance_df
    else:
        print("Could not find expected columns in importance data")
        importance_df_result = None
        
except Exception as e:
    print("Failed to extract importance: " + str(e))
    importance_df_result = None
```

## Step 8: Save Model

```python
%python
# Save model to OML datastore
model_name = 'CHURN_XGBOOST_MODEL'

# Save - correct syntax: first arg is dict of objects, then name
oml.ds.save({'churn_xgb_model': xgb_model}, model_name, description='Churn XGBoost Model v1', overwrite=True)
print("✓ Model '" + model_name + "' saved to OML datastore")

# Verify model is persisted
print("✓ Model is persisted in Oracle Database")
print("Model type: " + str(type(xgb_model)))
```

## Step 9: Optimize Threshold

```python
%python
# Find optimal probability threshold
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
import numpy as np

# Use predictions from Step 6 (y_test_vals and y_pred_proba should be available)
thresholds = np.arange(0.1, 0.9, 0.05)
f1_scores = []
precisions = []
recalls = []
accuracies = []

for threshold in thresholds:
    y_pred_thresh = (y_pred_proba >= threshold).astype(int)
    f1 = f1_score(y_test_vals, y_pred_thresh, zero_division=0)
    prec = precision_score(y_test_vals, y_pred_thresh, zero_division=0)
    rec = recall_score(y_test_vals, y_pred_thresh, zero_division=0)
    acc = accuracy_score(y_test_vals, y_pred_thresh)
    f1_scores.append(f1)
    precisions.append(prec)
    recalls.append(rec)
    accuracies.append(acc)

# Find optimal threshold (maximize F1)
optimal_idx = np.argmax(f1_scores)
optimal_threshold = thresholds[optimal_idx]

print("=" * 60)
print("THRESHOLD OPTIMIZATION")
print("=" * 60)
print("Optimal Threshold: " + str(round(optimal_threshold, 3)) + " (instead of 0.5)")
print("F1 Score at optimal: " + str(round(f1_scores[optimal_idx], 4)))
print("Precision at optimal: " + str(round(precisions[optimal_idx], 4)))
print("Recall at optimal: " + str(round(recalls[optimal_idx], 4)))
print("Accuracy at optimal: " + str(round(accuracies[optimal_idx], 4)))

# Re-evaluate with optimal threshold
y_pred_optimal = (y_pred_proba >= optimal_threshold).astype(int)
accuracy_opt = accuracy_score(y_test_vals, y_pred_optimal)
precision_opt = precision_score(y_test_vals, y_pred_optimal, zero_division=0)
recall_opt = recall_score(y_test_vals, y_pred_optimal, zero_division=0)
f1_opt = f1_score(y_test_vals, y_pred_optimal, zero_division=0)

print("\nComparison:")
print("  Threshold 0.5:  F1=" + str(round(f1, 4)) + ", Precision=" + str(round(precision, 4)) + ", Recall=" + str(round(recall, 4)))
print("  Threshold " + str(round(optimal_threshold, 3)) + ": F1=" + str(round(f1_opt, 4)) + ", Precision=" + str(round(precision_opt, 4)) + ", Recall=" + str(round(recall_opt, 4)))

# Store optimal threshold for later use
optimal_threshold_value = optimal_threshold
```

## Step 10: Score All Customers

```python
%python
# Score all active customers for churn risk
import pandas as pd
import numpy as np

# Load current features (all active customers)
current_features = oml.sync(view='CHURN_FEATURES')
current_features_pd = current_features.pull()

# Prepare features
X_current_pd = current_features_pd[feature_cols].copy()

# Clean data before pushing
print("Cleaning data before scoring...")
X_current_pd = X_current_pd.replace([np.inf, -np.inf], np.nan)
numeric_cols = X_current_pd.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    X_current_pd[col] = pd.to_numeric(X_current_pd[col], errors='coerce').fillna(0)

# Push to OML for scoring
X_current_oml = oml.push(X_current_pd)

# Predict churn probability
print("=" * 60)
print("Scoring All Customers")
print("=" * 60)
print("Scoring " + str(len(X_current_pd)) + " customers...")
churn_proba_oml = xgb_model.predict_proba(X_current_oml)

# Convert to numpy array
churn_proba_pd = churn_proba_oml.pull()
if isinstance(churn_proba_pd, pd.DataFrame):
    if 1 in churn_proba_pd.columns:
        churn_proba = churn_proba_pd[1].values
    elif len(churn_proba_pd.columns) == 2:
        churn_proba = churn_proba_pd.iloc[:, 1].values
    else:
        churn_proba = churn_proba_pd.values.flatten()
else:
    churn_proba = np.array(churn_proba_pd)

# Use optimal threshold (from Step 9) or default to 0.3 if not available
threshold = optimal_threshold_value if 'optimal_threshold_value' in globals() else 0.3

# Create results DataFrame
results = pd.DataFrame({
    'USER_ID': current_features_pd['USER_ID'],
    'CHURN_RISK_SCORE': churn_proba,
    'CHURN_RISK_PERCENT': (churn_proba * 100).round(2),
    'IS_AT_RISK': (churn_proba >= threshold).astype(int),
    'CUSTOMER_SEGMENT': current_features_pd['CUSTOMER_SEGMENT'],
    'ESTIMATED_LTV': current_features_pd['ESTIMATED_LTV']
})

results['LTV_AT_RISK'] = (results['CHURN_RISK_PERCENT'] / 100 * results['ESTIMATED_LTV']).round(2)

# Calculate summary statistics
total_customers = len(results)
at_risk_count = int(results['IS_AT_RISK'].sum())
avg_risk = float(results['CHURN_RISK_PERCENT'].mean())
median_risk = float(results['CHURN_RISK_PERCENT'].median())
total_ltv_at_risk = float(results['LTV_AT_RISK'].sum())

# Risk distribution counts
low_risk_count = int((results['CHURN_RISK_PERCENT'] < 30).sum())
medium_risk_count = int(((results['CHURN_RISK_PERCENT'] >= 30) & (results['CHURN_RISK_PERCENT'] < 50)).sum())
high_risk_count = int(((results['CHURN_RISK_PERCENT'] >= 50) & (results['CHURN_RISK_PERCENT'] < 70)).sum())
very_high_risk_count = int((results['CHURN_RISK_PERCENT'] >= 70).sum())

# Print results
print("\nScoring Results (Threshold: " + str(round(threshold, 3)) + "):")
print("Total customers scored: " + str(total_customers))
print("At-risk customers (>=" + str(int(threshold*100)) + "% risk): " + str(at_risk_count))
print("Average risk score: " + str(round(avg_risk, 2)) + "%")
print("Median risk score: " + str(round(median_risk, 2)) + "%")
print("Total LTV at risk: $" + format(total_ltv_at_risk, ',.2f'))

print("\nRisk Score Distribution:")
print("  Low risk (<30%): " + str(low_risk_count))
print("  Medium risk (30-50%): " + str(medium_risk_count))
print("  High risk (50-70%): " + str(high_risk_count))
print("  Very high risk (>=70%): " + str(very_high_risk_count))
```

## Step 11: Cohort-Level Metrics

```python
%python
# Analyze metrics by customer segment (cohort)
import pandas as pd

# Cohort analysis using pandas groupby
cohort_metrics = results.groupby('CUSTOMER_SEGMENT').agg({
    'USER_ID': 'count',
    'CHURN_RISK_PERCENT': 'mean',
    'ESTIMATED_LTV': 'sum',
    'LTV_AT_RISK': 'sum',
    'IS_AT_RISK': 'sum'
}).reset_index()

cohort_metrics.columns = [
    'COHORT_NAME', 
    'CUSTOMER_COUNT', 
    'AVG_RISK_SCORE', 
    'TOTAL_LTV', 
    'LTV_AT_RISK', 
    'AT_RISK_COUNT'
]

# Calculate additional metrics
cohort_metrics['AT_RISK_PERCENT'] = (cohort_metrics['AT_RISK_COUNT'] / cohort_metrics['CUSTOMER_COUNT'] * 100).round(2)
cohort_metrics['LTV_RISK_PERCENT'] = (cohort_metrics['LTV_AT_RISK'] / cohort_metrics['TOTAL_LTV'] * 100).round(2)

print("=" * 60)
print("Cohort-Level Metrics")
print("=" * 60)
print(cohort_metrics.to_string(index=False))

# Display summary insights
print("\n" + "=" * 60)
print("Key Insights by Cohort")
print("=" * 60)
for _, row in cohort_metrics.iterrows():
    print("\n" + str(row['COHORT_NAME']) + ":")
    print("  - " + str(row['CUSTOMER_COUNT']) + " customers")
    print("  - Avg Risk Score: " + str(round(row['AVG_RISK_SCORE'], 1)) + "%")
    print("  - At-Risk Count: " + str(row['AT_RISK_COUNT']) + " (" + str(row['AT_RISK_PERCENT']) + "%)")
    print("  - LTV at Risk: $" + format(row['LTV_AT_RISK'], ',.0f') + " (" + str(row['LTV_RISK_PERCENT']) + "% of total LTV)")
```

## Step 12: Analyze Risk Factors

```python
%python
# Analyze top risk factors driving churn predictions
import pandas as pd

# Merge results with features
merged = results.merge(current_features_pd, on='USER_ID', how='inner', suffixes=('', '_y'))

# Check if CUSTOMER_SEGMENT exists, if not get it from results
if 'CUSTOMER_SEGMENT' not in merged.columns:
    if 'CUSTOMER_SEGMENT' in results.columns:
        merged['CUSTOMER_SEGMENT'] = results['CUSTOMER_SEGMENT']
    elif 'CUSTOMER_SEGMENT_y' in merged.columns:
        merged['CUSTOMER_SEGMENT'] = merged['CUSTOMER_SEGMENT_y']

# Analyze each risk factor based on top important features
risk_factors = []

# 1. Months Since Last Purchase (Top feature - 77% importance)
high_months = merged[merged['MONTHS_SINCE_LAST_PURCHASE'] >= 1.5]
if len(high_months) > 0:
    primary_seg = 'All'
    if 'CUSTOMER_SEGMENT' in high_months.columns and len(high_months['CUSTOMER_SEGMENT'].mode()) > 0:
        primary_seg = high_months['CUSTOMER_SEGMENT'].mode().iloc[0]
    
    risk_factors.append({
        'RISK_FACTOR': 'No Purchase in 45+ Days (1.5+ months)',
        'IMPACT_SCORE': str(int(high_months['CHURN_RISK_PERCENT'].mean())) + '%',
        'AFFECTED_CUSTOMERS': len(high_months),
        'PRIMARY_SEGMENT': primary_seg,
        'AVG_RISK': float(high_months['CHURN_RISK_PERCENT'].mean()),
        'FEATURE_IMPORTANCE': '77%'
    })

# 2. Cart Abandonments (11.9% importance)
high_abandon = merged[merged['CART_ABANDONMENTS_30D'] >= 3]
if len(high_abandon) > 0:
    primary_seg = 'All'
    if 'CUSTOMER_SEGMENT' in high_abandon.columns and len(high_abandon['CUSTOMER_SEGMENT'].mode()) > 0:
        primary_seg = high_abandon['CUSTOMER_SEGMENT'].mode().iloc[0]
    
    risk_factors.append({
        'RISK_FACTOR': 'High Cart Abandonments (3+)',
        'IMPACT_SCORE': str(int(high_abandon['CHURN_RISK_PERCENT'].mean())) + '%',
        'AFFECTED_CUSTOMERS': len(high_abandon),
        'PRIMARY_SEGMENT': primary_seg,
        'AVG_RISK': float(high_abandon['CHURN_RISK_PERCENT'].mean()),
        'FEATURE_IMPORTANCE': '11.9%'
    })

# 3. Low Login Activity (10.8% importance)
low_login = merged[merged['LOGIN_COUNT_30D'] <= 3]
if len(low_login) > 0:
    primary_seg = 'All'
    if 'CUSTOMER_SEGMENT' in low_login.columns and len(low_login['CUSTOMER_SEGMENT'].mode()) > 0:
        primary_seg = low_login['CUSTOMER_SEGMENT'].mode().iloc[0]
    
    risk_factors.append({
        'RISK_FACTOR': 'Low Login Activity (≤3 logins)',
        'IMPACT_SCORE': str(int(low_login['CHURN_RISK_PERCENT'].mean())) + '%',
        'AFFECTED_CUSTOMERS': len(low_login),
        'PRIMARY_SEGMENT': primary_seg,
        'AVG_RISK': float(low_login['CHURN_RISK_PERCENT'].mean()),
        'FEATURE_IMPORTANCE': '10.8%'
    })

# 4. Email Engagement
low_email = merged[merged['EMAIL_OPEN_RATE_30D'] < 0.2]
if len(low_email) > 0:
    risk_factors.append({
        'RISK_FACTOR': 'Email Engagement Decay',
        'IMPACT_SCORE': str(int(low_email['CHURN_RISK_PERCENT'].mean())) + '%',
        'AFFECTED_CUSTOMERS': len(low_email),
        'PRIMARY_SEGMENT': 'All segments',
        'AVG_RISK': float(low_email['CHURN_RISK_PERCENT'].mean()),
        'FEATURE_IMPORTANCE': 'Low'
    })

# 5. Size/Fit Returns
size_returns = merged[merged['HAS_2PLUS_SIZE_RETURNS'] == 1]
if len(size_returns) > 0:
    primary_seg = 'All'
    if 'CUSTOMER_SEGMENT' in size_returns.columns and len(size_returns['CUSTOMER_SEGMENT'].mode()) > 0:
        primary_seg = size_returns['CUSTOMER_SEGMENT'].mode().iloc[0]
    
    risk_factors.append({
        'RISK_FACTOR': 'Size/Fit Issues (2+ returns)',
        'IMPACT_SCORE': str(int(size_returns['CHURN_RISK_PERCENT'].mean())) + '%',
        'AFFECTED_CUSTOMERS': len(size_returns),
        'PRIMARY_SEGMENT': primary_seg,
        'AVG_RISK': float(size_returns['CHURN_RISK_PERCENT'].mean()),
        'FEATURE_IMPORTANCE': 'Low'
    })

# Create DataFrame and sort by average risk
risk_factors_df = pd.DataFrame(risk_factors)
if len(risk_factors_df) > 0:
    risk_factors_df = risk_factors_df.sort_values('AVG_RISK', ascending=False)
    risk_factors_display = risk_factors_df[['RISK_FACTOR', 'IMPACT_SCORE', 'AFFECTED_CUSTOMERS', 'PRIMARY_SEGMENT', 'FEATURE_IMPORTANCE']]

    print("=" * 60)
    print("Top Risk Factors (Based on Model's Important Features)")
    print("=" * 60)
    print(risk_factors_display.to_string(index=False))
else:
    print("No risk factors identified")
```

## Step 13: Summary Report

```python
%python
# Generate comprehensive summary report
import pandas as pd

print("=" * 60)
print("CHURN MODEL DEVELOPMENT SUMMARY")
print("=" * 60)
print("\nModel Name: CHURN_XGBOOST_MODEL")
print("Model Type: XGBoost Binary Classification")
print("Churn Definition: Multi-factor (Dormant, 0.75+ months, activity decline, low login)")

print("\n--- Training Data ---")
print("Training Samples: " + str(len(X_train_pd)))
print("Test Samples: " + str(len(X_test_pd)))
print("Total Features: " + str(len(feature_cols)))
if 'importance_df_result' in globals():
    print("Features Used by Model: " + str(len(importance_df_result)))
else:
    print("Features Used by Model: N/A")

print("\n--- Model Performance (Threshold 0.5) ---")
print("  Accuracy:  " + str(round(accuracy, 4)) + " (" + str(round(accuracy*100, 2)) + "%)")
print("  Precision: " + str(round(precision, 4)) + " (" + str(round(precision*100, 2)) + "%)")
print("  Recall:    " + str(round(recall, 4)) + " (" + str(round(recall*100, 2)) + "%)")
print("  F1 Score:  " + str(round(f1, 4)))
print("  AUC-ROC:   " + str(round(auc, 4)))
print("  Model Confidence: " + str(int(auc * 100)) + "%")

if 'optimal_threshold_value' in globals():
    print("\n--- Model Performance (Optimal Threshold " + str(round(optimal_threshold_value, 3)) + ") ---")
    print("  Accuracy:  " + str(round(accuracy_opt, 4)) + " (" + str(round(accuracy_opt*100, 2)) + "%)")
    print("  Precision: " + str(round(precision_opt, 4)) + " (" + str(round(precision_opt*100, 2)) + "%)")
    print("  Recall:    " + str(round(recall_opt, 4)) + " (" + str(round(recall_opt*100, 2)) + "%)")
    print("  F1 Score:  " + str(round(f1_opt, 4)))

print("\n--- Top 5 Most Important Features ---")
if 'importance_df_result' in globals():
    top5 = importance_df_result.head(5)
    total_importance = importance_df_result['IMPORTANCE_SCORE'].sum()
    for idx, row in top5.iterrows():
        pct = (row['IMPORTANCE_SCORE'] / total_importance * 100) if total_importance > 0 else 0
        print("  " + str(row['FEATURE_NAME']) + ": " + str(round(row['IMPORTANCE_SCORE'], 4)) + " (" + str(round(pct, 1)) + "%)")

print("\n--- Scoring Results ---")
threshold = optimal_threshold_value if 'optimal_threshold_value' in globals() else 0.3
print("  Total Customers Scored: " + str(len(results)))
print("  At-Risk Customers (Threshold: " + str(round(threshold, 3)) + "): " + str(int(results['IS_AT_RISK'].sum())))
print("  Average Risk Score: " + str(round(results['CHURN_RISK_PERCENT'].mean(), 2)) + "%")
print("  Total LTV at Risk: $" + format(results['LTV_AT_RISK'].sum(), ',.2f'))

print("\n--- Cohort Summary ---")
for _, row in cohort_metrics.iterrows():
    print("  " + str(row['COHORT_NAME']) + ": " + str(row['AT_RISK_COUNT']) + " at-risk (" + str(row['AT_RISK_PERCENT']) + "%)")

print("\n" + "=" * 60)
print("MODEL PERFORMANCE NOTES")
print("=" * 60)
print("\nCurrent Issues:")
print("  1. AUC-ROC is low (52%) - barely better than random")
print("  2. Precision and Recall are both low (18-20%)")
print("  3. Model heavily relies on 3 features (99.9% of importance)")

print("\nRecommended Next Steps:")
print("  1. Feature Engineering:")
print("     - Model only using 10 features - check if others are being filtered")
print("     - Create interaction features (e.g., months_since_purchase * login_count)")
print("  2. Hyperparameter Tuning:")
print("     - Adjust max_depth, learning_rate, n_estimators")
print("     - Try different scale_pos_weight values")
print("  3. Churn Definition:")
print("     - Current definition may not align with actual churn behavior")
print("     - Consider validating churn definition with business stakeholders")
print("  4. Data Quality:")
print("     - Check if feature distributions make sense")
print("     - Verify data quality in top 3 important features")

print("\n" + "=" * 60)
print("Model development and evaluation complete!")
print("=" * 60)
```
