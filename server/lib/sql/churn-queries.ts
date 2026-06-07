import { isPostgresBackend } from '../db/backend';

const ORACLE_COHORT_ASSIGNMENTS = `
  WITH cohort_assignments AS (
    SELECT
      cp.USER_ID,
      cp.PREDICTED_CHURN_PROBABILITY,
      cp.PREDICTED_CHURN_LABEL,
      up.LIFETIME_VALUE,
      up.MEMBERSHIP_YEARS,
      up.TOTAL_PURCHASES,
      up.DAYS_SINCE_LAST_PURCHASE,
      up.LOGIN_FREQUENCY,
      up.EMAIL_OPEN_RATE,
      up.CART_ABANDONMENT_RATE,
      up.RETURNS_RATE,
      up.CUSTOMER_SERVICE_CALLS,
      au.AFFINITY_CARD,
      CASE
        WHEN up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1 THEN 'VIP'
        WHEN up.MEMBERSHIP_YEARS < 1 THEN 'New'
        WHEN up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0 THEN 'Dormant'
        WHEN up.TOTAL_PURCHASES >= 2
             AND up.DAYS_SINCE_LAST_PURCHASE <= 90
             AND up.LOGIN_FREQUENCY > 0 THEN 'Regular'
        ELSE 'Other'
      END AS cohort
    FROM OML.CHURN_PREDICTIONS cp
    JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
    JOIN ADMIN.USERS au ON up.USER_ID = au.ID
  )
`;

const POSTGRES_COHORT_ASSIGNMENTS = `
  WITH cohort_assignments AS (
    SELECT
      cp.user_id AS USER_ID,
      cp.predicted_churn_probability AS PREDICTED_CHURN_PROBABILITY,
      cp.predicted_churn_label AS PREDICTED_CHURN_LABEL,
      up.lifetime_value AS LIFETIME_VALUE,
      up.membership_years AS MEMBERSHIP_YEARS,
      up.total_purchases AS TOTAL_PURCHASES,
      up.days_since_last_purchase AS DAYS_SINCE_LAST_PURCHASE,
      up.login_frequency AS LOGIN_FREQUENCY,
      up.email_open_rate AS EMAIL_OPEN_RATE,
      up.cart_abandonment_rate AS CART_ABANDONMENT_RATE,
      up.returns_rate AS RETURNS_RATE,
      up.customer_service_calls AS CUSTOMER_SERVICE_CALLS,
      up.affinity_card AS AFFINITY_CARD,
      CASE
        WHEN up.lifetime_value > 5000 OR up.affinity_card = 1 THEN 'VIP'
        WHEN up.membership_years < 1 THEN 'New'
        WHEN up.days_since_last_purchase > 90 OR up.login_frequency = 0 THEN 'Dormant'
        WHEN up.total_purchases >= 2
             AND up.days_since_last_purchase <= 90
             AND up.login_frequency > 0 THEN 'Regular'
        ELSE 'Other'
      END AS cohort
    FROM ecomm.churn_predictions cp
    JOIN ecomm.user_profiles up ON cp.user_id = up.user_id
  )
`;

export function cohortAssignmentsCte(): string {
  return isPostgresBackend() ? POSTGRES_COHORT_ASSIGNMENTS : ORACLE_COHORT_ASSIGNMENTS;
}

export function summaryStatsQuery(): string {
  if (isPostgresBackend()) {
    return `
      SELECT
        COUNT(*)::bigint AS total_customers,
        SUM(CASE WHEN predicted_churn_label = 1 THEN 1 ELSE 0 END)::bigint AS at_risk_count,
        AVG(predicted_churn_probability) * 100 AS average_risk_score,
        SUM(CASE WHEN predicted_churn_label = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS at_risk_percentage
      FROM ecomm.churn_predictions
    `;
  }
  return `
    SELECT
      COUNT(*) AS total_customers,
      SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
      AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS average_risk_score,
      SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS at_risk_percentage
    FROM OML.CHURN_PREDICTIONS
  `;
}

export function summaryLtvQuery(): string {
  if (isPostgresBackend()) {
    return `
      SELECT
        SUM(CASE WHEN cp.predicted_churn_label = 1 THEN up.lifetime_value ELSE 0 END) AS total_ltv_at_risk
      FROM ecomm.churn_predictions cp
      INNER JOIN ecomm.user_profiles up ON cp.user_id = up.user_id
    `;
  }
  return `
    SELECT
      SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END) AS total_ltv_at_risk
    FROM OML.CHURN_PREDICTIONS cp
    INNER JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
  `;
}

