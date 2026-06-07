#!/usr/bin/env bash
# Open psql to OCI PostgreSQL through the SSH tunnel.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ -f "$PROJECT_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
fi

PSQL="${PSQL_PATH:-}"
if [[ -z "$PSQL" ]]; then
  for candidate in /opt/homebrew/opt/libpq/bin/psql /usr/local/opt/libpq/bin/psql psql; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PSQL="$candidate"
      break
    fi
  done
fi

if [[ -z "$PSQL" ]]; then
  echo "psql not found. Install libpq or set PSQL_PATH in .env" >&2
  exit 1
fi

LOCAL_PORT="${PGPORT:-15432}"
if ! lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Tunnel not running on port ${LOCAL_PORT}. Starting..."
  "$SCRIPT_DIR/pg-tunnel.sh"
fi

if [[ -n "${DATABASE_URL:-}" ]]; then
  exec "$PSQL" "$DATABASE_URL" "$@"
fi

: "${PGHOST:=127.0.0.1}"
: "${PGPORT:=15432}"
: "${PGUSER:?Set PGUSER or DATABASE_URL in .env}"
: "${PGDATABASE:?Set PGDATABASE or DATABASE_URL in .env}"

export PGPASSWORD="${PGPASSWORD:-}"
exec "$PSQL" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" "$@"
