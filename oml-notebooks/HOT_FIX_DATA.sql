-- ============================================================================
-- HOT FIX: Transform Existing Data to Have Realistic Churn Patterns
-- ============================================================================
-- This script fixes the existing data to have realistic patterns without
-- regenerating from scratch. Run these updates in order.
-- ============================================================================

-- ============================================================================
-- STEP 1: Fix Churn Patterns in CHURN_TRAINING_DATA
-- ============================================================================
-- This creates a corrected version of the training data with realistic patterns

CREATE OR REPLACE VIEW OML.CHURN_TRAINING_DATA_FIXED AS
SELECT 
    ctd.*,
    -- Fix MONTHS_SINCE_LAST_PURCHASE for churners (increase gap)
    CASE 
        WHEN ctd.CHURNED_60_90D = 1 THEN 
            LEAST(ctd.MONTHS_SINCE_LAST_PURCHASE * 2.0, 3.0)  -- Increase churners to 1.5-3.0
        ELSE 
            GREATEST(ctd.MONTHS_SINCE_LAST_PURCHASE * 0.8, 0.1)  -- Decrease non-churners to 0.1-0.4
    END AS MONTHS_SINCE_LAST_PURCHASE_FIXED,
    
    -- Fix LOGIN_COUNT_30D (CRITICAL - currently backwards!)
    CASE 
        WHEN ctd.CHURNED_60_90D = 1 THEN 
            GREATEST(ctd.LOGIN_COUNT_30D * 0.4, 2)  -- Churners: reduce to 2-5
        ELSE 
            ctd.LOGIN_COUNT_30D * 1.5  -- Non-churners: increase to 10-20
    END AS LOGIN_COUNT_30D_FIXED,
    
    -- Fix EMAIL_OPEN_RATE_30D (CRITICAL - currently identical!)
    CASE 
        WHEN ctd.CHURNED_60_90D = 1 THEN 
            GREATEST(ctd.EMAIL_OPEN_RATE_30D * 0.3, 0.2)  -- Churners: reduce to 0.2-0.4
        ELSE 
            LEAST(ctd.EMAIL_OPEN_RATE_30D * 0.75, 0.8)  -- Non-churners: reduce to 0.6-0.8
    END AS EMAIL_OPEN_RATE_30D_FIXED,
    
    -- Fix CART_ABANDONMENTS_30D (increase gap)
    CASE 
        WHEN ctd.CHURNED_60_90D = 1 THEN 
            ctd.CART_ABANDONMENTS_30D * 5.0  -- Churners: increase to 3-8
        ELSE 
            GREATEST(ctd.CART_ABANDONMENTS_30D * 0.5, 0)  -- Non-churners: reduce to 0-2
    END AS CART_ABANDONMENTS_30D_FIXED
    
FROM OML.CHURN_TRAINING_DATA ctd;

-- ============================================================================
-- STEP 2: Create Fixed CHURN_FEATURES View with Realistic Patterns
-- ============================================================================

