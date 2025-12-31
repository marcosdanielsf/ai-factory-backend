#!/bin/bash

# =============================================================================
# AI Factory Testing Framework - Railway API Test Script
# =============================================================================
# Este script testa todos os endpoints principais da API no Railway
#
# Uso:
#   1. Edite as variáveis API_URL e API_KEY abaixo
#   2. chmod +x test-railway-api.sh
#   3. ./test-railway-api.sh
# =============================================================================

# CONFIGURAÇÃO - EDITE AQUI
API_URL="https://SEU-PROJETO.railway.app"
API_KEY="your-custom-api-key"  # Opcional: só se configurou API_KEY

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local headers="$4"
    local data="$5"

    echo -e "${BLUE}Testing: $name${NC}"
    echo "Endpoint: $method $endpoint"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" $headers "$endpoint")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X $method $headers -d "$data" "$endpoint")
    fi

    http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')

    if [ "$http_status" -ge 200 ] && [ "$http_status" -lt 300 ]; then
        echo -e "${GREEN}✅ SUCCESS (HTTP $http_status)${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ FAILED (HTTP $http_status)${NC}"
        echo "$body"
    fi

    echo ""
}

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq não está instalado. Instale para melhor formatação JSON:${NC}"
    echo "brew install jq"
    echo ""
fi

# Validar configuração
if [ "$API_URL" = "https://SEU-PROJETO.railway.app" ]; then
    echo -e "${RED}❌ ERRO: Edite a variável API_URL no script!${NC}"
    exit 1
fi

echo "======================================================================"
echo "🧪 AI FACTORY TESTING FRAMEWORK - RAILWAY API TESTS"
echo "======================================================================"
echo "URL Base: $API_URL"
echo "API Key: ${API_KEY:0:10}..." # Mostra só primeiros 10 chars
echo "Data: $(date)"
echo ""
echo "======================================================================"
echo ""

# =============================================================================
# TESTES PÚBLICOS (sem autenticação)
# =============================================================================

echo -e "${YELLOW}📍 SEÇÃO 1: Endpoints Públicos${NC}"
echo ""

# 1. Health Check
test_endpoint \
    "Health Check" \
    "GET" \
    "$API_URL/health" \
    ""

# 2. Ping
test_endpoint \
    "Ping" \
    "GET" \
    "$API_URL/ping" \
    ""

# 3. OpenAPI Docs
test_endpoint \
    "API Documentation (OpenAPI)" \
    "GET" \
    "$API_URL/docs" \
    ""

# 4. OpenAPI JSON Schema
test_endpoint \
    "OpenAPI Schema" \
    "GET" \
    "$API_URL/openapi.json" \
    ""

# =============================================================================
# TESTES PROTEGIDOS (com autenticação)
# =============================================================================

echo -e "${YELLOW}📍 SEÇÃO 2: Endpoints Protegidos (com API Key)${NC}"
echo ""

# 5. List Agents
test_endpoint \
    "List Agents" \
    "GET" \
    "$API_URL/api/v1/agents" \
    "-H 'X-API-Key: $API_KEY'"

# 6. Metrics
test_endpoint \
    "System Metrics" \
    "GET" \
    "$API_URL/api/v1/metrics" \
    "-H 'X-API-Key: $API_KEY'"

# =============================================================================
# TESTES DE POST (requerem dados válidos)
# =============================================================================

echo -e "${YELLOW}📍 SEÇÃO 3: Endpoints POST (exemplos)${NC}"
echo ""

# Nota: Estes endpoints vão falhar se não houver dados válidos no banco
# São apenas para verificar se a API está aceitando requests

# 7. Test Run (vai falhar sem agent_version_id válido)
echo -e "${BLUE}Testing: Run Test (exemplo - pode falhar sem dados válidos)${NC}"
test_endpoint \
    "Run Test (expecting validation error)" \
    "POST" \
    "$API_URL/api/v1/test/run" \
    "-H 'X-API-Key: $API_KEY' -H 'Content-Type: application/json'" \
    '{"agent_version_id": "00000000-0000-0000-0000-000000000000"}'

# 8. Batch Test
echo -e "${BLUE}Testing: Batch Test (exemplo - pode falhar sem dados válidos)${NC}"
test_endpoint \
    "Batch Test (expecting validation error)" \
    "POST" \
    "$API_URL/api/v1/test/batch" \
    "-H 'X-API-Key: $API_KEY' -H 'Content-Type: application/json'" \
    '{"agent_version_ids": ["00000000-0000-0000-0000-000000000000"]}'

# =============================================================================
# TESTES DE PERFORMANCE
# =============================================================================

echo -e "${YELLOW}📍 SEÇÃO 4: Performance Tests${NC}"
echo ""

echo -e "${BLUE}Testing: Response Time for /health${NC}"
START=$(date +%s%N)
curl -s -o /dev/null "$API_URL/health"
END=$(date +%s%N)
ELAPSED=$(echo "scale=2; ($END - $START) / 1000000" | bc)

if (( $(echo "$ELAPSED < 100" | bc -l) )); then
    echo -e "${GREEN}✅ Response time: ${ELAPSED}ms (EXCELENTE)${NC}"
elif (( $(echo "$ELAPSED < 500" | bc -l) )); then
    echo -e "${YELLOW}⚠️  Response time: ${ELAPSED}ms (ACEITÁVEL)${NC}"
else
    echo -e "${RED}❌ Response time: ${ELAPSED}ms (LENTO)${NC}"
fi
echo ""

# =============================================================================
# TESTES DE CONECTIVIDADE
# =============================================================================

echo -e "${YELLOW}📍 SEÇÃO 5: Connectivity Tests${NC}"
echo ""

echo -e "${BLUE}Testing: SSL/TLS Certificate${NC}"
if curl -s --head "$API_URL" | grep -q "HTTP/.*200"; then
    echo -e "${GREEN}✅ HTTPS working${NC}"
else
    echo -e "${RED}❌ HTTPS not working${NC}"
fi
echo ""

echo -e "${BLUE}Testing: CORS Headers${NC}"
cors_headers=$(curl -s -I -X OPTIONS "$API_URL/health" | grep -i "access-control")
if [ -n "$cors_headers" ]; then
    echo -e "${GREEN}✅ CORS configured${NC}"
    echo "$cors_headers"
else
    echo -e "${YELLOW}⚠️  CORS headers not found${NC}"
fi
echo ""

# =============================================================================
# RESUMO
# =============================================================================

echo "======================================================================"
echo -e "${GREEN}✅ TESTES CONCLUÍDOS${NC}"
echo "======================================================================"
echo ""
echo "Próximos passos recomendados:"
echo ""
echo "1. Se todos os testes públicos passaram:"
echo "   ✅ Seu deploy está funcionando corretamente"
echo ""
echo "2. Se testes protegidos falharam (401/403):"
echo "   ⚠️  Verifique se API_KEY está configurada corretamente"
echo "   ⚠️  Configure: railway variables set API_KEY='sua-chave'"
echo ""
echo "3. Se testes POST falharam (400/422):"
echo "   ℹ️  Normal - requerem dados válidos no Supabase"
echo "   ℹ️  Teste manualmente com agent_version_id real"
echo ""
echo "4. Se response time > 500ms:"
echo "   ⚠️  Considere aumentar recursos no Railway"
echo "   ⚠️  Ou reduzir workers: GUNICORN_WORKERS=2"
echo ""
echo "5. Monitoramento contínuo:"
echo "   📊 Railway Dashboard: railway open"
echo "   📋 Logs ao vivo: railway logs --follow"
echo ""
echo "======================================================================"
echo ""
