# 📁 Referência de Arquivos - API Integration

## Lista Completa de Arquivos que Chamam a Railway API

---

## 🎯 Arquivos Principais

### 1. **`src/lib/api.ts`** - Cliente API Principal
**Localização**: `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/lib/api.ts`

**O que faz**: Cliente HTTP para comunicação com Railway API

**Variáveis de ambiente usadas**:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.API_KEY || 'dev-secret-key'
```

**Funções exportadas**:
```typescript
// 1. Iniciar teste de agente
testAgent(request: TestAgentRequest): Promise<TestAgentResponse>
// → POST ${API_URL}/api/test-agent

// 2. Verificar status do teste
getTestStatus(testId: string): Promise<TestAgentResponse>
// → GET ${API_URL}/api/test-status/:testId

// 3. Cancelar teste
cancelTest(testId: string): Promise<void>
// → POST ${API_URL}/api/test-cancel/:testId
```

**Interfaces**:
```typescript
interface TestAgentRequest {
  agent_version_id: string
  test_mode?: 'full' | 'quick'
  reflection_enabled?: boolean
}

interface TestAgentResponse {
  test_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  message: string
  overall_score?: number
  report_url?: string
}
```

---

### 2. **`src/hooks/useAgents.ts`** - React Query Hooks
**Localização**: `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/hooks/useAgents.ts`

**O que faz**: Hooks customizados para data fetching e mutations

**Importa de**: `src/lib/api.ts`

**Hooks que usam API**:
```typescript
// Mutation para testar agente
useTestAgent()
// → Chama testAgent() do api.ts
// → Invalida queries após sucesso
```

**Outros hooks** (NÃO usam Railway API, usam Supabase direto):
- `useAgents()` - Lista agentes
- `useAgent()` - Detalhes de agente
- `useLatestTestResults()` - Últimos testes
- `useTestHistory()` - Histórico de testes

---

### 3. **`src/lib/supabaseData.ts`** - Supabase Client
**Localização**: `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/lib/supabaseData.ts`

**O que faz**: Acesso direto ao Supabase (NÃO USA RAILWAY API)

**Variáveis de ambiente usadas**:
```typescript
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
```

**⚠️ IMPORTANTE**: Este arquivo acessa Supabase diretamente, sem passar pela Railway API.

---

## 📄 Páginas que Consomem a API

### 1. **`src/app/agents/page-supabase.tsx`**
**Localização**: `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/agents/page-supabase.tsx`

**O que faz**: Página de listagem de agentes com botão "Run Test"

**Usa**:
```typescript
import { useTestAgent } from '@/hooks/useAgents'

const { mutate: runTest, isPending } = useTestAgent()

