#!/bin/bash
# API test script for GitHub OAuth simulation
# Tests all OAuth endpoints using curl

set -e

FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8003}"
MOCK_GITHUB_URL="${MOCK_GITHUB_URL:-http://localhost:4010}"

echo "🚀 GitHub OAuth Simulation - API Test Suite"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Test function
test_api() {
    local name="$1"
    local command="$2"
    local expected_status="$3"
    local expected_content="$4"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "\n🧪 $name"
    
    # Run the command and capture output
    if output=$(eval "$command" 2>&1); then
        status=$(echo "$output" | grep -o "HTTP/[0-9.]* [0-9]*" | grep -o "[0-9]*" | head -1)
        if [ -z "$status" ]; then
            # For curl without -v, check if command succeeded
            if echo "$output" | grep -q "200\|201\|302\|307"; then
                status="200"
            fi
        fi
        
        if [ "$status" = "$expected_status" ]; then
            if [ -n "$expected_content" ]; then
                if echo "$output" | grep -q "$expected_content"; then
                    echo -e "   ${GREEN}✅ PASSED${NC}"
                    TESTS_PASSED=$((TESTS_PASSED + 1))
                else
                    echo -e "   ${RED}❌ FAILED${NC} - Expected content not found: $expected_content"
                    echo "   Output: $output"
                    TESTS_FAILED=$((TESTS_FAILED + 1))
                fi
            else
                echo -e "   ${GREEN}✅ PASSED${NC}"
                TESTS_PASSED=$((TESTS_PASSED + 1))
            fi
        else
            echo -e "   ${RED}❌ FAILED${NC} - Expected status $expected_status, got $status"
            echo "   Output: $output"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo -e "   ${RED}❌ FAILED${NC} - Command failed"
        echo "   Output: $output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Check if services are running
echo "🔍 Checking service availability..."

if curl -s "$FRONTEND_URL" > /dev/null; then
    echo -e "   ${GREEN}✅ Frontend server at $FRONTEND_URL${NC}"
else
    echo -e "   ${RED}❌ Frontend server at $FRONTEND_URL${NC}"
    echo "   Please start with: docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d"
    exit 1
fi

if curl -s "$BACKEND_URL/api/health" > /dev/null; then
    echo -e "   ${GREEN}✅ Backend server at $BACKEND_URL${NC}"
else
    echo -e "   ${RED}❌ Backend server at $BACKEND_URL${NC}"
    echo "   Please start with: docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d"
    exit 1
fi

if curl -s "$MOCK_GITHUB_URL/health" > /dev/null; then
    echo -e "   ${GREEN}✅ Mock GitHub server at $MOCK_GITHUB_URL${NC}"
else
    echo -e "   ${RED}❌ Mock GitHub server at $MOCK_GITHUB_URL${NC}"
    echo "   Please start with: ./run-sim.sh"
    exit 1
fi

# Test Mock GitHub Server
test_api "Mock GitHub Health Check" \
    "curl -s '$MOCK_GITHUB_URL/health'" \
    "200" \
    "github-simulation"

test_api "OAuth Authorize Page" \
    "curl -s '$MOCK_GITHUB_URL/login/oauth/authorize?client_id=test&state=test123'" \
    "200" \
    "Mock GitHub Login"

# Generate a test code
TEST_CODE="test_$(date +%s)"
test_api "Code Registration" \
    "curl -s -X POST '$MOCK_GITHUB_URL/api/_sim/issue-code' -H 'Content-Type: application/json' -d '{\"code\": \"$TEST_CODE\", \"login\": \"tom-sapletta-com\", \"state\": \"test123\"}'" \
    "200" \
    "ok"

test_api "Token Exchange" \
    "curl -s -X POST '$MOCK_GITHUB_URL/login/oauth/access_token' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"client_id\": \"Iv1.mock_test_client\", \"client_secret\": \"mock_secret_for_testing\", \"code\": \"$TEST_CODE\"}'" \
    "200" \
    "access_token"

# Extract token for subsequent tests
ACCESS_TOKEN=$(curl -s -X POST "$MOCK_GITHUB_URL/login/oauth/access_token" -H "Content-Type: application/json" -H "Accept: application/json" -d "{\"client_id\": \"Iv1.mock_test_client\", \"client_secret\": \"mock_secret_for_testing\", \"code\": \"$TEST_CODE\"}" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

test_api "User Profile" \
    "curl -s '$MOCK_GITHUB_URL/user' -H 'Authorization: Bearer $ACCESS_TOKEN'" \
    "200" \
    "tom-sapletta-com"

test_api "User Repositories" \
    "curl -s '$MOCK_GITHUB_URL/user/repos' -H 'Authorization: Bearer $ACCESS_TOKEN'" \
    "200" \
    "semcod"

# Test Backend OAuth
test_api "Backend OAuth Start" \
    "curl -s -w '%{http_code}' '$BACKEND_URL/auth/github' | tail -c 3" \
    "307" \
    ""

test_api "Backend OAuth Callback" \
    "curl -s -w '%{http_code}' '$BACKEND_URL/auth/callback?code=$TEST_CODE' | tail -c 3" \
    "307" \
    ""

# Test Error Cases
test_api "Invalid Code Error" \
    "curl -s -w '%{http_code}' -X POST '$MOCK_GITHUB_URL/login/oauth/access_token' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"client_id\": \"Iv1.mock_test_client\", \"client_secret\": \"mock_secret_for_testing\", \"code\": \"invalid_code\"}' | tail -c 3" \
    "400" \
    ""

test_api "Invalid Token Error" \
    "curl -s -w '%{http_code}' '$MOCK_GITHUB_URL/user' -H 'Authorization: Bearer invalid_token' | tail -c 3" \
    "401" \
    ""

test_api "Unauthorized API Access" \
    "curl -s -w '%{http_code}' '$BACKEND_URL/api/me' | tail -c 3" \
    "401" \
    ""

# Print results
echo ""
echo "=================================================="
echo "📊 Test Results Summary"
echo "=================================================="
echo "Total Tests: $TESTS_TOTAL"
echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"
SUCCESS_RATE=$(echo "scale=1; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc -l 2>/dev/null || echo "0")
echo "Success Rate: ${SUCCESS_RATE}%"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}All tests passed! The GitHub OAuth simulation is working correctly.${NC}"
else
    echo -e "\n⚠️  ${YELLOW}Some tests failed. Please check the configuration and logs.${NC}"
fi

echo ""
echo "🔗 Quick Links:"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
echo "Mock GitHub: $MOCK_GITHUB_URL"

echo ""
echo "🔍 Debugging Commands:"
echo "Check mock server: curl $MOCK_GITHUB_URL/health"
echo "Test OAuth redirect: curl -v '$BACKEND_URL/auth/github'"
echo "View backend logs: docker compose logs backend"
echo "Restart services: docker compose restart"

exit $TESTS_FAILED
