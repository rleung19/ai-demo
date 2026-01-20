-- ============================================================================
-- Feature Engineering Views for Churn Prediction Model
-- ============================================================================
-- Purpose: Create views for model training and scoring
-- Views:
--   1. CHURN_TRAINING_FEATURES - Features for training (excludes target)
--   2. CHURN_TRAINING_DATA - Features + target for training
--   3. CHURN_USER_FEATURES - Features for scoring actual users
--
-- Usage: Run this script as OML user in Oracle ADB Serverless
-- ============================================================================

-- ============================================================================
-- View 1: CHURN_TRAINING_FEATURES
-- ============================================================================
-- Purpose: Feature columns only (for model training)
-- Source: OML.CHURN_DATASET_TRAINING
-- Excludes: USER_ID, CHURNED (target label)

CREATE OR REPLACE VIEW OML.CHURN_TRAINING_FEATURES AS
SELECT 
    -- Demographics
    AGE,
    CASE 
        WHEN GENDER = 'Male' THEN 1
        WHEN GENDER = 'Female' THEN 2
        ELSE 0
    END AS GENDER_CODE,
    CASE 
        WHEN SIGNUP_QUARTER = 'Q1' THEN 1
        WHEN SIGNUP_QUARTER = 'Q2' THEN 2
        WHEN SIGNUP_QUARTER = 'Q3' THEN 3
        WHEN SIGNUP_QUARTER = 'Q4' THEN 4
        ELSE 0
    END AS SIGNUP_QUARTER_CODE,
    
    -- Membership
    MEMBERSHIP_YEARS,
    
    -- Engagement metrics
    LOGIN_FREQUENCY,
    SESSION_DURATION_AVG,
    PAGES_PER_SESSION,
    EMAIL_OPEN_RATE,
    SOCIAL_MEDIA_ENGAGEMENT_SCORE,
    MOBILE_APP_USAGE,
    
    -- Purchase behavior
    TOTAL_PURCHASES,
    AVERAGE_ORDER_VALUE,
    DAYS_SINCE_LAST_PURCHASE,
    LIFETIME_VALUE,
    
    -- Cart and wishlist
    CART_ABANDONMENT_RATE,
    WISHLIST_ITEMS,
    
    -- Customer service
    CUSTOMER_SERVICE_CALLS,
    RETURNS_RATE,
    PRODUCT_REVIEWS_WRITTEN,
    
    -- Financial
    DISCOUNT_USAGE_RATE,
    PAYMENT_METHOD_DIVERSITY,
    CREDIT_BALANCE
    
    -- Note: Excluding USER_ID (identifier) and CHURNED (target label)
    -- Note: Excluding COUNTRY, CITY (categorical, would need encoding)
FROM OML.CHURN_DATASET_TRAINING;

-- Note: COMMENT ON VIEW is not supported in Oracle, view purpose is documented above

-- ============================================================================
-- View 2: CHURN_TRAINING_DATA
-- ============================================================================
-- Purpose: Features + target label for training
-- Source: OML.CHURN_DATASET_TRAINING
-- Includes: All features + CHURNED (target)

CREATE OR REPLACE VIEW OML.CHURN_TRAINING_DATA AS
SELECT 
    USER_ID,
    -- All features from CHURN_TRAINING_FEATURES
    AGE,
    CASE 
        WHEN GENDER = 'Male' THEN 1
        WHEN GENDER = 'Female' THEN 2
        ELSE 0
    END AS GENDER_CODE,
    CASE 
        WHEN SIGNUP_QUARTER = 'Q1' THEN 1
        WHEN SIGNUP_QUARTER = 'Q2' THEN 2
        WHEN SIGNUP_QUARTER = 'Q3' THEN 3
        WHEN SIGNUP_QUARTER = 'Q4' THEN 4
        ELSE 0
    END AS SIGNUP_QUARTER_CODE,
    MEMBERSHIP_YEARS,
    LOGIN_FREQUENCY,
    SESSION_DURATION_AVG,
    PAGES_PER_SESSION,
    EMAIL_OPEN_RATE,
    SOCIAL_MEDIA_ENGAGEMENT_SCORE,
    MOBILE_APP_USAGE,
    TOTAL_PURCHASES,
    AVERAGE_ORDER_VALUE,
    DAYS_SINCE_LAST_PURCHASE,
    LIFETIME_VALUE,
    CART_ABANDONMENT_RATE,
    WISHLIST_ITEMS,
    CUSTOMER_SERVICE_CALLS,
    RETURNS_RATE,
    PRODUCT_REVIEWS_WRITTEN,
    DISCOUNT_USAGE_RATE,
    PAYMENT_METHOD_DIVERSITY,
    CREDIT_BALANCE,
    -- Target label
    CHURNED
