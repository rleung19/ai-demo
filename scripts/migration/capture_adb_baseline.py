#!/usr/bin/env python3
"""Capture ADB row counts and API-equivalent aggregates for migration parity checks."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from db_utils import connect_adb, load_env  # noqa: E402

FIXTURE_PATH = SCRIPT_DIR / "fixtures" / "adb_baseline.json"

ROW_COUNT_QUERIES = {
    "OML.CHURN_PREDICTIONS": "SELECT COUNT(*) FROM OML.CHURN_PREDICTIONS",
    "OML.USER_PROFILES": "SELECT COUNT(*) FROM OML.USER_PROFILES",
    "OML.MODEL_REGISTRY": "SELECT COUNT(*) FROM OML.MODEL_REGISTRY",
    "OML.CHURN_DATASET_TRAINING": "SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING",
    "ADMIN.USERS": "SELECT COUNT(*) FROM ADMIN.USERS",
}

SUMMARY_QUERY = """
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
    ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 4) AS average_risk_score,
    ROUND(
        SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        4
    ) AS at_risk_percentage
FROM OML.CHURN_PREDICTIONS
"""

LTV_QUERY = """
SELECT
    ROUND(SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN up.LIFETIME_VALUE ELSE 0 END), 2)
        AS total_ltv_at_risk
FROM OML.CHURN_PREDICTIONS cp
INNER JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
"""

COHORTS_QUERY = """
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
SELECT
    cohort,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS at_risk_count,
    ROUND(AVG(PREDICTED_CHURN_PROBABILITY) * 100, 2) AS avg_risk_score,
    ROUND(SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN LIFETIME_VALUE ELSE 0 END), 2) AS ltv_at_risk
FROM cohort_assignments
WHERE cohort != 'Other'
GROUP BY cohort
ORDER BY cohort
"""


def fetch_one(cursor, query: str) -> dict:
    cursor.execute(query)
    row = cursor.fetchone()
    cols = [d[0].lower() for d in cursor.description]
    return dict(zip(cols, row))


def main() -> None:
    load_env()
    conn = connect_adb()
    cursor = conn.cursor()

    baseline = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": "adb",
        "row_counts": {},
        "summary": {},
        "cohorts": [],
        "admin_users_accessible": True,
    }

    for label, query in ROW_COUNT_QUERIES.items():
        try:
            cursor.execute(query)
            baseline["row_counts"][label] = cursor.fetchone()[0]
        except Exception as exc:
            baseline["row_counts"][label] = None
            if label == "ADMIN.USERS":
                baseline["admin_users_accessible"] = False
                baseline["admin_users_error"] = str(exc)

    baseline["summary"] = fetch_one(cursor, SUMMARY_QUERY)
    baseline["summary"]["total_ltv_at_risk"] = fetch_one(cursor, LTV_QUERY)["total_ltv_at_risk"]

    cursor.execute(COHORTS_QUERY)
    cols = [d[0].lower() for d in cursor.description]
    baseline["cohorts"] = [dict(zip(cols, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(baseline, indent=2, default=str) + "\n")
    print(f"✓ Wrote baseline to {FIXTURE_PATH}")
    print(json.dumps(baseline["row_counts"], indent=2))


if __name__ == "__main__":
    main()
