#!/usr/bin/env python3
"""
Migrate churn data from Oracle ADB (OML + ADMIN.USERS) to PostgreSQL (ecomm schema).

Usage:
    python scripts/migration/migrate_adb_to_postgres.py
    python scripts/migration/migrate_adb_to_postgres.py --truncate
    python scripts/migration/migrate_adb_to_postgres.py --tables tier1
    python scripts/migration/migrate_adb_to_postgres.py --apply-ddl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from db_utils import apply_pg_ddl, check_tunnel, connect_adb, connect_postgres, load_env, pg_host_port  # noqa: E402
from psycopg2.extras import execute_values  # noqa: E402

BATCH_SIZE = 1000

TIER1_TABLES = ("user_profiles", "churn_predictions", "model_registry")
TIER2_TABLES = ("churn_dataset_training",)
ALL_TABLES = TIER1_TABLES + TIER2_TABLES

TRAINING_COLUMNS = [
    "user_id", "age", "gender", "country", "city", "membership_years",
    "login_frequency", "session_duration_avg", "pages_per_session",
    "cart_abandonment_rate", "wishlist_items", "total_purchases",
    "average_order_value", "days_since_last_purchase", "discount_usage_rate",
    "returns_rate", "email_open_rate", "customer_service_calls",
    "product_reviews_written", "social_media_engagement_score",
    "mobile_app_usage", "payment_method_diversity", "lifetime_value",
    "credit_balance", "signup_quarter", "churned",
]

PROFILE_COLUMNS = TRAINING_COLUMNS + ["affinity_card"]

PREDICTION_COLUMNS = [
    "user_id", "predicted_churn_probability", "predicted_churn_label", "risk_score",
    "model_version", "prediction_date", "last_updated", "confidence_score",
]

REGISTRY_COLUMNS = [
    "model_id", "model_name", "model_version", "model_type", "model_file_path",
    "metadata_file_path", "auc_score", "accuracy", "precision_score", "recall_score",
    "f1_score", "optimal_threshold", "training_date", "training_duration_seconds",
    "train_samples", "test_samples", "feature_count", "status", "is_production",
    "training_parameters", "notes", "created_at", "updated_at",
]

TABLE_QUERIES = {
    "user_profiles": """
        SELECT
            up.USER_ID, up.AGE, up.GENDER, up.COUNTRY, up.CITY, up.MEMBERSHIP_YEARS,
            up.LOGIN_FREQUENCY, up.SESSION_DURATION_AVG, up.PAGES_PER_SESSION,
            up.CART_ABANDONMENT_RATE, up.WISHLIST_ITEMS, up.TOTAL_PURCHASES,
            up.AVERAGE_ORDER_VALUE, up.DAYS_SINCE_LAST_PURCHASE, up.DISCOUNT_USAGE_RATE,
            up.RETURNS_RATE, up.EMAIL_OPEN_RATE, up.CUSTOMER_SERVICE_CALLS,
            up.PRODUCT_REVIEWS_WRITTEN, up.SOCIAL_MEDIA_ENGAGEMENT_SCORE,
            up.MOBILE_APP_USAGE, up.PAYMENT_METHOD_DIVERSITY, up.LIFETIME_VALUE,
            up.CREDIT_BALANCE, up.SIGNUP_QUARTER, up.CHURNED,
            au.AFFINITY_CARD
        FROM OML.USER_PROFILES up
        LEFT JOIN ADMIN.USERS au ON up.USER_ID = au.ID
        ORDER BY up.USER_ID
    """,
    "churn_predictions": """
        SELECT
            USER_ID, PREDICTED_CHURN_PROBABILITY, PREDICTED_CHURN_LABEL, RISK_SCORE,
            MODEL_VERSION, PREDICTION_DATE, LAST_UPDATED, CONFIDENCE_SCORE
        FROM OML.CHURN_PREDICTIONS
        ORDER BY USER_ID
    """,
    "model_registry": """
        SELECT
            MODEL_ID, MODEL_NAME, MODEL_VERSION, MODEL_TYPE, MODEL_FILE_PATH,
            METADATA_FILE_PATH, AUC_SCORE, ACCURACY, PRECISION_SCORE, RECALL_SCORE,
            F1_SCORE, OPTIMAL_THRESHOLD, TRAINING_DATE, TRAINING_DURATION_SECONDS,
            TRAIN_SAMPLES, TEST_SAMPLES, FEATURE_COUNT, STATUS, IS_PRODUCTION,
            TRAINING_PARAMETERS, NOTES, CREATED_AT, UPDATED_AT
        FROM OML.MODEL_REGISTRY
        ORDER BY MODEL_ID
    """,
    "churn_dataset_training": """
        SELECT
            USER_ID, AGE, GENDER, COUNTRY, CITY, MEMBERSHIP_YEARS,
            LOGIN_FREQUENCY, SESSION_DURATION_AVG, PAGES_PER_SESSION,
            CART_ABANDONMENT_RATE, WISHLIST_ITEMS, TOTAL_PURCHASES,
            AVERAGE_ORDER_VALUE, DAYS_SINCE_LAST_PURCHASE, DISCOUNT_USAGE_RATE,
            RETURNS_RATE, EMAIL_OPEN_RATE, CUSTOMER_SERVICE_CALLS,
            PRODUCT_REVIEWS_WRITTEN, SOCIAL_MEDIA_ENGAGEMENT_SCORE,
            MOBILE_APP_USAGE, PAYMENT_METHOD_DIVERSITY, LIFETIME_VALUE,
            CREDIT_BALANCE, SIGNUP_QUARTER, CHURNED
        FROM OML.CHURN_DATASET_TRAINING
        ORDER BY USER_ID
    """,
}

TABLE_PG_COLUMNS = {
    "user_profiles": PROFILE_COLUMNS,
    "churn_predictions": PREDICTION_COLUMNS,
    "model_registry": REGISTRY_COLUMNS,
    "churn_dataset_training": TRAINING_COLUMNS,
}


def normalize_row(row: tuple) -> tuple:
    return tuple(item.read() if hasattr(item, "read") else item for item in row)


def batched(iterable: Iterable[tuple], size: int) -> Iterable[list[tuple]]:
    batch: list[tuple] = []
    for item in iterable:
        batch.append(normalize_row(item))
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def apply_ddl(_pg_conn=None) -> None:
    apply_pg_ddl()


def truncate_tables(pg_conn, tables: tuple[str, ...]) -> None:
    qualified = ", ".join(f"ecomm.{table}" for table in tables)
    pg_conn.cursor().execute(f"TRUNCATE TABLE {qualified} RESTART IDENTITY CASCADE")
    pg_conn.commit()
    print(f"✓ Truncated {qualified}")


def migrate_table(adb_cur, pg_conn, table: str) -> int:
    columns = TABLE_PG_COLUMNS[table]
    col_list = ", ".join(columns)
    insert_sql = f"INSERT INTO ecomm.{table} ({col_list}) VALUES %s"

    adb_cur.execute(TABLE_QUERIES[table])
    total = 0
    pg_cur = pg_conn.cursor()
    while True:
        rows = adb_cur.fetchmany(BATCH_SIZE)
        if not rows:
            break
        execute_values(pg_cur, insert_sql, [normalize_row(r) for r in rows], page_size=BATCH_SIZE)
        total += len(rows)
        pg_conn.commit()
        print(f"  {table}: {total:,} rows...", end="\r")
    pg_cur.close()
    print(f"  {table}: {total:,} rows migrated")
    return total


def preflight() -> None:
    host, port = pg_host_port()
    if not check_tunnel(host, port):
        raise SystemExit(
            f"Postgres not reachable at {host}:{port}. "
            "Start tunnel: scripts/dev/pg-tunnel.sh"
        )
    print(f"✓ Postgres port open at {host}:{port}")

    adb = connect_adb()
    adb.close()
    print("✓ ADB connection OK")

    pg = connect_postgres()
    pg.close()
    print("✓ Postgres connection OK")


def parse_tables(value: str) -> tuple[str, ...]:
    if value == "tier1":
        return TIER1_TABLES
    if value == "all":
        return ALL_TABLES
    selected = tuple(part.strip() for part in value.split(",") if part.strip())
    unknown = set(selected) - set(ALL_TABLES)
    if unknown:
        raise SystemExit(f"Unknown tables: {', '.join(sorted(unknown))}")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate ADB churn data to PostgreSQL")
    parser.add_argument("--truncate", action="store_true", help="Truncate target tables before load")
    parser.add_argument("--apply-ddl", action="store_true", help="Apply sql/postgres/*.sql before migrate")
    parser.add_argument(
        "--tables",
        default="all",
        help="Tables to migrate: all | tier1 | comma-separated list",
    )
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    load_env()
    tables = parse_tables(args.tables)

    if not args.skip_preflight:
        preflight()

    pg_conn = connect_postgres()
    if args.apply_ddl:
        apply_ddl()

    if args.truncate:
        truncate_tables(pg_conn, tables)

    adb_conn = connect_adb()
    adb_cur = adb_conn.cursor()

    counts: dict[str, int] = {}
    for table in tables:
        print(f"\nMigrating {table}...")
        counts[table] = migrate_table(adb_cur, pg_conn, table)

    adb_cur.close()
    adb_conn.close()
    pg_conn.close()

    print("\n✓ Migration complete")
    for table, count in counts.items():
        print(f"  ecomm.{table}: {count:,}")


if __name__ == "__main__":
    main()
