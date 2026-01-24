#!/bin/bash
# Start both Next.js frontend and API server in PRODUCTION mode
# Used by Docker/Podman for production deployments

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Starting AI Demo Application (PRODUCTION)${NC}"
echo -e "${BLUE}============================================================${NC}"

# Ensure TNS_ADMIN is set
if [ -z "$TNS_ADMIN" ] && [ -n "$ADB_WALLET_PATH" ]; then
  export TNS_ADMIN="$ADB_WALLET_PATH"
  echo -e "${GREEN}✓ Set TNS_ADMIN to: $TNS_ADMIN${NC}"
fi

# Set API port if not set
if [ -z "$API_PORT" ]; then
  export API_PORT=3001
fi

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  NODE_ENV:         ${NODE_ENV:-production}"
echo "  Next.js Frontend: http://localhost:3000"
echo "  API Server:       http://localhost:$API_PORT"
echo "  TNS_ADMIN:        ${TNS_ADMIN:-not set}"
echo ""

# Function to cleanup on exit
cleanup() {
  echo ""
  echo -e "${BLUE}Shutting down servers...${NC}"
  kill $NEXTJS_PID $API_PID 2>/dev/null || true
  exit
}

trap cleanup SIGINT SIGTERM

# Start API server in background (production - uses compiled JS)
echo -e "${BLUE}Starting API server (production) on port $API_PORT...${NC}"
API_PORT=$API_PORT node dist/server/index.js &
API_PID=$!
echo -e "${GREEN}✓ API server started (PID: $API_PID)${NC}"

# Wait a bit for API server to start
sleep 2

# Start Next.js in production mode
echo -e "${BLUE}Starting Next.js frontend (production) on port 3000...${NC}"
next start &
NEXTJS_PID=$!
echo -e "${GREEN}✓ Next.js started (PID: $NEXTJS_PID)${NC}"

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Both servers are running in PRODUCTION mode!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Frontend:  http://localhost:3000"
echo "API:       http://localhost:$API_PORT"
echo ""
echo "Logs are streaming to stdout/stderr (visible via 'podman logs')"
echo ""

# Wait for both processes (keeps container running)
wait
