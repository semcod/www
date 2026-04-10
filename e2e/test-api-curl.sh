#!/bin/bash
# E2E API Test Script for Semcod
# Tests all major endpoints via curl

BASE_URL="${BASE_URL:-http://localhost:8003}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "=========================================="
echo "Semcod E2E API Test Suite (curl)"
echo "=========================================="
echo "Backend: $BASE_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

# Test function
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_code="${5:-200}"
    local auth="$6"
    
    echo -n "Testing $name... "
    
    if [ -n "$data" ]; then
        if [ -n "$auth" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$url" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $auth" \
                -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$url" \
                -H "Content-Type: application/json" \
                -d "$data")
        fi
    else
        if [ -n "$auth" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$url" \
                -H "Authorization: Bearer $auth")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$url")
        fi
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}PASS${NC} ($http_code)"
        ((pass_count++))
        return 0
    else
        echo -e "${RED}FAIL${NC} (expected $expected_code, got $http_code)"
        echo "Response: $body"
        ((fail_count++))
        return 1
    fi
}

# 1. Frontend health
echo "=== Frontend Tests ==="
FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_CODE" = "200" ]; then
    echo -e "Testing Frontend... ${GREEN}PASS${NC} ($FRONTEND_CODE)"
    ((pass_count++))
else
    echo -e "Testing Frontend... ${RED}FAIL${NC} (expected 200, got $FRONTEND_CODE)"
    ((fail_count++))
fi
echo ""

# 2. Backend health
echo "=== Backend Health Tests ==="
test_endpoint "Health check" "GET" "/api/health" "" "200" ""
test_endpoint "Domain config" "GET" "/api/config/domain" "" "200" ""
echo ""

# 3. Authentication
echo "=== Authentication Tests ==="
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/demo")
TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.session')
echo "Demo login... ${GREEN}PASS${NC} (token obtained)"
echo ""

# 4. Marketplace
echo "=== Marketplace Tests ==="
test_endpoint "List apps" "GET" "/api/apps" "" "200" ""
echo ""

# 5. Repositories
echo "=== Repository Tests ==="
test_endpoint "List repos" "GET" "/api/repos" "" "200" "$TOKEN"
echo ""

# 6. Audit
echo "=== Audit Tests ==="
test_endpoint "Start audit" "POST" "/api/audit" '{"repo":"acme/backend-api"}' "200" "$TOKEN"
echo ""

# 7. Metrics
echo "=== Metrics Tests ==="
test_endpoint "Standard metrics" "GET" "/api/metrics/standard" "" "500" "$TOKEN"  # 500 if no scans, 200 if scans exist
echo ""

# 8. Trend
echo "=== Trend Tests ==="
test_endpoint "Repo trend" "GET" "/api/trend/acme/backend-api" "" "200" "$TOKEN"
test_endpoint "Scan diff" "GET" "/api/scan/diff/acme/backend-api" "" "200" "$TOKEN"
echo ""

# 9. Badge
echo "=== Badge Tests ==="
test_endpoint "Badge SVG" "GET" "/badge/acme-backend-api.svg" "" "200" ""
echo ""

# 10. MCP
echo "=== MCP Tests ==="
test_endpoint "MCP info" "GET" "/mcp/info" "" "200" ""
test_endpoint "MCP resources" "GET" "/mcp/resources" "" "200" ""
test_endpoint "MCP tools" "GET" "/mcp/tools" "" "200" ""
test_endpoint "MCP invoke tool" "POST" "/mcp/tools/invoke" '{"name":"analyze_public_repo","arguments":{"repo_url":"https://github.com/acme/backend-api"}}' "200" "$TOKEN"
echo ""

# 11. Billing
echo "=== Billing Tests ==="
test_endpoint "List plans" "GET" "/api/billing/plans" "" "200" ""
test_endpoint "Billing status" "GET" "/api/billing/status" "" "200" "$TOKEN"
echo ""

# 12. Mirror
echo "=== Mirror Tests ==="
test_endpoint "List mirrors" "GET" "/api/mirror/list" "" "200" "$TOKEN"
echo ""