FROM OML.CHURN_DATASET_TRAINING;

-- Note: COMMENT ON VIEW is not supported in Oracle, view purpose is documented above

-- ============================================================================
-- View 3: CHURN_USER_FEATURES
-- ============================================================================
-- Purpose: Features for scoring actual users
-- Source: OML.USER_PROFILES
-- Excludes: USER_ID (for joining), CHURNED (historical label, not prediction)

CREATE OR REPLACE VIEW OML.CHURN_USER_FEATURES AS
SELECT 
    USER_ID,
    -- All features (same as training)
    AGE,
    CASE 
        WHEN GENDER = 'Male' THEN 1
        WHEN GENDER = 'Female' THEN 2
        ELSE 0
    END AS GENDER_CODE,
    CASE 
        WHEN SIGNUP_QUARTER = 'Q1' THEN 1
        WHEN SIGNUP_QUARTER = 'Q2' THEN 2
        WHEN SIGNUP_QUARTER = 'Q3' THEN 3
        WHEN SIGNUP_QUARTER = 'Q4' THEN 4
        ELSE 0
    END AS SIGNUP_QUARTER_CODE,
    MEMBERSHIP_YEARS,
    LOGIN_FREQUENCY,
    SESSION_DURATION_AVG,
    PAGES_PER_SESSION,
    EMAIL_OPEN_RATE,
    SOCIAL_MEDIA_ENGAGEMENT_SCORE,
    MOBILE_APP_USAGE,
    TOTAL_PURCHASES,
    AVERAGE_ORDER_VALUE,
    DAYS_SINCE_LAST_PURCHASE,
    LIFETIME_VALUE,
    CART_ABANDONMENT_RATE,
    WISHLIST_ITEMS,
    CUSTOMER_SERVICE_CALLS,
    RETURNS_RATE,
    PRODUCT_REVIEWS_WRITTEN,
    DISCOUNT_USAGE_RATE,
    PAYMENT_METHOD_DIVERSITY,
    CREDIT_BALANCE
    -- Note: Excluding CHURNED (historical label, not used for prediction)
FROM OML.USER_PROFILES;

-- Note: COMMENT ON VIEW is not supported in Oracle, view purpose is documented above

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify views created
SELECT 
    VIEW_NAME,
    TEXT_LENGTH
FROM USER_VIEWS
WHERE VIEW_NAME IN (
    'CHURN_TRAINING_FEATURES',
    'CHURN_TRAINING_DATA',
    'CHURN_USER_FEATURES'
)
ORDER BY VIEW_NAME;

-- Test view row counts
SELECT 
    'CHURN_TRAINING_FEATURES' AS VIEW_NAME,
    COUNT(*) AS ROW_COUNT
FROM OML.CHURN_TRAINING_FEATURES
UNION ALL
SELECT 
    'CHURN_TRAINING_DATA' AS VIEW_NAME,
    COUNT(*) AS ROW_COUNT
FROM OML.CHURN_TRAINING_DATA
UNION ALL
SELECT 
    'CHURN_USER_FEATURES' AS VIEW_NAME,
    COUNT(*) AS ROW_COUNT
FROM OML.CHURN_USER_FEATURES;

-- ============================================================================
-- End of Feature Views Creation
-- ============================================================================