export function activeModelQuery(): string {
  if (isPostgresBackend()) {
    return `
      SELECT
        model_version AS MODEL_VERSION,
        auc_score AS model_confidence,
        training_date AS last_update
      FROM ecomm.model_registry
      WHERE status = 'ACTIVE'
      ORDER BY training_date DESC
      LIMIT 1
    `;
  }
  return `
    SELECT
      MODEL_VERSION,
      AUC_SCORE AS model_confidence,
      TRAINING_DATE AS last_update
    FROM OML.MODEL_REGISTRY
    WHERE STATUS = 'ACTIVE'
    ORDER BY TRAINING_DATE DESC
    FETCH FIRST 1 ROW ONLY
  `;
}

export function cohortsListQuery(): string {
  return `
    ${cohortAssignmentsCte()}
    SELECT
      cohort,
      COUNT(*) AS customer_count,
      SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
      ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
      ROUND(
        AVG(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN PREDICTED_CHURN_PROBABILITY END) * 100,
        2
      ) AS avg_risk_score_at_risk,
      SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
    FROM cohort_assignments
    WHERE cohort != 'Other'
    GROUP BY cohort
    ORDER BY
      CASE cohort
        WHEN 'VIP' THEN 1
        WHEN 'Regular' THEN 2
        WHEN 'New' THEN 3
        WHEN 'Dormant' THEN 4
        ELSE 5
      END
  `;
}

export function cohortDetailSummaryQuery(): string {
  return `
    ${cohortAssignmentsCte()}
    SELECT
      COUNT(*) AS customer_count,
      SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
      ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
      SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END) AS ltv_at_risk
    FROM cohort_assignments
    WHERE UPPER(cohort) = :cohortName
  `;
}

export function cohortDetailUsersQuery(
  whereClauses: string[],
  orderBy: string,
  withPagination: boolean
): string {
  const pagination = withPagination
    ? isPostgresBackend()
      ? ' LIMIT :limit OFFSET :offset'
      : ' OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY'
    : '';

  return `
    ${cohortAssignmentsCte()}
    SELECT
      USER_ID,
      PREDICTED_CHURN_PROBABILITY,
      LIFETIME_VALUE,
      COUNT(*) OVER() AS total_count
    FROM cohort_assignments
    WHERE ${whereClauses.join('\n      AND ')}
    ${orderBy}${pagination}
  `;
}

export function metricsQuery(): string {
  if (isPostgresBackend()) {
    return `
      SELECT
        model_id AS MODEL_ID,
        model_name AS MODEL_NAME,
        model_version AS MODEL_VERSION,
        model_type AS MODEL_TYPE,
        auc_score AS AUC_SCORE,
        accuracy AS ACCURACY,
        precision_score AS PRECISION_SCORE,
        recall_score AS RECALL_SCORE,
        f1_score AS F1_SCORE,
        optimal_threshold AS OPTIMAL_THRESHOLD,
        training_date AS TRAINING_DATE,
        train_samples AS TRAIN_SAMPLES,
        test_samples AS TEST_SAMPLES,
        feature_count AS FEATURE_COUNT,
        status AS STATUS
      FROM ecomm.model_registry
      WHERE status = 'ACTIVE'
      ORDER BY training_date DESC
      LIMIT 1
    `;
  }
  return `
    SELECT
      MODEL_ID,
      MODEL_NAME,
      MODEL_VERSION,
      MODEL_TYPE,
      AUC_SCORE,
      ACCURACY,
      PRECISION_SCORE,
      RECALL_SCORE,
      F1_SCORE,
      OPTIMAL_THRESHOLD,
      TRAINING_DATE,
      TRAIN_SAMPLES,
      TEST_SAMPLES,
      FEATURE_COUNT,
      STATUS
    FROM OML.MODEL_REGISTRY
    WHERE STATUS = 'ACTIVE'
    ORDER BY TRAINING_DATE DESC
    FETCH FIRST 1 ROW ONLY
  `;
}