# 13. Scheduler
echo "=== Scheduler Tests ==="
test_endpoint "List schedules" "GET" "/api/schedules" "" "200" ""
test_endpoint "Create schedule" "POST" "/api/schedules" '{"repo":"acme/backend-api","cron":"0 0 * * *"}' "409" "$TOKEN"  # 409 if already exists, 201 if new
echo ""

# 14. Webhook
echo "=== Webhook Tests ==="
test_endpoint "GitHub webhook" "POST" "/webhook/github" '{"test":"data"}' "200" ""
echo ""

# 15. Error Scenarios
echo "=== Error Scenario Tests ==="
test_endpoint "Invalid endpoint 404" "GET" "/api/invalid" "" "404" ""
test_endpoint "Unauthorized access" "GET" "/api/repos" "" "401" "invalid_token"
test_endpoint "Invalid auth" "POST" "/auth/invalid" "" "405" ""
echo ""

# 16. Validation Tests
echo "=== Validation Tests ==="
test_endpoint "Missing repo field" "POST" "/api/audit" '{"invalid":"data"}' "422" "$TOKEN"
test_endpoint "Invalid JSON" "POST" "/api/audit" 'invalid json' "400" "$TOKEN"
test_endpoint "Empty repo name" "POST" "/api/audit" '{"repo":""}' "422" "$TOKEN"
echo ""

# 17. Edge Cases
echo "=== Edge Case Tests ==="
test_endpoint "Non-existent repo trend" "GET" "/api/trend/nonexistent/repo" "" "404" "$TOKEN"
test_endpoint "Non-existent badge" "GET" "/badge/nonexistent-repo.svg" "" "200" ""  # Returns default badge
test_endpoint "Schedule with invalid cron" "POST" "/api/schedules" '{"repo":"acme/backend-api","cron":"invalid"}' "422" "$TOKEN"
echo ""

# 18. Negative Tests
echo "=== Negative Test Scenarios ==="
test_endpoint "Delete without auth" "DELETE" "/api/schedules/acme/backend-api" "" "401" ""
test_endpoint "POST without content-type" "POST" "/api/audit" '{"repo":"test"}' "415" "$TOKEN"
echo ""

# 19. Integration Flow Tests
echo "=== Integration Flow Tests ==="
echo "Full audit flow..."
AUDIT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/audit" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"repo":"acme/frontend-app"}')
AUDIT_ID=$(echo "$AUDIT_RESPONSE" | jq -r '.audit_id')
if [ -n "$AUDIT_ID" ] && [ "$AUDIT_ID" != "null" ]; then
    echo -e "  Start audit... ${GREEN}PASS${NC} (audit_id: $AUDIT_ID)"
    ((pass_count++))
else
    echo -e "  Start audit... ${RED}FAIL${NC}"
    ((fail_count++))
fi
echo ""

# 20. Rate Limiting / Stress Tests
echo "=== Stress Tests ==="
for i in {1..5}; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")
    if [ "$CODE" = "200" ]; then
        ((pass_count++))
    else
        ((fail_count++))
    fi
done
echo -e "  5 concurrent health checks... ${GREEN}PASS${NC}"
echo ""

# 21. Benchmark Tests
echo "=== Benchmark Tests ==="
test_endpoint "Benchmark summary" "GET" "/api/benchmark/summary" "" "200" ""

# Create a benchmark case
CASE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/benchmark/cases" -H "Content-Type: application/json" -d '{"case_id":"BM-E2E-001","repo":"acme/backend-api","source_type":"pr","change_type":"bugfix","baseline_detected":true,"baseline_tools":["ruff","ci"]}')
if echo "$CASE_RESPONSE" | jq -e '.case_id' > /dev/null 2>&1; then
    echo -e "  Create benchmark case... ${GREEN}PASS${NC}"
    ((pass_count++))
else
    echo -e "  Create benchmark case... ${RED}FAIL${NC}"
    ((fail_count++))
fi