CREATE OR REPLACE VIEW OML.CHURN_FEATURES_FIXED AS
SELECT 
    cf.*,
    -- Use fixed values from training data if available, otherwise keep original
    COALESCE(
        (SELECT MONTHS_SINCE_LAST_PURCHASE_FIXED 
         FROM OML.CHURN_TRAINING_DATA_FIXED 
         WHERE USER_ID = cf.USER_ID),
        cf.MONTHS_SINCE_LAST_PURCHASE
    ) AS MONTHS_SINCE_LAST_PURCHASE_FIXED,
    
    COALESCE(
        (SELECT LOGIN_COUNT_30D_FIXED 
         FROM OML.CHURN_TRAINING_DATA_FIXED 
         WHERE USER_ID = cf.USER_ID),
        CASE 
            WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 1.0 THEN 
                GREATEST(cf.LOGIN_COUNT_30D * 0.4, 2)  -- At-risk: reduce logins
            ELSE 
                cf.LOGIN_COUNT_30D * 1.5  -- Active: increase logins
        END
    ) AS LOGIN_COUNT_30D_FIXED,
    
    COALESCE(
        (SELECT EMAIL_OPEN_RATE_30D_FIXED 
         FROM OML.CHURN_TRAINING_DATA_FIXED 
         WHERE USER_ID = cf.USER_ID),
        CASE 
            WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 1.0 THEN 
                GREATEST(cf.EMAIL_OPEN_RATE_30D * 0.3, 0.2)  -- At-risk: reduce email
            ELSE 
                LEAST(cf.EMAIL_OPEN_RATE_30D * 0.75, 0.8)  -- Active: moderate email
        END
    ) AS EMAIL_OPEN_RATE_30D_FIXED,
    
    COALESCE(
        (SELECT CART_ABANDONMENTS_30D_FIXED 
         FROM OML.CHURN_TRAINING_DATA_FIXED 
         WHERE USER_ID = cf.USER_ID),
        CASE 
            WHEN cf.MONTHS_SINCE_LAST_PURCHASE >= 1.0 THEN 
                cf.CART_ABANDONMENTS_30D * 5.0  -- At-risk: increase abandons
            ELSE 
                GREATEST(cf.CART_ABANDONMENTS_30D * 0.5, 0)  -- Active: reduce abandons
        END
    ) AS CART_ABANDONMENTS_30D_FIXED
    
FROM OML.CHURN_FEATURES cf;

-- ============================================================================
-- STEP 3: Strengthen Correlations - Update Related Features Together
-- ============================================================================
-- This view enforces correlations between related features

CREATE OR REPLACE VIEW OML.CHURN_FEATURES_CORRELATED AS
SELECT 
    cff.*,
    
    -- Strengthen SPEND -> LOGIN correlation (should be ~0.5)
    -- High spenders should have more logins
    CASE 
        WHEN cff.TOTAL_SPENT_24M > 1500 THEN 
            LEAST(cff.LOGIN_COUNT_30D_FIXED * 1.3, 25)  -- High spenders: more logins
        WHEN cff.TOTAL_SPENT_24M > 800 THEN 
            cff.LOGIN_COUNT_30D_FIXED  -- Medium spenders: keep as is
        ELSE 
            GREATEST(cff.LOGIN_COUNT_30D_FIXED * 0.7, 2)  -- Low spenders: fewer logins
    END AS LOGIN_COUNT_30D_CORRELATED,
    
    -- Strengthen SPEND -> EMAIL correlation (should be ~0.5)
    -- High spenders should have better email engagement
    CASE 
        WHEN cff.TOTAL_SPENT_24M > 1500 THEN 
            LEAST(cff.EMAIL_OPEN_RATE_30D_FIXED * 1.2, 0.9)  -- High spenders: better email
        WHEN cff.TOTAL_SPENT_24M > 800 THEN 
            cff.EMAIL_OPEN_RATE_30D_FIXED  -- Medium spenders: keep as is
        ELSE 
            GREATEST(cff.EMAIL_OPEN_RATE_30D_FIXED * 0.8, 0.2)  -- Low spenders: worse email
    END AS EMAIL_OPEN_RATE_30D_CORRELATED,
    
    -- Strengthen RETURNS -> RATING correlation (should be ~-0.6)
    -- More returns should correlate with lower ratings
    CASE 
        WHEN cff.TOTAL_RETURNS_COUNT >= 3 THEN 
            GREATEST(cff.AVG_REVIEW_RATING - 1.5, 2.0)  -- High returns: lower ratings
        WHEN cff.TOTAL_RETURNS_COUNT >= 1 THEN 
            GREATEST(cff.AVG_REVIEW_RATING - 0.5, 3.0)  -- Some returns: moderate ratings
        ELSE 
            LEAST(cff.AVG_REVIEW_RATING + 0.3, 5.0)  -- No returns: higher ratings
    END AS AVG_REVIEW_RATING_CORRELATED,
    
    -- Strengthen ABANDON -> EMAIL correlation (should be ~-0.4, currently positive!)
    -- More abandons should correlate with LOWER email engagement
    CASE 
        WHEN cff.CART_ABANDONMENTS_30D_FIXED >= 5 THEN 
            GREATEST(cff.EMAIL_OPEN_RATE_30D_FIXED * 0.4, 0.1)  -- High abandons: low email
        WHEN cff.CART_ABANDONMENTS_30D_FIXED >= 2 THEN 
            cff.EMAIL_OPEN_RATE_30D_FIXED * 0.7  -- Medium abandons: moderate email
        ELSE 
            LEAST(cff.EMAIL_OPEN_RATE_30D_FIXED * 1.1, 0.9)  -- Low abandons: better email
    END AS EMAIL_OPEN_RATE_30D_ABANDON_CORRELATED
    
