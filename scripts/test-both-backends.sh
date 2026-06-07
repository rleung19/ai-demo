#!/usr/bin/env bash
# Test Oracle ADB and PostgreSQL: direct connections + Express churn API.
#
# Usage:
#   ./scripts/test-both-backends.sh
#   npm run test:backends
#
# Prerequisites:
#   - .env configured for ADB wallet and Postgres (PGHOST/PGUSER/PGPASSWORD/PGDATABASE)
#   - Postgres SSH tunnel on PGHOST:PGPORT (default 127.0.0.1:15432)
#   - Oracle Instant Client for thick-mode wallet (see scripts/test-node-connection.js)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ORACLE_PORT="${ORACLE_TEST_PORT:-3002}"
POSTGRES_PORT="${POSTGRES_TEST_PORT:-3003}"
PRIMARY_PORT="${API_PORT:-3001}"
SERVER_START_TIMEOUT="${SERVER_START_TIMEOUT:-45}"

failures=0
oracle_summary=""
postgres_summary=""

pass() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; failures=$((failures + 1)); }
warn() { echo -e "${YELLOW}!${NC} $1"; }

load_env() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi
}

wait_for_server() {
  local port=$1
  local deadline=$((SECONDS + SERVER_START_TIMEOUT))
  while (( SECONDS < deadline )); do
    if curl -sf "http://localhost:${port}/api/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

start_express() {
  local backend=$1 port=$2
  DB_BACKEND="$backend" API_PORT="$port" npx tsx server/index.ts >/tmp/express-test-${backend}-${port}.log 2>&1 &
  echo $!
}

stop_express() {
  local pid=$1
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
}

port_free() {
  ! lsof -i ":$1" >/dev/null 2>&1
}

test_express_backend() {
  local backend=$1 port=$2
  local pid=""

  echo ""
  echo "=== Express + ${backend} (:${port}) ==="

  if ! port_free "$port"; then
    fail "Port ${port} in use (set ORACLE_TEST_PORT / POSTGRES_TEST_PORT)"
    return
  fi

  pid="$(start_express "$backend" "$port")"
  if ! wait_for_server "$port"; then
    fail "Express (${backend}) did not become ready on :${port}"
    tail -15 "/tmp/express-test-${backend}-${port}.log" 2>/dev/null || true
    stop_express "$pid"
    return
  fi

  local health summary http_backend at_risk
  health="$(curl -sf "http://localhost:${port}/api/health" 2>/dev/null || echo "")"
  summary="$(curl -sf "http://localhost:${port}/api/kpi/churn/summary" 2>/dev/null || echo "")"

  if [[ -z "$health" ]]; then
    fail "GET /api/health failed (${backend})"
  else
    http_backend="$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('database',{}).get('backend','?'))" 2>/dev/null || echo "?")"
    db_connected="$(echo "$health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('database',{}).get('connected', False))" 2>/dev/null || echo "False")"
    if [[ "$http_backend" == "$backend" && "$db_connected" == "True" ]]; then
      pass "Health (${backend}, connected)"
    else
      fail "Health check unexpected for ${backend} (backend=${http_backend}, connected=${db_connected})"
    fi
  fi

  if [[ -z "$summary" ]]; then
    fail "GET /api/kpi/churn/summary failed (${backend})"
  else
    at_risk="$(echo "$summary" | python3 -c "import sys,json; print(json.load(sys.stdin).get('atRiskCount','?'))" 2>/dev/null || echo "?")"
    pass "Summary (${backend}): atRiskCount=${at_risk}"
    if [[ "$backend" == "oracle" ]]; then
      oracle_summary="$at_risk"
    else
      postgres_summary="$at_risk"
    fi
  fi

  stop_express "$pid"
}

load_env

echo "Testing both database backends"
echo "================================"

echo ""
echo "=== Direct connections ==="
if python3 scripts/migration/test_pg_connection.py >/dev/null 2>&1; then
  pass "Postgres direct (Python)"
else
  fail "Postgres direct — run ./scripts/dev/pg-tunnel.sh and check PG* in .env"
fi

if node scripts/test-node-connection.js >/dev/null 2>&1; then
  pass "Oracle ADB direct (Node)"
else
  fail "Oracle direct — check ADB wallet / Instant Client in .env"
fi

test_express_backend oracle "$ORACLE_PORT"
test_express_backend postgres "$POSTGRES_PORT"

if curl -sf "http://localhost:${PRIMARY_PORT}/api/health" >/dev/null 2>&1; then
  echo ""
  echo "=== Existing server (:${PRIMARY_PORT}) ==="
  running_backend="$(curl -sf "http://localhost:${PRIMARY_PORT}/api/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('database',{}).get('backend','?'))" 2>/dev/null || echo "?")"
  pass "Already running with backend=${running_backend}"
else
  warn "No Express server on :${PRIMARY_PORT} (start with npm run server:dev or server:dev:postgres)"
fi

if [[ -n "$oracle_summary" && -n "$postgres_summary" ]]; then
  echo ""
  if [[ "$oracle_summary" == "$postgres_summary" ]]; then
    pass "Parity: atRiskCount matches (${oracle_summary})"
  else
    warn "Parity: atRiskCount differs (oracle=${oracle_summary}, postgres=${postgres_summary})"
  fi
fi

echo ""
echo "================================"
if (( failures == 0 )); then
  echo -e "${GREEN}All backend tests passed.${NC}"
  exit 0
else
  echo -e "${RED}${failures} test(s) failed.${NC}"
  exit 1
fi
