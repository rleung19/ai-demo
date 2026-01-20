-- ============================================================================
-- Churn Prediction Model - Database Schema Creation
-- ============================================================================
-- Purpose: Create tables for churn prediction model in OML schema
-- Tables:
--   1. CHURN_DATASET_TRAINING - Training data (45,858 rows)
--   2. USER_PROFILES - Input features for actual users (4,142 rows)
--   3. CHURN_PREDICTIONS - Model predictions/output (4,142 rows)
--
-- Usage: Run this script as OML user in Oracle ADB Serverless
-- ============================================================================

-- ============================================================================
-- Table 1: CHURN_DATASET_TRAINING
-- ============================================================================
-- Purpose: Store training data for model training
-- Source: data/processed/churn_dataset_training.csv
-- Rows: 45,858
-- USER_ID: Placeholder IDs (TRAIN_1, TRAIN_2, etc.)

CREATE TABLE OML.CHURN_DATASET_TRAINING (
    USER_ID VARCHAR2(36) NOT NULL,
    AGE NUMBER(5,2),
    GENDER VARCHAR2(20),
    COUNTRY VARCHAR2(50),
    CITY VARCHAR2(50),
    MEMBERSHIP_YEARS NUMBER(5,2),
    LOGIN_FREQUENCY NUMBER(5,2),
    SESSION_DURATION_AVG NUMBER(5,2),
    PAGES_PER_SESSION NUMBER(5,2),
    CART_ABANDONMENT_RATE NUMBER(5,2),
    WISHLIST_ITEMS NUMBER(5,2),
    TOTAL_PURCHASES NUMBER(10),
    AVERAGE_ORDER_VALUE NUMBER(10,2),
    DAYS_SINCE_LAST_PURCHASE NUMBER(5),
    DISCOUNT_USAGE_RATE NUMBER(5,2),
    RETURNS_RATE NUMBER(5,2),
    EMAIL_OPEN_RATE NUMBER(5,2),
    CUSTOMER_SERVICE_CALLS NUMBER(5),
    PRODUCT_REVIEWS_WRITTEN NUMBER(5),
    SOCIAL_MEDIA_ENGAGEMENT_SCORE NUMBER(5,2),
    MOBILE_APP_USAGE NUMBER(5,2),
    PAYMENT_METHOD_DIVERSITY NUMBER(2),
    LIFETIME_VALUE NUMBER(10,2),
    CREDIT_BALANCE NUMBER(10,2),
    SIGNUP_QUARTER VARCHAR2(10),
    CHURNED NUMBER(1) NOT NULL,
    CONSTRAINT CHK_CHURNED CHECK (CHURNED IN (0, 1)),
    CONSTRAINT PK_CHURN_TRAINING PRIMARY KEY (USER_ID)
);

COMMENT ON TABLE OML.CHURN_DATASET_TRAINING IS 'Training data for churn prediction model (45,858 rows)';
COMMENT ON COLUMN OML.CHURN_DATASET_TRAINING.USER_ID IS 'Placeholder ID (TRAIN_1, TRAIN_2, etc.)';
COMMENT ON COLUMN OML.CHURN_DATASET_TRAINING.CHURNED IS 'Historical churn label: 0 = retained, 1 = churned';

-- ============================================================================
-- Table 2: USER_PROFILES
-- ============================================================================
-- Purpose: Store input features for churn prediction on actual users
-- Source: data/processed/churn_dataset_mapped.csv
-- Rows: 4,142
-- USER_ID: Real UUIDs from ADMIN.USERS.ID
-- Note: Contains features only (input to model), NOT predictions

CREATE TABLE OML.USER_PROFILES (
    USER_ID VARCHAR2(36) NOT NULL,
    AGE NUMBER(5,2),
    GENDER VARCHAR2(20),
    COUNTRY VARCHAR2(50),
    CITY VARCHAR2(50),
    MEMBERSHIP_YEARS NUMBER(5,2),
    LOGIN_FREQUENCY NUMBER(5,2),
    SESSION_DURATION_AVG NUMBER(5,2),
    PAGES_PER_SESSION NUMBER(5,2),
    CART_ABANDONMENT_RATE NUMBER(5,2),
    WISHLIST_ITEMS NUMBER(5,2),
    TOTAL_PURCHASES NUMBER(10),
    AVERAGE_ORDER_VALUE NUMBER(10,2),
    DAYS_SINCE_LAST_PURCHASE NUMBER(5),
    DISCOUNT_USAGE_RATE NUMBER(5,2),
    RETURNS_RATE NUMBER(5,2),
    EMAIL_OPEN_RATE NUMBER(5,2),
    CUSTOMER_SERVICE_CALLS NUMBER(5),
    PRODUCT_REVIEWS_WRITTEN NUMBER(5),
    SOCIAL_MEDIA_ENGAGEMENT_SCORE NUMBER(5,2),
    MOBILE_APP_USAGE NUMBER(5,2),
    PAYMENT_METHOD_DIVERSITY NUMBER(2),
    LIFETIME_VALUE NUMBER(10,2),
    CREDIT_BALANCE NUMBER(10,2),
    SIGNUP_QUARTER VARCHAR2(10),
    CHURNED NUMBER(1),
    CONSTRAINT CHK_USER_PROFILES_CHURNED CHECK (CHURNED IN (0, 1)),
    CONSTRAINT PK_USER_PROFILES PRIMARY KEY (USER_ID)
);