FROM OML.CHURN_FEATURES_FIXED cff;

-- ============================================================================
-- STEP 4: Create Final Fixed Training Data View
-- ============================================================================

CREATE OR REPLACE VIEW OML.CHURN_TRAINING_DATA_FINAL AS
SELECT 
    cfc.USER_ID,
    cfc.CUST_YEAR_OF_BIRTH,
    cfc.CUST_MARITAL_STATUS,
    cfc.CUST_INCOME_LEVEL,
    cfc.CUST_CREDIT_LIMIT,
    cfc.GENDER,
    cfc.EDUCATION,
    cfc.OCCUPATION,
    cfc.HOUSEHOLD_SIZE,
    cfc.YRS_RESIDENCE,
    cfc.AFFINITY_CARD,
    
    -- Use fixed/correlated values
    cfc.ORDER_COUNT_24M,
    cfc.TOTAL_SPENT_24M,
    cfc.AVG_ORDER_VALUE_24M,
    COALESCE(cfc.MONTHS_SINCE_LAST_PURCHASE_FIXED, cfc.MONTHS_SINCE_LAST_PURCHASE) AS MONTHS_SINCE_LAST_PURCHASE,
    cfc.CUSTOMER_AGE_MONTHS,
    cfc.PURCHASE_VELOCITY,
    
    -- Use correlated login count
    COALESCE(cfc.LOGIN_COUNT_30D_CORRELATED, cfc.LOGIN_COUNT_30D_FIXED, cfc.LOGIN_COUNT_30D) AS LOGIN_COUNT_30D,
    cfc.LOGIN_FREQUENCY_CATEGORY,
    cfc.MONTHS_SINCE_LAST_LOGIN,
    cfc.SUPPORT_TICKETS_24M,
    
    -- Use correlated ratings
    COALESCE(cfc.AVG_REVIEW_RATING_CORRELATED, cfc.AVG_REVIEW_RATING) AS AVG_REVIEW_RATING,
    cfc.REVIEW_COUNT,
    cfc.DETRACTOR_COUNT,
    cfc.PASSIVE_COUNT,
    cfc.PROMOTER_COUNT,
    cfc.NPS_SCORE,
    cfc.HAS_NEGATIVE_SENTIMENT,
    cfc.NEGATIVE_REVIEWS_90D,
    
    -- Use correlated email (prioritize abandon correlation)
    COALESCE(cfc.EMAIL_OPEN_RATE_30D_ABANDON_CORRELATED, 
             cfc.EMAIL_OPEN_RATE_30D_CORRELATED, 
             cfc.EMAIL_OPEN_RATE_30D_FIXED, 
             cfc.EMAIL_OPEN_RATE_30D) AS EMAIL_OPEN_RATE_30D,
    cfc.EMAILS_SENT_30D,
    cfc.EMAILS_OPENED_30D,
    cfc.EMAILS_CLICKED_30D,
    cfc.EMAIL_CLICK_RATE_30D,
    cfc.HAS_UNSUBSCRIBED,
    
    -- Use fixed cart abandons
    COALESCE(cfc.CART_ABANDONMENTS_30D_FIXED, cfc.CART_ABANDONMENTS_30D) AS CART_ABANDONMENTS_30D,
    cfc.CART_ADDITIONS_30D,
    cfc.TOTAL_SESSIONS_30D,
    cfc.BROWSE_TO_CART_RATIO,
    
    -- Keep returns as is (already correlated with ratings)
    cfc.SIZE_FIT_RETURNS_COUNT,
    cfc.HAS_2PLUS_SIZE_RETURNS,
    cfc.TOTAL_RETURNS_COUNT,
    
    cfc.CUSTOMER_SEGMENT,
    cfc.ESTIMATED_LTV,
    
    -- Keep original churn target
    ctd.CHURNED_60_90D
    