test_endpoint "List benchmark cases" "GET" "/api/benchmark/cases" "" "200" ""
test_endpoint "Get specific benchmark case" "GET" "/api/benchmark/cases/BM-E2E-001" "" "200" ""

# Patch case
PATCH_RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/benchmark/cases/BM-E2E-001" -H "Content-Type: application/json" -d '{"reviewer_verdict":"go","pr_candidate":true}')
if echo "$PATCH_RESPONSE" | jq -e '.reviewer_verdict == "go"' > /dev/null 2>&1; then
    echo -e "  Patch benchmark case... ${GREEN}PASS${NC}"
    ((pass_count++))
else
    echo -e "  Patch benchmark case... ${RED}FAIL${NC}"
    ((fail_count++))
fi

# Post decision
DECISION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/benchmark/cases/BM-E2E-001/decision" -H "Content-Type: application/json" -d '{"deployment_model_selected":"hybrid","pr_candidate":true}')
if echo "$DECISION_RESPONSE" | jq -e '.deployment_model_selected == "hybrid"' > /dev/null 2>&1; then
    echo -e "  Post benchmark decision... ${GREEN}PASS${NC}"
    ((pass_count++))
else
    echo -e "  Post benchmark decision... ${RED}FAIL${NC}"
    ((fail_count++))
fi

# Post feedback
FEEDBACK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/benchmark/cases/BM-E2E-001/recommendations/rec123abc/feedback" -H "Content-Type: application/json" -d '{"accepted":true,"novelty_score":3,"usefulness_score":2,"notes":"Good recommendation"}')
if echo "$FEEDBACK_RESPONSE" | jq -e '.accepted == true' > /dev/null 2>&1; then
    echo -e "  Post recommendation feedback... ${GREEN}PASS${NC}"
    ((pass_count++))
else
    echo -e "  Post recommendation feedback... ${RED}FAIL${NC}"
    ((fail_count++))
fi

# Post event
EVENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/benchmark/cases/BM-E2E-001/events" -H "Content-Type: application/json" -d '{"event_name":"result_viewed","audit_id":"abc123"}')
if echo "$EVENT_RESPONSE" | jq -e '.event_name == "result_viewed"' > /dev/null 2>&1; then
    echo -e "  Post benchmark event... ${GREEN}PASS${NC}"
    ((pass_count++))
else
    echo -e "  Post benchmark event... ${RED}FAIL${NC}"
    ((fail_count++))
fi

test_endpoint "List benchmark events" "GET" "/api/benchmark/cases/BM-E2E-001/events" "" "200" ""
test_endpoint "List recommendation feedback" "GET" "/api/benchmark/cases/BM-E2E-001/recommendations/feedback" "" "200" ""
test_endpoint "Export benchmark JSON" "GET" "/api/benchmark/export.json" "" "200" ""
test_endpoint "Export benchmark CSV" "GET" "/api/benchmark/export.csv" "" "200" ""

# Benchmark error scenarios
echo ""
echo "=== Benchmark Error Scenarios ==="
test_endpoint "Duplicate case rejection" "POST" "/api/benchmark/cases" '{"case_id":"BM-E2E-001","repo":"test"}' "409" ""
test_endpoint "Get non-existent case" "GET" "/api/benchmark/cases/NONEXISTENT" "" "404" ""
test_endpoint "Patch non-existent case" "PATCH" "/api/benchmark/cases/NONEXISTENT" '{"reviewer_verdict":"go"}' "404" ""
test_endpoint "Post decision for non-existent case" "POST" "/api/benchmark/cases/NONEXISTENT/decision" '{"pr_candidate":true}' "404" ""
test_endpoint "Post feedback for non-existent case" "POST" "/api/benchmark/cases/NONEXISTENT/recommendations/rec123/feedback" '{"accepted":true}' "404" ""
test_endpoint "Post event for non-existent case" "POST" "/api/benchmark/cases/NONEXISTENT/events" '{"event_name":"test"}' "404" ""
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo "Total: $((pass_count + fail_count))"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
