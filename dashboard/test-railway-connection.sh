#!/bin/bash

# =============================================================================
# RAILWAY CONNECTION TEST SCRIPT
# =============================================================================
# Este script testa a conexão entre Dashboard Next.js e Railway API
#
# Uso:
#   chmod +x test-railway-connection.sh
#   ./test-railway-connection.sh https://seu-projeto.railway.app sua-api-key
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parâmetros
RAILWAY_URL=${1:-"http://localhost:8000"}
API_KEY=${2:-"dev-secret-key"}

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         RAILWAY CONNECTION TEST - Dashboard Next.js          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Railway URL:${NC} $RAILWAY_URL"
echo -e "${YELLOW}API Key:${NC} ${API_KEY:0:10}..."
echo ""

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4

    echo -e "${BLUE}Testing:${NC} $description"
    echo -e "${YELLOW}  → $method $RAILWAY_URL$endpoint${NC}"

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$RAILWAY_URL$endpoint" \
            -H "X-API-Key: $API_KEY" \
            -H "Content-Type: application/json" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$RAILWAY_URL$endpoint" \
            -H "X-API-Key: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}  ✓ Success${NC} - HTTP $http_code"
        echo -e "${GREEN}    Response:${NC} ${body:0:100}..."
        return 0
    elif [ "$http_code" -ge 400 ] && [ "$http_code" -lt 500 ]; then
        echo -e "${RED}  ✗ Client Error${NC} - HTTP $http_code"
        echo -e "${RED}    Response:${NC} $body"
        return 1
    elif [ "$http_code" -ge 500 ]; then
        echo -e "${RED}  ✗ Server Error${NC} - HTTP $http_code"
        echo -e "${RED}    Response:${NC} $body"
        return 1
    else
        echo -e "${RED}  ✗ Connection Failed${NC}"
        echo -e "${RED}    Error:${NC} $response"
        return 1
    fi

    echo ""
}

# =============================================================================
# TESTES
# =============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}1. HEALTH CHECK${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

test_endpoint "GET" "/health" "Health check endpoint" || echo -e "${YELLOW}  ⚠ Health endpoint may not exist${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}2. API ENDPOINTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Test data
TEST_DATA='{
  "agent_version_id": "test-uuid-123",
  "test_mode": "quick",
  "reflection_enabled": false
}'

test_endpoint "POST" "/api/test-agent" "Start test endpoint" "$TEST_DATA"
echo ""

# Se conseguiu criar teste, tentar pegar status
if [ $? -eq 0 ]; then
    echo -e "${BLUE}Testing:${NC} Get test status"
    test_endpoint "GET" "/api/test-status/test-uuid-123" "Get test status"
    echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}3. CORS CHECK${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Testing:${NC} CORS headers"
cors_response=$(curl -s -I -X OPTIONS "$RAILWAY_URL/api/test-agent" \
    -H "Origin: https://your-app.vercel.app" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: X-API-Key, Content-Type" 2>&1)

if echo "$cors_response" | grep -qi "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}  ✓ CORS configured${NC}"
    echo -e "${GREEN}    $(echo "$cors_response" | grep -i "Access-Control-Allow-Origin")${NC}"
else
    echo -e "${RED}  ✗ CORS not configured${NC}"
    echo -e "${YELLOW}    Configure CORS in your Railway API to allow Vercel origins${NC}"
fi
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}4. ENVIRONMENT CHECK${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f ".env.local" ]; then
    echo -e "${GREEN}  ✓ .env.local exists${NC}"

    if grep -q "NEXT_PUBLIC_API_URL" .env.local; then
        current_url=$(grep "NEXT_PUBLIC_API_URL" .env.local | cut -d '=' -f2)
        echo -e "${GREEN}    NEXT_PUBLIC_API_URL=${NC}$current_url"

        if [ "$current_url" != "$RAILWAY_URL" ]; then
            echo -e "${YELLOW}    ⚠ Warning: .env.local URL differs from test URL${NC}"
        fi
    else
        echo -e "${RED}    ✗ NEXT_PUBLIC_API_URL not found in .env.local${NC}"
    fi

    if grep -q "API_KEY" .env.local; then
        echo -e "${GREEN}    API_KEY configured${NC}"
    else
        echo -e "${RED}    ✗ API_KEY not found in .env.local${NC}"
    fi
else
    echo -e "${RED}  ✗ .env.local not found${NC}"
    echo -e "${YELLOW}    Create .env.local from .env.railway.template${NC}"
fi
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}5. DASHBOARD LOCAL TEST${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if command -v node &> /dev/null; then
    echo -e "${GREEN}  ✓ Node.js installed${NC}"
    echo -e "${GREEN}    $(node --version)${NC}"
else
    echo -e "${RED}  ✗ Node.js not installed${NC}"
fi

if [ -f "package.json" ]; then
    echo -e "${GREEN}  ✓ package.json found${NC}"

    if [ -d "node_modules" ]; then
        echo -e "${GREEN}  ✓ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}  ⚠ Dependencies not installed${NC}"
        echo -e "${YELLOW}    Run: npm install${NC}"
    fi
else
    echo -e "${RED}  ✗ package.json not found${NC}"
fi
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "  1. ${GREEN}Update .env.local:${NC}"
echo -e "     ${BLUE}NEXT_PUBLIC_API_URL=$RAILWAY_URL${NC}"
echo ""
echo -e "  2. ${GREEN}Test dashboard locally:${NC}"
echo -e "     ${BLUE}npm run dev${NC}"
echo -e "     ${BLUE}open http://localhost:3000${NC}"
echo ""
echo -e "  3. ${GREEN}Configure Vercel env vars:${NC}"
echo -e "     ${BLUE}vercel env add NEXT_PUBLIC_API_URL${NC}"
echo -e "     ${BLUE}vercel env add API_KEY${NC}"
echo ""
echo -e "  4. ${GREEN}Deploy to Vercel:${NC}"
echo -e "     ${BLUE}vercel --prod${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Test completed!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
