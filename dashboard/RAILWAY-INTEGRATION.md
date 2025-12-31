# 🚂 Railway API Integration Guide

## Dashboard Next.js → Railway API → Supabase Database

---

## 📋 Status: Checklist de Integração

### 1. Identificação dos Arquivos que Chamam a API
- ✅ **`src/lib/api.ts`** - Cliente principal da API
  - `testAgent()` - Inicia teste de agente
  - `getTestStatus()` - Verifica status do teste
  - `cancelTest()` - Cancela teste em execução

- ✅ **`src/hooks/useAgents.ts`** - React Query hooks
  - `useTestAgent()` - Mutation para testar agente
  - Integra com `api.ts` para executar testes

- ✅ **`src/lib/supabaseData.ts`** - Acesso direto ao Supabase
  - NÃO usa Railway API
  - Acessa views do Supabase diretamente

### 2. Páginas que Consomem a API
- ✅ **`src/app/agents/page-supabase.tsx`** - Botão "Run Test"
- ✅ **`src/app/page-supabase.tsx`** - Dashboard com realtime updates

---

## 🔧 Template de Configuração

### Arquivo: `.env.local`
```bash
# Supabase (já configurado)
NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao

# Railway API
NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app
API_KEY=sua-api-key-segura
```

### Arquivo já existente: `.env.production`
```bash
NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmdW15d3Z3dWJ2ZXJudmhqZWhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDM3OTksImV4cCI6MjA2Njk3OTc5OX0.60VyeZ8XaD6kz7Eh5Ov_nEeDtu5woMwMJYgUM-Sruao
NEXT_PUBLIC_API_URL=https://ai-factory-api.railway.app
```

---

## 📁 Arquivos que Usam Environment Variables

### 1. `src/lib/api.ts`
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.API_KEY || 'dev-secret-key'

