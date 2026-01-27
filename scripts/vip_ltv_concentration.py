#!/usr/bin/env python3
"""
VIP At-Risk: How many users account for the top 80% of LTV at risk?

Uses the same VIP definition as the cohorts API:
  VIP = LIFETIME_VALUE > 5000 OR AFFINITY_CARD = 1 (from ADMIN.USERS)
  At-risk = PREDICTED_CHURN_LABEL = 1

Orders VIP at-risk users by LIFETIME_VALUE descending, computes cumulative LTV,
and returns the minimum N such that the top N users account for >= 80% of
total LTV at risk for VIP.

Connectivity: uses get_db_connection() from scripts/test-python-connection.py
(same .env, Oracle client init, and connection logic as that script).

Usage:
    python scripts/vip_ltv_concentration.py
"""

import importlib.util
import sys
from pathlib import Path

script_dir = Path(__file__).parent

def _get_db_connection():
    """Use same connectivity as scripts/test-python-connection.py (get_db_connection)."""
    spec = importlib.util.spec_from_file_location(
        "test_python_connection",
        script_dir / "test-python-connection.py",
    )
    tpc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tpc)
    return tpc.get_db_connection()

def main():
    try:
        conn = _get_db_connection()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Run: python scripts/test-python-connection.py")
        return 1

    sql = """
    WITH vip_at_risk AS (
      SELECT up.LIFETIME_VALUE
      FROM OML.CHURN_PREDICTIONS cp
      JOIN OML.USER_PROFILES up ON cp.USER_ID = up.USER_ID
      JOIN ADMIN.USERS au ON up.USER_ID = au.ID
      WHERE (up.LIFETIME_VALUE > 5000 OR au.AFFINITY_CARD = 1)
        AND cp.PREDICTED_CHURN_LABEL = 1
    ),
    t AS (
      SELECT SUM(LIFETIME_VALUE) AS total_ltv, COUNT(*) AS total_users FROM vip_at_risk
    ),
    r AS (
      SELECT
        ROW_NUMBER() OVER (ORDER BY LIFETIME_VALUE DESC) AS rn,
        SUM(LIFETIME_VALUE) OVER (ORDER BY LIFETIME_VALUE DESC) AS cum_ltv
      FROM vip_at_risk
    )
    SELECT
      (SELECT total_users FROM t)       AS vip_at_risk_users,
      (SELECT total_ltv FROM t)         AS total_ltv_at_risk,
      (SELECT MIN(r.rn)
       FROM r CROSS JOIN t
       WHERE r.cum_ltv >= 0.8 * t.total_ltv) AS users_for_top_80_pct_ltv
    FROM DUAL
    """
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    conn.close()

    if not row or row[0] is None:
        print("No VIP at-risk users found.")
        return 0

    total_users, total_ltv, n80 = row
    total_ltv = float(total_ltv or 0)
    total_users = int(total_users or 0)
    n80 = int(n80) if n80 is not None else 0

    pct = (n80 / total_users * 100) if total_users else 0

    print("=" * 60)
    print("VIP at-risk: users that account for top 80% of LTV at risk")
    print("=" * 60)
    print(f"  VIP at-risk users (total):     {total_users:,}")
    print(f"  Total LTV at risk (VIP):       ${total_ltv:,.2f}")
    print(f"  Users for top 80% of that LTV: {n80:,}")
    print(f"  (i.e. {pct:.1f}% of VIP at-risk users hold 80% of VIP LTV at risk)")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
