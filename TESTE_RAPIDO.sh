#!/bin/bash
# ============================================
# TESTE RÁPIDO - AI Factory Server
# ============================================

echo "🧪 Testando Server.py..."
echo ""

cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework

# 1. Verificar sintaxe
echo "1️⃣ Verificando sintaxe Python..."
python3 -m py_compile server.py && echo "✅ Sintaxe OK" || echo "❌ Erro de sintaxe"
echo ""

# 2. Testar imports
echo "2️⃣ Testando imports..."
python3 -c "from server import app; print('✅ Imports OK')" || echo "❌ Erro nos imports"
echo ""

# 3. Listar endpoints
echo "3️⃣ Listando endpoints..."
python3 -c "
from server import app
routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        for method in route.methods:
            if method not in ['HEAD', 'OPTIONS']:
                routes.append(f'{method:6} {route.path}')

print(f'Total: {len(set(routes))} endpoints')
for r in sorted(set(routes)):
    print(f'  {r}')
" 2>/dev/null
echo ""

# 4. Verificar arquivos criados
echo "4️⃣ Verificando arquivos criados..."
FILES=(
    "server.py"
    "test_api.sh"
    ".env.example"
    "API_QUICKSTART.md"
    "SERVER_SUMMARY.md"
    "ENTREGA_SERVER_API.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (não encontrado)"
    fi
done
echo ""

# 5. Verificar .env
echo "5️⃣ Verificando configuração..."
if [ -f ".env" ]; then
    echo "  ✅ .env existe"
    if grep -q "SUPABASE_URL" .env && grep -q "API_KEY" .env; then
        echo "  ✅ Variáveis configuradas"
    else
        echo "  ⚠️  Algumas variáveis faltando"
    fi
else
    echo "  ⚠️  .env não encontrado (copie .env.example)"
fi
echo ""

# 6. Verificar virtual env
echo "6️⃣ Verificando virtual environment..."
if [ -d "venv" ]; then
    echo "  ✅ venv existe"
    if [ -f "venv/bin/python" ]; then
        echo "  ✅ Python em venv/bin/python"
    fi
else
    echo "  ❌ venv não encontrado"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PRÓXIMOS PASSOS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Configure .env:"
echo "   cp .env.example .env && nano .env"
echo ""
echo "2. Ative virtual env:"
echo "   source venv/bin/activate"
echo ""
echo "3. Inicie o servidor:"
echo "   python server.py"
echo ""
echo "4. Acesse documentação:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Teste API:"
echo "   ./test_api.sh"
echo ""