COMMENT ON TABLE OML.USER_PROFILES IS 'Input features for churn prediction on actual users (4,142 rows). Contains features only, NOT predictions.';
COMMENT ON COLUMN OML.USER_PROFILES.USER_ID IS 'Real UUID from ADMIN.USERS.ID';
COMMENT ON COLUMN OML.USER_PROFILES.CHURNED IS 'Historical churn label (for reference only), NOT the prediction';

-- ============================================================================
-- Table 3: CHURN_PREDICTIONS
-- ============================================================================
-- Purpose: Store predicted churn scores produced by the ML model
-- Rows: One per user (matches USER_PROFILES)
-- USER_ID: Real UUIDs from ADMIN.USERS.ID
-- Note: This is the OUTPUT from the model, not input features

CREATE TABLE OML.CHURN_PREDICTIONS (
    USER_ID VARCHAR2(36) NOT NULL,
    PREDICTED_CHURN_PROBABILITY NUMBER(5,4) NOT NULL,
    PREDICTED_CHURN_LABEL NUMBER(1) NOT NULL,
    RISK_SCORE NUMBER(3) NOT NULL,
    MODEL_VERSION VARCHAR2(50) NOT NULL,
    PREDICTION_DATE TIMESTAMP NOT NULL,
    LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONFIDENCE_SCORE NUMBER(5,4),
    CONSTRAINT CHK_PREDICTED_LABEL CHECK (PREDICTED_CHURN_LABEL IN (0, 1)),
    CONSTRAINT CHK_PROBABILITY CHECK (PREDICTED_CHURN_PROBABILITY >= 0 AND PREDICTED_CHURN_PROBABILITY <= 1),
    CONSTRAINT CHK_RISK_SCORE CHECK (RISK_SCORE >= 0 AND RISK_SCORE <= 100),
    CONSTRAINT CHK_CONFIDENCE CHECK (CONFIDENCE_SCORE IS NULL OR (CONFIDENCE_SCORE >= 0 AND CONFIDENCE_SCORE <= 1)),
    CONSTRAINT PK_CHURN_PREDICTIONS PRIMARY KEY (USER_ID)
);

COMMENT ON TABLE OML.CHURN_PREDICTIONS IS 'Predicted churn scores from ML model (output, not input features)';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.USER_ID IS 'Real UUID from ADMIN.USERS.ID';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.PREDICTED_CHURN_PROBABILITY IS 'Churn probability (0.0 to 1.0)';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.PREDICTED_CHURN_LABEL IS 'Binary prediction: 0 = retained, 1 = churned';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.RISK_SCORE IS 'Risk score (0-100) for display';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.MODEL_VERSION IS 'Version of model used for prediction';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.PREDICTION_DATE IS 'When prediction was made';
COMMENT ON COLUMN OML.CHURN_PREDICTIONS.CONFIDENCE_SCORE IS 'Model confidence (optional)';

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Indexes for CHURN_DATASET_TRAINING
CREATE INDEX IDX_CHURN_TRAINING_CHURNED ON OML.CHURN_DATASET_TRAINING(CHURNED);

-- Indexes for USER_PROFILES
CREATE INDEX IDX_USER_PROFILES_LIFETIME_VALUE ON OML.USER_PROFILES(LIFETIME_VALUE);
CREATE INDEX IDX_USER_PROFILES_DAYS_SINCE ON OML.USER_PROFILES(DAYS_SINCE_LAST_PURCHASE);

-- Indexes for CHURN_PREDICTIONS
CREATE INDEX IDX_CHURN_PRED_LABEL ON OML.CHURN_PREDICTIONS(PREDICTED_CHURN_LABEL);
CREATE INDEX IDX_CHURN_PRED_RISK ON OML.CHURN_PREDICTIONS(RISK_SCORE);
CREATE INDEX IDX_CHURN_PRED_DATE ON OML.CHURN_PREDICTIONS(PREDICTION_DATE);
CREATE INDEX IDX_CHURN_PRED_MODEL ON OML.CHURN_PREDICTIONS(MODEL_VERSION);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify tables created
SELECT 
    TABLE_NAME,
    NUM_ROWS,
    LAST_ANALYZED
FROM USER_TABLES
WHERE TABLE_NAME IN (
    'CHURN_DATASET_TRAINING',
    'USER_PROFILES',
    'CHURN_PREDICTIONS'
)
ORDER BY TABLE_NAME;

-- Verify constraints
SELECT 
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE,
    TABLE_NAME
FROM USER_CONSTRAINTS
WHERE TABLE_NAME IN (
    'CHURN_DATASET_TRAINING',
    'USER_PROFILES',
    'CHURN_PREDICTIONS'
)
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- ============================================================================
-- End of Schema Creation
-- ============================================================================
