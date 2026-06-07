-- ============================================================================
-- E-Commerce / Churn Schema — PostgreSQL (OCI)
-- ============================================================================
-- Target: single schema `ecomm` (one database, one application user)
-- Source mapping: OML.* + AFFINITY_CARD from ADMIN.USERS (denormalized)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ecomm;

-- ============================================================================
-- user_profiles (+ affinity_card from ADMIN.USERS)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ecomm.user_profiles (
    user_id                     VARCHAR(36) PRIMARY KEY,
    age                         NUMERIC(5, 2),
    gender                      VARCHAR(20),
    country                     VARCHAR(50),
    city                        VARCHAR(50),
    membership_years            NUMERIC(5, 2),
    login_frequency             NUMERIC(5, 2),
    session_duration_avg        NUMERIC(5, 2),
    pages_per_session           NUMERIC(5, 2),
    cart_abandonment_rate       NUMERIC(5, 2),
    wishlist_items              NUMERIC(5, 2),
    total_purchases             INTEGER,
    average_order_value         NUMERIC(10, 2),
    days_since_last_purchase    INTEGER,
    discount_usage_rate         NUMERIC(5, 2),
    returns_rate                NUMERIC(5, 2),
    email_open_rate             NUMERIC(5, 2),
    customer_service_calls      INTEGER,
    product_reviews_written     INTEGER,
    social_media_engagement_score NUMERIC(5, 2),
    mobile_app_usage            NUMERIC(5, 2),
    payment_method_diversity    SMALLINT,
    lifetime_value              NUMERIC(10, 2),
    credit_balance              NUMERIC(10, 2),
    signup_quarter              VARCHAR(10),
    churned                     SMALLINT CHECK (churned IN (0, 1)),
    affinity_card               SMALLINT
);

COMMENT ON TABLE ecomm.user_profiles IS 'User features for churn; affinity_card merged from ADB ADMIN.USERS';

-- ============================================================================
-- churn_predictions
-- ============================================================================
CREATE TABLE IF NOT EXISTS ecomm.churn_predictions (
    user_id                     VARCHAR(36) PRIMARY KEY,
    predicted_churn_probability NUMERIC(5, 4) NOT NULL
        CHECK (predicted_churn_probability >= 0 AND predicted_churn_probability <= 1),
    predicted_churn_label       SMALLINT NOT NULL CHECK (predicted_churn_label IN (0, 1)),
    risk_score                  SMALLINT NOT NULL
        CHECK (risk_score >= 0 AND risk_score <= 100),
    model_version               VARCHAR(50) NOT NULL,
    prediction_date             TIMESTAMP NOT NULL,
    last_updated                TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score            NUMERIC(5, 4)
        CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- ============================================================================
-- model_registry
-- ============================================================================
CREATE TABLE IF NOT EXISTS ecomm.model_registry (
    model_id                    VARCHAR(50) PRIMARY KEY,
    model_name                  VARCHAR(100) NOT NULL,
    model_version               VARCHAR(50) NOT NULL,
    model_type                  VARCHAR(50) NOT NULL,
    model_file_path             VARCHAR(500) NOT NULL,
    metadata_file_path          VARCHAR(500),
    auc_score                   NUMERIC(5, 4),
    accuracy                    NUMERIC(5, 4),
    precision_score             NUMERIC(5, 4),
    recall_score                NUMERIC(5, 4),
    f1_score                    NUMERIC(5, 4),
    optimal_threshold           NUMERIC(5, 4),
    training_date               TIMESTAMP NOT NULL,
    training_duration_seconds   NUMERIC(10, 2),
    train_samples               INTEGER,
    test_samples                INTEGER,
    feature_count               SMALLINT,
    status                      VARCHAR(20) DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'DEPRECATED', 'ARCHIVED')),
    is_production               SMALLINT DEFAULT 0 CHECK (is_production IN (0, 1)),
    training_parameters         TEXT,
    notes                       VARCHAR(1000),
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- churn_dataset_training (Tier 2 — ML pipeline)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ecomm.churn_dataset_training (
    user_id                     VARCHAR(36) PRIMARY KEY,
    age                         NUMERIC(5, 2),
    gender                      VARCHAR(20),
    country                     VARCHAR(50),
    city                        VARCHAR(50),
    membership_years            NUMERIC(5, 2),
    login_frequency             NUMERIC(5, 2),
    session_duration_avg        NUMERIC(5, 2),
    pages_per_session           NUMERIC(5, 2),
    cart_abandonment_rate       NUMERIC(5, 2),
    wishlist_items              NUMERIC(5, 2),
    total_purchases             INTEGER,
    average_order_value         NUMERIC(10, 2),
    days_since_last_purchase    INTEGER,
    discount_usage_rate         NUMERIC(5, 2),
    returns_rate                NUMERIC(5, 2),
    email_open_rate             NUMERIC(5, 2),
    customer_service_calls      INTEGER,
    product_reviews_written     INTEGER,
    social_media_engagement_score NUMERIC(5, 2),
    mobile_app_usage            NUMERIC(5, 2),
    payment_method_diversity    SMALLINT,
    lifetime_value              NUMERIC(10, 2),
    credit_balance              NUMERIC(10, 2),
    signup_quarter              VARCHAR(10),
    churned                     SMALLINT NOT NULL CHECK (churned IN (0, 1))
);

-- ============================================================================
-- Indexes
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_user_profiles_lifetime_value
    ON ecomm.user_profiles (lifetime_value);
CREATE INDEX IF NOT EXISTS idx_user_profiles_days_since
    ON ecomm.user_profiles (days_since_last_purchase);
CREATE INDEX IF NOT EXISTS idx_user_profiles_affinity_card
    ON ecomm.user_profiles (affinity_card);

CREATE INDEX IF NOT EXISTS idx_churn_pred_label
    ON ecomm.churn_predictions (predicted_churn_label);
CREATE INDEX IF NOT EXISTS idx_churn_pred_risk
    ON ecomm.churn_predictions (risk_score);
CREATE INDEX IF NOT EXISTS idx_churn_pred_date
    ON ecomm.churn_predictions (prediction_date);
CREATE INDEX IF NOT EXISTS idx_churn_pred_model
    ON ecomm.churn_predictions (model_version);

CREATE INDEX IF NOT EXISTS idx_model_registry_name
    ON ecomm.model_registry (model_name);
CREATE INDEX IF NOT EXISTS idx_model_registry_version
    ON ecomm.model_registry (model_version);
CREATE INDEX IF NOT EXISTS idx_model_registry_status
    ON ecomm.model_registry (status);
CREATE INDEX IF NOT EXISTS idx_model_registry_production
    ON ecomm.model_registry (is_production);
CREATE INDEX IF NOT EXISTS idx_model_registry_date
    ON ecomm.model_registry (training_date);

CREATE INDEX IF NOT EXISTS idx_churn_training_churned
    ON ecomm.churn_dataset_training (churned);