export async function testAgent(request: TestAgentRequest): Promise<TestAgentResponse> {
  const response = await fetch(`${API_URL}/api/test-agent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify(request),
  })
  // ...
}
```

**Endpoints usados:**
- `POST ${API_URL}/api/test-agent`
- `GET ${API_URL}/api/test-status/:testId`
- `POST ${API_URL}/api/test-cancel/:testId`

---

## 🎯 Como Configurar no Vercel

### Opção 1: Via Dashboard
1. Acesse https://vercel.com/dashboard
2. Selecione seu projeto
3. Vá em **Settings** → **Environment Variables**
4. Adicione as seguintes variáveis:

| Nome | Valor | Ambientes |
|------|-------|-----------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://bfumywvwubvernvhjehk.supabase.co` | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development |
| `NEXT_PUBLIC_API_URL` | `https://seu-projeto.railway.app` | Production |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Development |
| `API_KEY` | `sua-api-key-segura` | Production, Preview, Development |

5. Clique em **Save**
6. Faça um **Redeploy** do projeto

### Opção 2: Via Vercel CLI
```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Adicionar variáveis de ambiente
vercel env add NEXT_PUBLIC_API_URL production
# Cole: https://seu-projeto.railway.app

vercel env add API_KEY production
# Cole: sua-api-key-segura

# Fazer deploy
vercel --prod
```

---

## 🧪 Scripts de Validação

### Script 1: Testar conexão local
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard

# 1. Verificar env vars
cat .env.local

# 2. Rodar dashboard
npm run dev

# 3. Abrir no browser
open http://localhost:3000

# 4. Testar endpoints manualmente
# - Ir em /agents
# - Clicar em "Run Test" em um agente
# - Verificar console do browser (F12)
# - Deve aparecer log da chamada API
```

### Script 2: Testar API Railway
```bash
# Testar se API Railway está no ar
curl https://seu-projeto.railway.app/health

# Testar endpoint de teste
curl -X POST https://seu-projeto.railway.app/api/test-agent \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "agent_version_id": "uuid-teste",
    "test_mode": "quick",
    "reflection_enabled": false
  }'
```

---

## 🔄 Fluxo de Dados

```
┌──────────────────────────────────────────────────────────────┐
│                    DASHBOARD NEXT.JS (Vercel)                │
│                                                              │
│  User clicks "Run Test"                                      │
│         ↓                                                    │
│  useTestAgent() hook                                         │
│         ↓                                                    │
│  testAgent() from api.ts                                     │
│         ↓                                                    │
│  POST https://seu-projeto.railway.app/api/test-agent         │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                    RAILWAY API (Python/FastAPI)              │
│                                                              │
│  1. Recebe request com agent_version_id                      │
│  2. Valida API_KEY                                           │
│  3. Consulta Supabase para pegar contexto do agente          │
│  4. Chama Anthropic Claude API                               │
│  5. Executa testes                                           │
│  6. Salva resultados no Supabase                             │
│  7. Retorna test_id e status                                 │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                    SUPABASE DATABASE                         │
│                                                              │
│  Tables:                                                     │
│  - agenttest_test_results (novo resultado)                   │
│  - agenttest_agents (atualiza last_tested_at)                │
│                                                              │
│  Views auto-update:                                          │
│  - vw_agent_performance_summary                              │
│  - vw_latest_test_results                                    │
│  - vw_test_results_history                                   │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│               DASHBOARD (Realtime Update)                    │
│                                                              │
│  Supabase Realtime subscription detecta mudança              │
│         ↓                                                    │
│  React Query invalida cache                                  │
│         ↓                                                    │
│  Dashboard recarrega dados automaticamente                   │
│         ↓                                                    │
│  Score atualizado aparece para o usuário                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Erro: "Failed to fetch"
```
TypeError: Failed to fetch
```
**Causa**: Railway API não está respondendo ou URL incorreta

**Solução**:
1. Verificar se Railway API está no ar:
   ```bash
   curl https://seu-projeto.railway.app/health
   ```
2. Verificar variável `NEXT_PUBLIC_API_URL` no Vercel
3. Verificar logs do Railway: `railway logs`

---

### Erro: "CORS blocked"
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS
```
**Causa**: Railway API não permite origem do Vercel

**Solução**: Adicionar CORS no backend Railway:
```python
# main.py (FastAPI)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://seu-dashboard.vercel.app",
        "https://*.vercel.app"  # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Erro: "Unauthorized" (401)
```
Error: Failed to start test: HTTP 401
```
**Causa**: API_KEY inválida ou ausente

**Solução**:
1. Verificar variável `API_KEY` no Vercel
2. Verificar se backend Railway está validando corretamente
3. Usar a mesma chave em ambos os lados

---

### Erro: "Environment variable not defined"
```
NEXT_PUBLIC_API_URL is undefined
```
**Causa**: Variáveis não carregadas

**Solução**:
1. Reiniciar servidor dev: `npm run dev`
2. Limpar cache: `rm -rf .next`
3. Verificar `.env.local` existe
4. Variáveis `NEXT_PUBLIC_*` devem começar com esse prefixo

---

### Dados não atualizam após teste
**Causa**: Realtime não configurado ou cache não invalida

**Solução**:
1. Verificar se `useRealtimeTestUpdates()` está sendo chamado
2. Verificar console do browser para erros
3. Force refresh: `queryClient.invalidateQueries(['agents'])`

---

## 📊 Validação de Conexão

### Checklist de Testes
- [ ] Railway API responde em `/health`
- [ ] Railway API aceita requisições do Vercel (CORS OK)
- [ ] Supabase retorna dados nas views
- [ ] Dashboard carrega stats corretamente
- [ ] Botão "Run Test" funciona
- [ ] Loading state aparece durante teste
- [ ] Score atualiza após teste completar
- [ ] Realtime updates funcionam
- [ ] Erros são tratados com mensagens claras

### Como Testar Cada Item
```bash
# 1. Health check
curl https://seu-projeto.railway.app/health
# Esperado: 200 OK

# 2. CORS (via browser DevTools)
# Abrir https://seu-dashboard.vercel.app
# F12 → Network → Verificar headers de resposta
# Esperado: Access-Control-Allow-Origin: *

# 3. Supabase
# Abrir Supabase Dashboard → Table Editor
# Verificar se vw_agent_performance_summary tem dados

# 4. Dashboard stats
# Abrir https://seu-dashboard.vercel.app
# Verificar se números aparecem nos cards

# 5. Botão "Run Test"
# Clicar em "Run Test"
# Verificar alert de sucesso
# Verificar console: POST /api/test-agent → 200 OK

# 6. Loading state
# Deve aparecer spinner durante teste

# 7. Score update
# Aguardar ~30s após teste
# Recarregar página
# Verificar novo score

# 8. Realtime
# Abrir 2 abas do dashboard
# Fazer teste em uma
# Verificar se a outra atualiza

# 9. Error handling
# Parar Railway API
# Tentar fazer teste
# Verificar mensagem de erro clara
```

---

## 🚀 Deploy Checklist

### Antes do Deploy
- [ ] Código testado localmente
- [ ] `.env.production` configurado
- [ ] Railway API está no ar
- [ ] Supabase migrations executadas
- [ ] CORS configurado no backend

### Durante o Deploy (Vercel)
- [ ] Environment variables adicionadas
- [ ] Build passa sem erros
- [ ] Preview deployment funciona
- [ ] Production deployment funciona

### Após o Deploy
- [ ] Testar URL de produção
- [ ] Verificar que API Railway responde
- [ ] Verificar que dados carregam
- [ ] Testar botão "Run Test"
- [ ] Verificar logs no Vercel
- [ ] Verificar logs no Railway

---

## 📞 Suporte

**Arquivos importantes:**
- `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/lib/api.ts`
- `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/hooks/useAgents.ts`
- `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/INTEGRATION-GUIDE.md`

**Comandos úteis:**
```bash
# Ver logs do Vercel
vercel logs

# Ver logs do Railway
railway logs

# Testar API local
npm run dev

# Build local
npm run build
```

---

**Status**: ✅ Documentação completa
**Próximo passo**: Configurar URL Railway e testar integração!