// Quando clica em "Run Test"
runTest({
  agent_version_id: agent.agent_version_id,
  test_mode: 'full',
  reflection_enabled: true,
})
```

**Fluxo**:
1. User clica botão "Run Test"
2. Chama `runTest()`
3. Hook `useTestAgent()` chama `testAgent()` do `api.ts`
4. `api.ts` faz POST para Railway API
5. Railway retorna `test_id`
6. Alert mostra confirmação
7. Queries são invalidadas
8. Dados recarregam automaticamente

---

### 2. **`src/app/page-supabase.tsx`**
**Localização**: `/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/page-supabase.tsx`

**O que faz**: Dashboard principal

**Usa**: Somente Supabase direto (não usa Railway API)

**Realtime updates**:
```typescript
useRealtimeTestUpdates() // Monitora mudanças na tabela agenttest_test_results
```

---

## 🔄 Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────┐
│                  USER INTERFACE                             │
│                                                             │
│  src/app/agents/page-supabase.tsx                           │
│         ↓                                                   │
│  Button "Run Test" clicked                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  REACT QUERY LAYER                          │
│                                                             │
│  src/hooks/useAgents.ts                                     │
│         ↓                                                   │
│  useTestAgent() mutation                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  API CLIENT LAYER                           │
│                                                             │
│  src/lib/api.ts                                             │
│         ↓                                                   │
│  testAgent(request)                                         │
│         ↓                                                   │
│  fetch(${API_URL}/api/test-agent, {                         │
│    method: 'POST',                                          │
│    headers: {                                               │
│      'X-API-Key': API_KEY                                   │
│    },                                                       │
│    body: JSON.stringify(request)                            │
│  })                                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  RAILWAY API                                │
│                                                             │
│  POST /api/test-agent                                       │
│         ↓                                                   │
│  Validates API_KEY                                          │
│  Starts test in background                                  │
│  Returns test_id                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  SUPABASE DATABASE                          │
│                                                             │
│  INSERT INTO agenttest_test_results                         │
│  UPDATE agenttest_agents                                    │
│         ↓                                                   │
│  Triggers Realtime event                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  DASHBOARD (Realtime)                       │
│                                                             │
│  useRealtimeTestUpdates() detecta mudança                   │
│         ↓                                                   │
│  React Query invalida cache                                 │
│         ↓                                                   │
│  Dashboard recarrega dados automaticamente                  │
│         ↓                                                   │
│  UI atualiza com novo score                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Endpoints Railway API

### 1. **POST /api/test-agent**
**Descrição**: Inicia teste de um agente

**Headers**:
```
Content-Type: application/json
X-API-Key: {API_KEY}
```

**Body**:
```json
{
  "agent_version_id": "uuid-do-agente",
  "test_mode": "full",
  "reflection_enabled": true
}
```

**Response (200)**:
```json
{
  "test_id": "uuid-do-teste",
  "status": "queued",
  "message": "Test started successfully"
}
```

**Response (400)**:
```json
{
  "message": "Invalid agent_version_id"
}
```

**Response (401)**:
```json
{
  "message": "Invalid API key"
}
```

---

### 2. **GET /api/test-status/:testId**
**Descrição**: Verifica status de um teste

**Headers**:
```
X-API-Key: {API_KEY}
```

**Response (200)**:
```json
{
  "test_id": "uuid-do-teste",
  "status": "running",
  "message": "Test in progress",
  "overall_score": null,
  "report_url": null
}
```

**Response quando completo**:
```json
{
  "test_id": "uuid-do-teste",
  "status": "completed",
  "message": "Test completed",
  "overall_score": 8.5,
  "report_url": "https://..."
}
```

---

### 3. **POST /api/test-cancel/:testId**
**Descrição**: Cancela teste em execução

**Headers**:
```
X-API-Key: {API_KEY}
```

**Response (200)**:
```json
{
  "message": "Test cancelled successfully"
}
```

---

## 🔑 Environment Variables Necessárias

### Dashboard (Next.js)
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Railway API
NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app
API_KEY=sua-api-key-segura
```

### Railway API (Backend)
```bash
# Supabase
SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Auth
API_KEY=sua-api-key-segura
```

---

## 📝 Resumo de Arquivos

| Arquivo | Função | Usa Railway API | Usa Supabase |
|---------|--------|-----------------|--------------|
| `src/lib/api.ts` | Cliente HTTP | ✅ | ❌ |
| `src/hooks/useAgents.ts` | React Query hooks | ✅ (via api.ts) | ✅ |
| `src/lib/supabaseData.ts` | Data fetchers | ❌ | ✅ |
| `src/app/agents/page-supabase.tsx` | UI de agentes | ✅ (via hooks) | ✅ |
| `src/app/page-supabase.tsx` | Dashboard | ❌ | ✅ |

---

## 🔍 Como Debugar

### 1. Verificar chamadas API no Browser
```javascript
// F12 → Console
// Filtrar por: /api/test-agent

// Ver request
console.log('Request:', {
  url: 'https://seu-projeto.railway.app/api/test-agent',
  method: 'POST',
  headers: {
    'X-API-Key': '***'
  },
  body: { agent_version_id: '...' }
})

// Ver response
console.log('Response:', response)
```

### 2. Ver logs do Railway
```bash
railway logs --follow
```

### 3. Ver logs do Vercel
```bash
vercel logs --follow
```

### 4. Testar endpoint manualmente
```bash
curl -X POST https://seu-projeto.railway.app/api/test-agent \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-api-key" \
  -d '{
    "agent_version_id": "uuid-teste",
    "test_mode": "quick",
    "reflection_enabled": false
  }' \
  -v
```

---

## ✅ Checklist de Validação

- [ ] `src/lib/api.ts` existe
- [ ] `NEXT_PUBLIC_API_URL` configurada
- [ ] `API_KEY` configurada
- [ ] Railway API responde em `/health`
- [ ] CORS configurado no Railway
- [ ] Botão "Run Test" funciona
- [ ] Alert de sucesso aparece
- [ ] Dados atualizam após teste

---

**Documentação completa dos arquivos que interagem com Railway API**