FROM OML.CHURN_FEATURES_CORRELATED cfc
INNER JOIN OML.CHURN_TRAINING_DATA ctd ON cfc.USER_ID = ctd.USER_ID
WHERE ctd.CUSTOMER_AGE_MONTHS >= 3
    AND ctd.ORDER_COUNT_24M > 0;

-- ============================================================================
-- STEP 5: Verification Queries
-- ============================================================================

-- Check if patterns are fixed
SELECT 
    'BEFORE FIX' as status,
    CHURNED_60_90D,
    ROUND(AVG(MONTHS_SINCE_LAST_PURCHASE), 2) as avg_months,
    ROUND(AVG(LOGIN_COUNT_30D), 2) as avg_logins,
    ROUND(AVG(EMAIL_OPEN_RATE_30D), 2) as avg_email,
    ROUND(AVG(CART_ABANDONMENTS_30D), 2) as avg_abandons
FROM OML.CHURN_TRAINING_DATA
GROUP BY CHURNED_60_90D
UNION ALL
SELECT 
    'AFTER FIX' as status,
    CHURNED_60_90D,
    ROUND(AVG(MONTHS_SINCE_LAST_PURCHASE), 2) as avg_months,
    ROUND(AVG(LOGIN_COUNT_30D), 2) as avg_logins,
    ROUND(AVG(EMAIL_OPEN_RATE_30D), 2) as avg_email,
    ROUND(AVG(CART_ABANDONMENTS_30D), 2) as avg_abandons
FROM OML.CHURN_TRAINING_DATA_FINAL
GROUP BY CHURNED_60_90D
ORDER BY status, CHURNED_60_90D;

-- Check correlations
SELECT 
    'CORRELATIONS AFTER FIX' as metric,
    ROUND(CORR(TOTAL_SPENT_24M, LOGIN_COUNT_30D), 3) as spend_login_corr,
    ROUND(CORR(TOTAL_SPENT_24M, EMAIL_OPEN_RATE_30D), 3) as spend_email_corr,
    ROUND(CORR(ORDER_COUNT_24M, LOGIN_COUNT_30D), 3) as orders_login_corr,
    ROUND(CORR(TOTAL_RETURNS_COUNT, AVG_REVIEW_RATING), 3) as returns_rating_corr,
    ROUND(CORR(CART_ABANDONMENTS_30D, EMAIL_OPEN_RATE_30D), 3) as abandon_email_corr
FROM OML.CHURN_FEATURES_CORRELATED;

-- ============================================================================
-- USAGE INSTRUCTIONS
-- ============================================================================
-- 1. Run all CREATE VIEW statements above
-- 2. Run verification queries to check improvements
-- 3. Update your notebook to use:
--    - OML.CHURN_FEATURES_CORRELATED instead of OML.CHURN_FEATURES
--    - OML.CHURN_TRAINING_DATA_FINAL instead of OML.CHURN_TRAINING_DATA
-- 4. Re-train your model and check AUC improvement
-- ============================================================================
