#!/usr/bin/env python3
"""Quick Postgres connectivity test (tunnel + DATABASE_URL)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from db_utils import check_tunnel, connect_postgres, load_env, pg_host_port  # noqa: E402


def main() -> None:
    load_env()
    host, port = pg_host_port()
    if not check_tunnel(host, port):
        raise SystemExit(
            f"Cannot reach Postgres at {host}:{port}. Run: scripts/dev/pg-tunnel.sh"
        )

    conn = connect_postgres()
    cur = conn.cursor()
    cur.execute("SELECT 1 AS ok, current_database(), current_user, current_schema()")
    row = cur.fetchone()
    cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ecomm'")
    has_ecomm = cur.fetchone() is not None
    cur.close()
    conn.close()

    print(f"✓ Connected to database={row[1]} user={row[2]}")
    print(f"  ecomm schema exists: {has_ecomm}")


if __name__ == "__main__":
    main()
