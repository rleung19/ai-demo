#!/usr/bin/env python3
"""Shared database helpers for ADB → Postgres migration scripts."""

from __future__ import annotations

import glob
import os
import socket
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise SystemExit("python-dotenv is required. Run: pip install python-dotenv") from exc

    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE)
    else:
        load_dotenv()


def pg_host_port() -> tuple[str, int]:
    url = os.getenv("DATABASE_URL")
    if url:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 5432
        return host, port
    host = os.getenv("PGHOST", "127.0.0.1")
    port = int(os.getenv("PGPORT", "5432"))
    return host, port


def check_tunnel(host: str | None = None, port: int | None = None) -> bool:
    host, port = host or pg_host_port()[0], port or pg_host_port()[1]
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except OSError:
        return False


def init_oracle_client() -> None:
    import oracledb

    if os.getenv("ORACLE_CLIENT_INITIALIZED") == "1":
        return

    wallet_path = os.getenv("ADB_WALLET_PATH")
    if wallet_path:
        os.environ["TNS_ADMIN"] = os.getenv("TNS_ADMIN") or wallet_path

    lib_dir = os.getenv("ORACLE_CLIENT_LIB_DIR")
    if not lib_dir:
        for pattern in ["/opt/oracle/instantclient_*", "/opt/homebrew/lib"]:
            matches = glob.glob(pattern) if "*" in pattern else [pattern]
            for match in matches:
                if not os.path.exists(match):
                    continue
                for lib_name in ("libclntsh.dylib", "libclntsh.so"):
                    if os.path.exists(os.path.join(match, lib_name)):
                        lib_dir = match
                        break
                if lib_dir:
                    break
            if lib_dir:
                break

    if lib_dir:
        try:
            oracledb.init_oracle_client(lib_dir=lib_dir)
        except oracledb.ProgrammingError:
            pass

    os.environ["ORACLE_CLIENT_INITIALIZED"] = "1"


def connect_adb() -> Any:
    import oracledb

    load_env()
    init_oracle_client()

    wallet_path = os.getenv("ADB_WALLET_PATH")
    connection_string = os.getenv("ADB_CONNECTION_STRING")
    username = os.getenv("ADB_USERNAME", "OML")
    password = os.getenv("ADB_PASSWORD")

    if not all([wallet_path, connection_string, password]):
        raise SystemExit(
            "Missing ADB config. Set ADB_WALLET_PATH, ADB_CONNECTION_STRING, ADB_PASSWORD in .env"
        )

    os.environ["TNS_ADMIN"] = os.getenv("TNS_ADMIN") or wallet_path
    return oracledb.connect(user=username, password=password, dsn=connection_string)


def connect_postgres() -> Any:
    import psycopg2

    load_env()
    url = os.getenv("DATABASE_URL")
    if url:
        return psycopg2.connect(url)

    required = ("PGHOST", "PGUSER", "PGPASSWORD", "PGDATABASE")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise SystemExit(
            "Missing Postgres config. Set DATABASE_URL or "
            + ", ".join(missing)
            + " in .env"
        )

    return psycopg2.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        dbname=os.getenv("PGDATABASE"),
    )


def find_psql() -> str:
    candidates = [
        os.getenv("PSQL_PATH"),
        "/opt/homebrew/opt/libpq/bin/psql",
        "/usr/local/opt/libpq/bin/psql",
        "psql",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if candidate == "psql" or os.path.isfile(candidate):
            return candidate
    return "psql"


def apply_pg_ddl() -> None:
    import subprocess

    load_env()
    psql = find_psql()
    sql_dir = PROJECT_ROOT / "sql" / "postgres"
    env = os.environ.copy()

    url = os.getenv("DATABASE_URL")
    if url:
        base_cmd = [psql, url, "-v", "ON_ERROR_STOP=1", "-f"]
    else:
        base_cmd = [
            psql,
            "-h",
            os.getenv("PGHOST", "127.0.0.1"),
            "-p",
            os.getenv("PGPORT", "5432"),
            "-U",
            os.getenv("PGUSER", ""),
            "-d",
            os.getenv("PGDATABASE", ""),
            "-v",
            "ON_ERROR_STOP=1",
            "-f",
        ]
        env["PGPASSWORD"] = os.getenv("PGPASSWORD", "")

    for filename in ("001_create_schema.sql", "002_create_views.sql"):
        path = sql_dir / filename
        if not path.exists():
            raise FileNotFoundError(path)
        print(f"Applying {filename}...")
        result = subprocess.run(
            [*base_cmd, str(path)],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise SystemExit(f"Failed applying {filename}")
    print("✓ DDL applied")


def rows_to_dicts(cursor, rows: list[tuple]) -> list[dict[str, Any]]:
    columns = [desc[0].lower() for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
