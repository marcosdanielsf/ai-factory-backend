#!/bin/bash
# ============================================
# AI Factory Testing Framework - API Test
# ============================================

API_KEY="your-secret-api-key-here-change-me"
BASE_URL="http://localhost:8000"

echo "🧪 Testing AI Factory API..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test 1: Health Check
echo -e "${BLUE}📍 Test 1: Health Check${NC}"
curl -s "${BASE_URL}/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Protected endpoint without API key (should fail)
echo -e "${BLUE}📍 Test 2: Protected endpoint WITHOUT API key (should fail)${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/agents")
if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo -e "${GREEN}✅ PASS: Correctly rejected (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FAIL: Expected 401/403, got HTTP $HTTP_CODE${NC}"
fi
echo ""

# Test 3: List agents with API key
echo -e "${BLUE}📍 Test 3: List Agents${NC}"
curl -s -X GET "${BASE_URL}/api/agents?limit=5" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""
echo ""

# Test 4: Get agent details (replace with real UUID)
echo -e "${BLUE}📍 Test 4: Get Agent Details${NC}"
echo "⚠️  Replace AGENT_UUID with real agent ID"
AGENT_UUID="00000000-0000-0000-0000-000000000000"
curl -s -X GET "${BASE_URL}/api/agent/${AGENT_UUID}" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" | python3 -m json.tool || echo "No agent found (expected)"
echo ""
echo ""

# Test 5: Queue a test (replace with real UUID)
echo -e "${BLUE}📍 Test 5: Queue Agent Test${NC}"
echo "⚠️  Replace AGENT_UUID with real agent ID"
curl -s -X POST "${BASE_URL}/api/test-agent" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_version_id": "00000000-0000-0000-0000-000000000000"
  }' | python3 -m json.tool || echo "No agent found (expected)"
echo ""
echo ""

# Test 6: Create skill (replace with real UUID)
echo -e "${BLUE}📍 Test 6: Create/Update Skill${NC}"
echo "⚠️  Replace AGENT_UUID with real agent ID"
curl -s -X POST "${BASE_URL}/api/agent/${AGENT_UUID}/skill" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "# Test Skill\n\nYou are a test agent.",
    "examples": "Example 1: Hello -> Hi there!",
    "rubric": "1. Completeness\n2. Tone\n3. Engagement",
    "test_cases": [
      {
        "name": "Test case 1",
        "input": "Hello",
        "expected_behavior": "Friendly greeting"
      }
    ]
  }' | python3 -m json.tool || echo "No agent found (expected)"
echo ""
echo ""

# Test 7: Get test history
echo -e "${BLUE}📍 Test 7: Get Test History${NC}"
curl -s -X GET "${BASE_URL}/api/agent/${AGENT_UUID}/tests?limit=5" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" | python3 -m json.tool || echo "No agent found (expected)"
echo ""
echo ""

echo -e "${GREEN}✅ API tests completed!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Update API_KEY in .env file"
echo "2. Update AGENT_UUID in this script with real agent ID"
echo "3. Run: ./test_api.sh"
