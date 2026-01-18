#!/bin/bash
# Test API Endpoints
# Tests all churn model API endpoints and reports results

API_URL="${API_URL:-http://localhost:3001}"
echo "Testing API endpoints at: $API_URL"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local endpoint=$2
    local method=${3:-GET}
    
    echo -n "Testing $name ($method $endpoint)... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -20 || echo "$body" | head -5
    elif [ "$http_code" = "503" ]; then
        echo -e "${YELLOW}⚠ Service Unavailable${NC} (HTTP $http_code)"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -10 || echo "$body" | head -3
    else
        echo -e "${RED}✗ Failed${NC} (HTTP $http_code)"
        echo "$body" | head -3
    fi
    echo ""
}

# Test all endpoints
echo "1. Root endpoint"
test_endpoint "Root" "/"

echo "2. Health check"
test_endpoint "Health" "/api/health"

echo "3. Churn summary"
test_endpoint "Summary" "/api/kpi/churn/summary"

echo "4. Churn cohorts"
test_endpoint "Cohorts" "/api/kpi/churn/cohorts"

echo "5. Churn metrics"
test_endpoint "Metrics" "/api/kpi/churn/metrics"

echo "6. Chart data (7 days)"
test_endpoint "Chart Data" "/api/kpi/churn/chart-data?period=7d"

echo "7. Chart data (30 days)"
test_endpoint "Chart Data" "/api/kpi/churn/chart-data?period=30d"

echo "=================================="
echo "Testing complete!"
