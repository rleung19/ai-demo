#!/usr/bin/env bash
# Start SSH tunnel to OCI PostgreSQL if local port is not already listening.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

LOCAL_PORT="${PG_LOCAL_PORT:-15432}"
REMOTE_HOST="${PG_REMOTE_HOST:-10.0.1.239}"
REMOTE_PORT="${PG_REMOTE_PORT:-5432}"
JUMP_HOST="${PG_JUMP_HOST:-40b5c371.nip.io}"

if lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✓ Tunnel already listening on 127.0.0.1:${LOCAL_PORT}"
  exit 0
fi

echo "Starting SSH tunnel 127.0.0.1:${LOCAL_PORT} -> ${REMOTE_HOST}:${REMOTE_PORT} via ${JUMP_HOST}"
ssh -f -N -L "${LOCAL_PORT}:${REMOTE_HOST}:${REMOTE_PORT}" "$JUMP_HOST"

sleep 1
if lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✓ Tunnel up on 127.0.0.1:${LOCAL_PORT}"
else
  echo "❌ Tunnel failed to start" >&2
  exit 1
fi
