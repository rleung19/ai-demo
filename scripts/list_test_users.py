#!/usr/bin/env python3
"""
List 5 USER_IDs that are NOT in the original 26 users, for testing the recommender.

Usage:
  # With v1 recommendations.csv (to exclude the original 26):
  python list_test_users.py --exclude-csv /path/to/recommendations.csv

  # Get the v1 recommendations from your Data Science backup first:
  # /home/datascience/backups/v1_20260125_121732/results/recommendations.csv
  # Download it, then:
  python list_test_users.py --exclude-csv ./v1_recommendations.csv

  # Without exclude: returns 5 users (may include some of the 26)
  python list_test_users.py

---

Or run this in your Data Science notebook (you already have connection_parameters):

  # 1) Original 26 from v1 backup
  v1_recs = pd.read_csv("/home/datascience/backups/v1_20260125_121732/results/recommendations.csv")
  original_26 = set(v1_recs["user_id"].astype(str))   # or "USER_ID" if different

  # 2) All users from DB
  q = "SELECT DISTINCT USER_ID FROM ADMIN.ORDERS_PROFILE_V WHERE USER_ID IS NOT NULL"
  all_df = pd.DataFrame.ads.read_sql(q, connection_parameters=connection_parameters)
  all_ids = all_df["USER_ID"].astype(str).tolist()

  # 3) 5 not in the 26
  not_in_26 = [u for u in all_ids if u not in original_26]
  for u in not_in_26[:5]:
      print(u)
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / ".env"

try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

try:
    import oracledb
except ImportError:
    print("oracledb not installed. Run: pip install oracledb")
    sys.exit(1)


def _get_db_connection():
    """Use same connection logic as test-python-connection.py (thick mode + wallet)."""
    spec = importlib.util.spec_from_file_location(
        "test_python_connection",
        script_dir / "test-python-connection.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.get_db_connection()


def load_exclude_ids(path: str) -> set:
    """Load user IDs to exclude from a CSV (e.g. v1 recommendations.csv)."""
    import csv
    exclude = set()
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return exclude
        # Prefer user_id, else USER_ID, else first column
        uid_col = None
        for c in ("user_id", "USER_ID", "user"):
            if c in (reader.fieldnames or []):
                uid_col = c
                break
        if not uid_col:
            uid_col = reader.fieldnames[0]
        for row in reader:
            v = (row.get(uid_col) or "").strip()
            if v:
                exclude.add(v)
    return exclude


def main():
    ap = argparse.ArgumentParser(description="List 5 USER_IDs not in the original 26")
    ap.add_argument(
        "--exclude-csv",
        default=None,
        help="CSV with user_id column to exclude (e.g. v1 results/recommendations.csv)",
    )
    ap.add_argument("-n", "--num", type=int, default=5, help="Number of users to return (default: 5)")
    args = ap.parse_args()

    exclude = set()
    if args.exclude_csv:
        p = Path(args.exclude_csv)
        if not p.exists():
            print(f"File not found: {p}")
            sys.exit(1)
        exclude = load_exclude_ids(str(p))
        print(f"Excluding {len(exclude)} user(s) from {p.name}\n")

    try:
        conn = _get_db_connection()
    except Exception as e:
        print(f"Database connection error: {e}")
        print("\nIf you see ORA-12506 / DPY-6000 / 'Listener refused':")
        print("  - Run: python scripts/test-python-connection.py")
        print("  - Or use the Data Science notebook snippet in this script's docstring.")
        sys.exit(1)

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT USER_ID
            FROM ADMIN.ORDERS_PROFILE_V
            WHERE USER_ID IS NOT NULL
            ORDER BY USER_ID
            """
        )
        all_ids = [str(r[0]) for r in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as e:
        conn.close()
        print(f"Database error: {e}")
        sys.exit(1)

    candidate = [u for u in all_ids if u not in exclude]

    if len(candidate) < args.num:
        print(f"Only {len(candidate)} user(s) available after exclusions (requested {args.num}).")
        n = len(candidate)
    else:
        n = args.num

    chosen = candidate[:n]

    print("=" * 60)
    print(f"{len(chosen)} USER_IDs to use for testing (not in the original 26)")
    print("=" * 60)
    for i, uid in enumerate(chosen, 1):
        print(uid)
    print("=" * 60)
    print()
    print("Use in your test cell, e.g.:")
    print('  result = test_deployment.predict({"user_id": "%s", "top_k": 5})' % (chosen[0] if chosen else "USER_ID"))
    print()
    if not exclude and all_ids:
        print("To exclude the original 26: download v1 recommendations from")
        print("  /home/datascience/backups/v1_.../results/recommendations.csv")
        print("  and run: python list_test_users.py --exclude-csv <path>")
    print()


if __name__ == "__main__":
    main()
