-- ============================================================================
-- Feature views — ported from sql/create_feature_views.sql (Oracle OML)
-- ============================================================================

CREATE OR REPLACE VIEW ecomm.churn_training_features AS
SELECT
    age,
    CASE
        WHEN gender = 'Male' THEN 1
        WHEN gender = 'Female' THEN 2
        ELSE 0
    END AS gender_code,
    CASE
        WHEN signup_quarter = 'Q1' THEN 1
        WHEN signup_quarter = 'Q2' THEN 2
        WHEN signup_quarter = 'Q3' THEN 3
        WHEN signup_quarter = 'Q4' THEN 4
        ELSE 0
    END AS signup_quarter_code,
    membership_years,
    login_frequency,
    session_duration_avg,
    pages_per_session,
    email_open_rate,
    social_media_engagement_score,
    mobile_app_usage,
    total_purchases,
    average_order_value,
    days_since_last_purchase,
    lifetime_value,
    cart_abandonment_rate,
    wishlist_items,
    customer_service_calls,
    returns_rate,
    product_reviews_written,
    discount_usage_rate,
    payment_method_diversity,
    credit_balance
FROM ecomm.churn_dataset_training;

CREATE OR REPLACE VIEW ecomm.churn_training_data AS
SELECT
    user_id,
    age,
    CASE
        WHEN gender = 'Male' THEN 1
        WHEN gender = 'Female' THEN 2
        ELSE 0
    END AS gender_code,
    CASE
        WHEN signup_quarter = 'Q1' THEN 1
        WHEN signup_quarter = 'Q2' THEN 2
        WHEN signup_quarter = 'Q3' THEN 3
        WHEN signup_quarter = 'Q4' THEN 4
        ELSE 0
    END AS signup_quarter_code,
    membership_years,
    login_frequency,
    session_duration_avg,
    pages_per_session,
    email_open_rate,
    social_media_engagement_score,
    mobile_app_usage,
    total_purchases,
    average_order_value,
    days_since_last_purchase,
    lifetime_value,
    cart_abandonment_rate,
    wishlist_items,
    customer_service_calls,
    returns_rate,
    product_reviews_written,
    discount_usage_rate,
    payment_method_diversity,
    credit_balance,
    churned
FROM ecomm.churn_dataset_training;

CREATE OR REPLACE VIEW ecomm.churn_user_features AS
SELECT
    user_id,
    age,
    CASE
        WHEN gender = 'Male' THEN 1
        WHEN gender = 'Female' THEN 2
        ELSE 0
    END AS gender_code,
    CASE
        WHEN signup_quarter = 'Q1' THEN 1
        WHEN signup_quarter = 'Q2' THEN 2
        WHEN signup_quarter = 'Q3' THEN 3
        WHEN signup_quarter = 'Q4' THEN 4
        ELSE 0
    END AS signup_quarter_code,
    membership_years,
    login_frequency,
    session_duration_avg,
    pages_per_session,
    email_open_rate,
    social_media_engagement_score,
    mobile_app_usage,
    total_purchases,
    average_order_value,
    days_since_last_purchase,
    lifetime_value,
    cart_abandonment_rate,
    wishlist_items,
    customer_service_calls,
    returns_rate,
    product_reviews_written,
    discount_usage_rate,
    payment_method_diversity,
    credit_balance
FROM ecomm.user_profiles;
