#!/usr/bin/env python3
"""
Compare ADB and PostgreSQL after migration — row counts and API-equivalent aggregates.

Usage:
    python scripts/migration/validate_parity.py
    python scripts/migration/validate_parity.py --baseline scripts/migration/fixtures/adb_baseline.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = SCRIPT_DIR / "reports"
DEFAULT_BASELINE = SCRIPT_DIR / "fixtures" / "adb_baseline.json"
sys.path.insert(0, str(SCRIPT_DIR))

from db_utils import connect_adb, connect_postgres, load_env  # noqa: E402

PG_ROW_COUNTS = {
    "ecomm.churn_predictions": "SELECT COUNT(*) FROM ecomm.churn_predictions",
    "ecomm.user_profiles": "SELECT COUNT(*) FROM ecomm.user_profiles",
    "ecomm.model_registry": "SELECT COUNT(*) FROM ecomm.model_registry",
    "ecomm.churn_dataset_training": "SELECT COUNT(*) FROM ecomm.churn_dataset_training",
}

ADB_TO_PG_COUNT = {
    "OML.CHURN_PREDICTIONS": "ecomm.churn_predictions",
    "OML.USER_PROFILES": "ecomm.user_profiles",
    "OML.MODEL_REGISTRY": "ecomm.model_registry",
    "OML.CHURN_DATASET_TRAINING": "ecomm.churn_dataset_training",
}

PG_SUMMARY_QUERY = """
SELECT
    COUNT(*)::bigint AS total_customers,
    SUM(CASE WHEN predicted_churn_label = 1 THEN 1 ELSE 0 END)::bigint AS at_risk_count,
    ROUND((AVG(predicted_churn_probability) * 100)::numeric, 4) AS average_risk_score,
    ROUND(
        (SUM(CASE WHEN predicted_churn_label = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric,
        4
    ) AS at_risk_percentage
FROM ecomm.churn_predictions
"""

PG_LTV_QUERY = """
SELECT
    ROUND(SUM(CASE WHEN cp.predicted_churn_label = 1 THEN up.lifetime_value ELSE 0 END)::numeric, 2)
        AS total_ltv_at_risk
FROM ecomm.churn_predictions cp
INNER JOIN ecomm.user_profiles up ON cp.user_id = up.user_id
"""

PG_COHORTS_QUERY = """
WITH cohort_assignments AS (
    SELECT
        cp.predicted_churn_label,
        cp.predicted_churn_probability,
        up.lifetime_value,
        up.membership_years,
        up.total_purchases,
        up.days_since_last_purchase,
        up.login_frequency,
        up.affinity_card,
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
SELECT
    cohort,
    COUNT(*)::bigint AS customer_count,
    SUM(CASE WHEN predicted_churn_label = 1 THEN 1 ELSE 0 END)::bigint AS at_risk_count,
    ROUND((AVG(predicted_churn_probability) * 100)::numeric, 2) AS avg_risk_score,
    ROUND(SUM(CASE WHEN predicted_churn_label = 1 THEN lifetime_value ELSE 0 END)::numeric, 2)
        AS ltv_at_risk
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


def compare_counts(adb_counts: dict, pg_counts: dict) -> list[dict]:
    mismatches = []
    for adb_key, pg_key in ADB_TO_PG_COUNT.items():
        adb_val = adb_counts.get(adb_key)
        pg_val = pg_counts.get(pg_key)
        ok = adb_val is not None and pg_val is not None and int(adb_val) == int(pg_val)
        mismatches.append(
            {
                "check": "row_count",
                "adb": adb_key,
                "postgres": pg_key,
                "adb_value": adb_val,
                "postgres_value": pg_val,
                "ok": ok,
            }
        )
    return mismatches


def compare_summary(adb_summary: dict, pg_summary: dict, tolerance: float = 0.01) -> list[dict]:
    checks = []
    for key in ("total_customers", "at_risk_count", "average_risk_score", "total_ltv_at_risk"):
        adb_val = float(adb_summary.get(key) or 0)
        pg_val = float(pg_summary.get(key) or 0)
        if key in ("total_customers", "at_risk_count"):
            ok = int(adb_val) == int(pg_val)
        else:
            ok = abs(adb_val - pg_val) <= tolerance
        checks.append(
            {
                "check": f"summary.{key}",
                "adb_value": adb_val,
                "postgres_value": pg_val,
                "ok": ok,
            }
        )
    return checks


def compare_cohorts(adb_cohorts: list[dict], pg_cohorts: list[dict]) -> list[dict]:
    adb_map = {row["cohort"]: row for row in adb_cohorts}
    pg_map = {row["cohort"]: row for row in pg_cohorts}
    checks = []
    for cohort in sorted(set(adb_map) | set(pg_map)):
        adb_row = adb_map.get(cohort, {})
        pg_row = pg_map.get(cohort, {})
        for key in ("customer_count", "at_risk_count"):
            adb_val = int(adb_row.get(key) or 0)
            pg_val = int(pg_row.get(key) or 0)
            checks.append(
                {
                    "check": f"cohort.{cohort}.{key}",
                    "adb_value": adb_val,
                    "postgres_value": pg_val,
                    "ok": adb_val == pg_val,
                }
            )
    return checks


def load_or_capture_baseline(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())

    print(f"Baseline not found at {path}; capturing from ADB...")
    from capture_adb_baseline import main as capture_main

    capture_main()
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ADB vs Postgres migration parity")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    args = parser.parse_args()

    load_env()
    baseline = load_or_capture_baseline(args.baseline)

    pg_conn = connect_postgres()
    pg_cur = pg_conn.cursor()

    pg_counts = {}
    for label, query in PG_ROW_COUNTS.items():
        pg_cur.execute(query)
        pg_counts[label] = pg_cur.fetchone()[0]

    pg_summary = fetch_one(pg_cur, PG_SUMMARY_QUERY)
    pg_summary["total_ltv_at_risk"] = fetch_one(pg_cur, PG_LTV_QUERY)["total_ltv_at_risk"]

    pg_cur.execute(PG_COHORTS_QUERY)
    cols = [d[0].lower() for d in pg_cur.description]
    pg_cohorts = [dict(zip(cols, row)) for row in pg_cur.fetchall()]
    pg_cur.close()
    pg_conn.close()

    # Live ADB counts for comparison (authoritative)
    adb_conn = connect_adb()
    adb_cur = adb_conn.cursor()
    adb_counts = {}
    for adb_key in ADB_TO_PG_COUNT:
        schema, table = adb_key.split(".")
        adb_cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        adb_counts[adb_key] = adb_cur.fetchone()[0]
    adb_cur.close()
    adb_conn.close()

    report = {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "baseline_captured_at": baseline.get("captured_at"),
        "checks": [],
        "passed": True,
    }

    report["checks"].extend(compare_counts(adb_counts, pg_counts))
    report["checks"].extend(compare_summary(baseline.get("summary", {}), pg_summary))
    report["checks"].extend(compare_cohorts(baseline.get("cohorts", []), pg_cohorts))

    failures = [check for check in report["checks"] if not check["ok"]]
    report["passed"] = len(failures) == 0
    report["failure_count"] = len(failures)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORTS_DIR / f"parity_{stamp}.json"
    report_path.write_text(json.dumps(report, indent=2, default=str) + "\n")

    print(f"Report: {report_path}")
    for check in report["checks"]:
        status = "OK" if check["ok"] else "FAIL"
        print(f"  [{status}] {check['check']}: {check.get('adb_value')} vs {check.get('postgres_value')}")

    if failures:
        print(f"\n❌ {len(failures)} parity check(s) failed")
        sys.exit(1)

    print("\n✓ All parity checks passed")


if __name__ == "__main__":
    main()