export function chartDistributionQuery(): string {
  const bucketCase = isPostgresBackend()
    ? `CASE
        WHEN predicted_churn_probability < 0.1 THEN '< 10%'
        WHEN predicted_churn_probability < 0.2 THEN '10-20%'
        WHEN predicted_churn_probability < 0.3 THEN '20-30%'
        WHEN predicted_churn_probability < 0.4 THEN '30-40%'
        WHEN predicted_churn_probability < 0.5 THEN '40-50%'
        WHEN predicted_churn_probability < 0.6 THEN '50-60%'
        WHEN predicted_churn_probability < 0.7 THEN '60-70%'
        WHEN predicted_churn_probability < 0.8 THEN '70-80%'
        WHEN predicted_churn_probability < 0.9 THEN '80-90%'
        ELSE '>= 90%'
      END`
    : `CASE
        WHEN PREDICTED_CHURN_PROBABILITY < 0.1 THEN '< 10%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.2 THEN '10-20%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.3 THEN '20-30%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.4 THEN '30-40%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.5 THEN '40-50%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.6 THEN '50-60%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.7 THEN '60-70%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.8 THEN '70-80%'
        WHEN PREDICTED_CHURN_PROBABILITY < 0.9 THEN '80-90%'
        ELSE '>= 90%'
      END`;

  const table = isPostgresBackend() ? 'ecomm.churn_predictions' : 'OML.CHURN_PREDICTIONS';
  const probCol = isPostgresBackend() ? 'predicted_churn_probability' : 'PREDICTED_CHURN_PROBABILITY';
  const labelCol = isPostgresBackend() ? 'predicted_churn_label' : 'PREDICTED_CHURN_LABEL';

  return `
    SELECT
      ${bucketCase} AS risk_range,
      COUNT(*) AS customer_count,
      SUM(CASE WHEN ${labelCol} = 1 THEN 1 ELSE 0 END) AS at_risk_count
    FROM ${table}
    GROUP BY ${bucketCase}
    ORDER BY MIN(${probCol})
  `;
}

function riskFactorSegmentSubquery(whereClause: string): string {
  if (isPostgresBackend()) {
    return `
      SELECT string_agg(cohort, ', ' ORDER BY cnt DESC) AS primary_segment
      FROM (
        SELECT cohort, COUNT(*) AS cnt
        FROM cohort_assignments
        WHERE ${whereClause} AND cohort != 'Other'
        GROUP BY cohort
        ORDER BY cnt DESC
        LIMIT 2
      ) top_cohorts
    `;
  }
  return `
    SELECT LISTAGG(cohort, ', ') WITHIN GROUP (ORDER BY cnt DESC) AS primary_segment
    FROM (
      SELECT cohort, COUNT(*) AS cnt
      FROM cohort_assignments
      WHERE ${whereClause} AND cohort != 'Other'
      GROUP BY cohort
      ORDER BY cnt DESC
      FETCH FIRST 2 ROWS ONLY
    )
  `;
}

export function riskFactorQuery(
  label: string,
  whereClause: string,
  cteSuffix: string
): string {
  return `
    ${cohortAssignmentsCte()}
    , affected_${cteSuffix} AS (
      SELECT
        COUNT(*) AS affected_customers,
        ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 1) AS impact_score
      FROM cohort_assignments
      WHERE ${whereClause} AND cohort != 'Other'
    ),
    ${cteSuffix}_segments AS (
      ${riskFactorSegmentSubquery(whereClause)}
    )
    SELECT
      '${label}' AS risk_factor,
      ae.affected_customers,
      ae.impact_score,
      COALESCE(es.primary_segment, 'All segments') AS primary_segment
    FROM affected_${cteSuffix} ae
    CROSS JOIN ${cteSuffix}_segments es
  `;
}

export const RISK_FACTOR_QUERIES = [
  {
    query: () =>
      riskFactorQuery('Email open rate < 20%', 'EMAIL_OPEN_RATE < 20', 'email'),
  },
  {
    query: () =>
      riskFactorQuery('No Purchase in 45+ Days', 'DAYS_SINCE_LAST_PURCHASE > 45', 'no_purchase'),
  },
  {
    query: () =>
      riskFactorQuery('Cart abandonment rate > 50%', 'CART_ABANDONMENT_RATE > 50', 'cart'),
  },
  {
    query: () =>
      riskFactorQuery('Returns rate > 20%', 'RETURNS_RATE > 20', 'returns'),
  },
  {
    query: () =>
      riskFactorQuery('Customer service calls > 2', 'CUSTOMER_SERVICE_CALLS > 2', 'support'),
  },
];

export function isDatabaseError(message: string): boolean {
  return (
    message.includes('ORA-') ||
    message.includes('database') ||
    message.includes('ECONNREFUSED') ||
    message.includes('Connection terminated') ||
    message.includes('password authentication failed') ||
    message.includes('connect ETIMEDOUT')
  );
}
