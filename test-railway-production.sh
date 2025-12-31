#!/bin/bash

# Script para testar o backend Railway em produção
# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testando Backend Railway em Produção"
echo "=========================================="
echo ""

# Pedir URL do Railway
echo "Cole a URL do Railway (exemplo: https://web-production-bfcb1.up.railway.app):"
read RAILWAY_URL

# Remover trailing slash se houver
RAILWAY_URL="${RAILWAY_URL%/}"

echo ""
echo "📍 URL testada: $RAILWAY_URL"
echo ""

# Teste 1: Health Check
echo "1️⃣ Testando /health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/health")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passou! (HTTP $HEALTH_RESPONSE)${NC}"
    curl -s "$RAILWAY_URL/health" | jq '.' 2>/dev/null || curl -s "$RAILWAY_URL/health"
else
    echo -e "${RED}❌ Health check falhou! (HTTP $HEALTH_RESPONSE)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 2: API Docs
echo "2️⃣ Testando /docs endpoint..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/docs")

if [ "$DOCS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ API Docs acessível! (HTTP $DOCS_RESPONSE)${NC}"
    echo "   Acesse: $RAILWAY_URL/docs"
else
    echo -e "${RED}❌ API Docs não acessível! (HTTP $DOCS_RESPONSE)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 3: Listar Agentes (Supabase Connection)
echo "3️⃣ Testando conexão com Supabase (GET /api/agents)..."
AGENTS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$RAILWAY_URL/api/agents")
HTTP_CODE=$(echo "$AGENTS_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
AGENTS_BODY=$(echo "$AGENTS_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Conexão com Supabase OK! (HTTP $HTTP_CODE)${NC}"
    echo ""
    echo "📊 Agentes encontrados:"
    echo "$AGENTS_BODY" | jq -r '.agents[] | "   - \(.name) (v\(.version)) - Score: \(.last_test_score // "N/A")"' 2>/dev/null || echo "$AGENTS_BODY"
else
    echo -e "${RED}❌ Erro ao conectar com Supabase! (HTTP $HTTP_CODE)${NC}"
    echo "$AGENTS_BODY"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 4: Test Agent Endpoint
echo "4️⃣ Testando endpoint de teste (POST /api/test-agent)..."
echo "   (Usando agent_version_id de exemplo)"

# Pegar primeiro agent_id do response anterior
AGENT_ID=$(echo "$AGENTS_BODY" | jq -r '.agents[0].agent_version_id' 2>/dev/null)

if [ -n "$AGENT_ID" ] && [ "$AGENT_ID" != "null" ]; then
    echo "   Agent ID detectado: $AGENT_ID"

    TEST_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
        -X POST "$RAILWAY_URL/api/test-agent" \
        -H "Content-Type: application/json" \
        -d "{
            \"agent_version_id\": \"$AGENT_ID\",
            \"test_mode\": \"quick\",
            \"reflection_enabled\": false
        }")

    TEST_HTTP_CODE=$(echo "$TEST_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    TEST_BODY=$(echo "$TEST_RESPONSE" | sed '/HTTP_CODE:/d')

    if [ "$TEST_HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Endpoint de teste funcionando! (HTTP $TEST_HTTP_CODE)${NC}"
        echo ""
        echo "📋 Resultado do teste:"
        echo "$TEST_BODY" | jq '.' 2>/dev/null || echo "$TEST_BODY"
    else
        echo -e "${YELLOW}⚠️  Endpoint de teste retornou: (HTTP $TEST_HTTP_CODE)${NC}"
        echo "$TEST_BODY"
    fi
else
    echo -e "${YELLOW}⚠️  Pulando teste - nenhum agente encontrado${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Resumo Final
echo "📊 RESUMO DOS TESTES"
echo "===================="
echo ""

PASSED=0
FAILED=0

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Health Check${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Health Check${NC}"
    ((FAILED++))
fi

if [ "$DOCS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ API Docs${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ API Docs${NC}"
    ((FAILED++))
fi

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Supabase Connection${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Supabase Connection${NC}"
    ((FAILED++))
fi

if [ "$TEST_HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Test Agent Endpoint${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Test Agent Endpoint (não testado)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $PASSED -ge 3 ]; then
    echo -e "${GREEN}✅ Backend está funcionando corretamente!${NC}"
    echo ""
    echo "🔗 URLs Importantes:"
    echo "   • Backend: $RAILWAY_URL"
    echo "   • API Docs: $RAILWAY_URL/docs"
    echo "   • Health: $RAILWAY_URL/health"
    echo ""
    echo "📋 Próximo passo: Deploy do Dashboard no Vercel"
else
    echo -e "${RED}❌ Alguns testes falharam. Verifique as variáveis de ambiente no Railway.${NC}"
fi

echo ""
