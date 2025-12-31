# Teste de Integração Supabase

## Como testar a integração

### 1. Verificar conexão com Supabase

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
node -e "
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(
  'https://bfumywvwubvernvhjehk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao'
);

async function test() {
  const { data, error } = await supabase
    .from('vw_agent_performance_summary')
    .select('agent_name, last_test_score')
    .limit(5);

  if (error) {
    console.error('❌ Error:', error.message);
  } else {
    console.log('✅ Connected! Found', data?.length, 'agents');
    console.log(JSON.stringify(data, null, 2));
  }
}

test();
"
```

### 2. Rodar o dashboard

```bash
npm run dev
```

Abra: http://localhost:3000

### 3. Verificar páginas

1. **Dashboard Principal** (http://localhost:3000)
   - Deve mostrar stats cards com dados reais
   - Gráfico de score history
   - Lista de agentes recentes

2. **Página de Agentes** (http://localhost:3000/agents)
   - Grid de agentes
   - Busca funcionando
   - Filtros de status
   - Botão "Run Test" (irá falhar se API não estiver rodando)

### 4. Testar botão "Run Test"

Para que funcione, você precisa ter um backend API rodando em `localhost:8000`.

Se não tiver, você verá um erro - isso é esperado.

### 5. Ativar páginas com Supabase

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# Backup
cp src/app/page.tsx src/app/page-mock.tsx.backup
cp src/app/agents/page.tsx src/app/agents/page-mock.tsx.backup

# Ativar Supabase
mv src/app/page.tsx src/app/page-mock.tsx
mv src/app/page-supabase.tsx src/app/page.tsx

mv src/app/agents/page.tsx src/app/agents/page-mock.tsx
mv src/app/agents/page-supabase.tsx src/app/agents/page.tsx
```

Agora as páginas principais usarão dados reais do Supabase!

### 6. Reverter para mock (se necessário)

```bash
mv src/app/page.tsx src/app/page-supabase.tsx
mv src/app/page-mock.tsx src/app/page.tsx

mv src/app/agents/page.tsx src/app/agents/page-supabase.tsx
mv src/app/agents/page-mock.tsx src/app/agents/page.tsx
```

---

## Checklist

- [ ] Supabase conectado (teste node acima)
- [ ] Dashboard carregou sem erros
- [ ] Stats cards aparecem com dados
- [ ] Página de agentes mostra grid
- [ ] Busca funciona
- [ ] Filtros funcionam
- [ ] Botão "Run Test" aparece (pode dar erro se API não estiver rodando)

---

## Próximos passos

1. Se quiser testar o botão "Run Test", você precisa:
   - Ter um backend API rodando em localhost:8000
   - Endpoint: POST /api/test-agent
   - Headers: X-API-Key: dev-secret-key

2. Para criar o backend, você pode usar:
   - FastAPI (Python)
   - Express (Node.js)
   - Qualquer framework que aceite POST requests

---

Tudo pronto! 🎉
