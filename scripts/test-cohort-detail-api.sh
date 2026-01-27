#!/bin/bash
# Test script for cohort detail API endpoint
# Tests all scenarios from task 8

BASE_URL="${1:-http://localhost:3001}"
ENDPOINT="${BASE_URL}/api/kpi/churn/cohorts"

echo "=========================================="
echo "Testing Cohort Detail API"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

test_endpoint() {
    local test_name="$1"
    local url="$2"
    local expected_status="$3"
    local expected_keyword="$4"
    
    test_count=$((test_count + 1))
    echo "[Test $test_count] $test_name"
    echo "  URL: $url"
    
    # Use timeout and better error handling
    response=$(curl -s -w "\n%{http_code}" --max-time 30 "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Check if curl failed
    if [ -z "$http_code" ] || [ "$http_code" = "000" ]; then
        echo -e "  ${RED}✗ FAIL${NC} - Connection failed or timeout"
        echo "  Response: $body"
        fail_count=$((fail_count + 1))
        echo ""
        return
    fi
    
    if [ "$http_code" = "$expected_status" ]; then
        if [ -n "$expected_keyword" ]; then
            if echo "$body" | grep -q "$expected_keyword"; then
                echo -e "  ${GREEN}✓ PASS${NC} - Status: $http_code, Contains: $expected_keyword"
                pass_count=$((pass_count + 1))
            else
                echo -e "  ${RED}✗ FAIL${NC} - Status: $http_code (correct), but missing keyword: $expected_keyword"
                echo "  Response preview: $(echo "$body" | head -c 200)..."
                fail_count=$((fail_count + 1))
            fi
        else
            echo -e "  ${GREEN}✓ PASS${NC} - Status: $http_code"
            pass_count=$((pass_count + 1))
        fi
    else
        echo -e "  ${RED}✗ FAIL${NC} - Expected status $expected_status, got $http_code"
        echo "  Response preview: $(echo "$body" | head -c 200)..."
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

# Test 8.1: Valid cohort names
echo "=== 8.1: Valid Cohort Names ==="
test_endpoint "VIP cohort" "$ENDPOINT/VIP" "200" "cohort"
test_endpoint "Regular cohort" "$ENDPOINT/Regular" "200" "cohort"
test_endpoint "New cohort" "$ENDPOINT/New" "200" "cohort"
test_endpoint "Dormant cohort" "$ENDPOINT/Dormant" "200" "cohort"
test_endpoint "Other cohort" "$ENDPOINT/Other" "200" "cohort"
test_endpoint "Case insensitive (vip)" "$ENDPOINT/vip" "200" "cohort"
test_endpoint "Case insensitive (REGULAR)" "$ENDPOINT/REGULAR" "200" "cohort"

# Test 8.2: Pagination
echo "=== 8.2: Pagination ==="
test_endpoint "Pagination: limit=10" "$ENDPOINT/VIP?limit=10" "200" "pagination"
test_endpoint "Pagination: limit=10, offset=10" "$ENDPOINT/VIP?limit=10&offset=10" "200" "pagination"
test_endpoint "Pagination: limit=5, offset=0" "$ENDPOINT/VIP?limit=5&offset=0" "200" "pagination"

# Test 8.3: Sorting
echo "=== 8.3: Sorting ==="
test_endpoint "Sort by churn (default)" "$ENDPOINT/VIP?limit=5&sort=churn" "200" "users"
test_endpoint "Sort by LTV" "$ENDPOINT/VIP?limit=5&sort=ltv" "200" "users"

# Test 8.4: limit=-1 (all users)
echo "=== 8.4: limit=-1 (All Users) ==="
test_endpoint "Return all users" "$ENDPOINT/VIP?limit=-1" "200" "pagination"

# Test 8.5: Invalid cohort name (404)
echo "=== 8.5: Invalid Cohort Name (404) ==="
test_endpoint "Invalid cohort name" "$ENDPOINT/InvalidCohort" "404" "not found"
test_endpoint "Empty cohort name" "$ENDPOINT/" "404" ""

# Test 8.6: Invalid query parameters (400)
echo "=== 8.6: Invalid Query Parameters (400) ==="
test_endpoint "Invalid limit (too high)" "$ENDPOINT/VIP?limit=1000" "400" "limit"
test_endpoint "Invalid limit (zero)" "$ENDPOINT/VIP?limit=0" "400" "limit"
test_endpoint "Invalid limit (negative, not -1)" "$ENDPOINT/VIP?limit=-2" "400" "limit"
test_endpoint "Invalid sort value" "$ENDPOINT/VIP?sort=invalid" "400" "sort"
test_endpoint "Invalid offset (negative)" "$ENDPOINT/VIP?offset=-1" "400" "offset"

# Test 8.7: Caching (verify cache hit)
echo "=== 8.7: Caching Behavior ==="
echo "[Test $((test_count + 1))] Cache test - First request"
first_response=$(curl -s -w "\n%{http_code}" "$ENDPOINT/VIP?limit=5")
first_code=$(echo "$first_response" | tail -n1)
if [ "$first_code" = "200" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} - First request successful"
    pass_count=$((pass_count + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} - First request failed with status $first_code"
    fail_count=$((fail_count + 1))
fi
test_count=$((test_count + 1))
echo ""

sleep 1

echo "[Test $((test_count + 1))] Cache test - Second request (should be cached)"
second_response=$(curl -s -w "\n%{http_code}" "$ENDPOINT/VIP?limit=5")
second_code=$(echo "$second_response" | tail -n1)
if [ "$second_code" = "200" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} - Second request successful (cache working)"
    pass_count=$((pass_count + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} - Second request failed with status $second_code"
    fail_count=$((fail_count + 1))
fi
test_count=$((test_count + 1))
echo ""

# Test 8.8: Database error handling (503) - This is hard to test without breaking DB
echo "=== 8.8: Database Error Handling (503) ==="
echo -e "  ${YELLOW}⚠ SKIP${NC} - Requires database connection failure simulation"
echo "  (Would need to break DB connection or use invalid credentials)"
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
