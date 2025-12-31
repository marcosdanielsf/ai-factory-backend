#!/bin/bash

echo "🚀 AI Factory Dashboard - Quick Start"
echo "===================================="
echo ""

cd "$(dirname "$0")"

echo "📦 Verificando dependências..."
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules não encontrado. Rodando npm install..."
    npm install
fi

echo ""
echo "✅ Dependências OK!"
echo ""

echo "🔧 Opções:"
echo ""
echo "1) Rodar dashboard com mock data (padrão)"
echo "2) Rodar dashboard com Supabase (dados reais)"
echo "3) Testar conexão com Supabase"
echo "4) Build de produção"
echo ""

read -p "Escolha uma opção (1-4): " option

case $option in
    1)
        echo ""
        echo "🎯 Rodando com mock data..."
        npm run dev
        ;;
    2)
        echo ""
        echo "🔄 Ativando páginas com Supabase..."
        
        # Backup
        [ -f src/app/page.tsx ] && mv src/app/page.tsx src/app/page-mock.tsx
        [ -f src/app/agents/page.tsx ] && mv src/app/agents/page.tsx src/app/agents/page-mock.tsx
        
        # Ativar Supabase
        [ -f src/app/page-supabase.tsx ] && mv src/app/page-supabase.tsx src/app/page.tsx
        [ -f src/app/agents/page-supabase.tsx ] && mv src/app/agents/page-supabase.tsx src/app/agents/page.tsx
        
        echo "✅ Supabase ativado!"
        echo ""
        echo "🎯 Rodando com dados reais do Supabase..."
        npm run dev
        ;;
    3)
        echo ""
        echo "🔍 Testando conexão com Supabase..."
        node -e "
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(
  'https://bfumywvwubvernvhjehk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao'
);

async function test() {
  console.log('🔌 Conectando...');
  const { data, error } = await supabase
    .from('vw_agent_performance_summary')
    .select('agent_name, last_test_score')
    .limit(5);

  if (error) {
    console.error('❌ Erro:', error.message);
  } else {
    console.log('✅ Conectado! Encontrados', data?.length, 'agentes');
    console.log(JSON.stringify(data, null, 2));
  }
}

test();
"
        ;;
    4)
        echo ""
        echo "🏗️  Build de produção..."
        npm run build
        echo ""
        echo "✅ Build concluído!"
        echo ""
        echo "Para rodar em produção:"
        echo "  npm run start"
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac
