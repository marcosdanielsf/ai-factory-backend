# 🐛 Bugs Encontrados no Dashboard

**Data:** 31/12/2025 13:45 BRT

---

## Problemas Identificados:

### 1. ❌ Página de Detalhes do Agente (`/agents/[id]`)

**Arquivo:** `src/app/agents/[id]/page.tsx`

**Problema:**
- Usa dados **mockados** (`mockData`) ao invés do Supabase
- Quando clica em um agente na homepage, a página dá erro ou mostra dados fake

**Erro:**
```typescript
// Linha 6 - ERRADO
import { agents, testRuns } from '@/lib/mockData';

// Linha 10 - ERRADO
const agent = agents.find((a) => a.id === params.id);
```

**Solução Necessária:**
- Buscar agente do Supabase usando `agent_version_id`
- Buscar histórico de testes do Supabase
- Remover dependência de `mockData`

---

### 2. ❌ Página de Lista de Testes (`/tests`)

**Arquivo:** `src/app/tests/page.tsx`

**Problema:**
- Usa dados **mockados** (`testRuns`, `agents`) ao invés do Supabase
- Mostra dados fake ao invés dos testes reais

**Erro:**
```typescript
// Linha 10 - ERRADO
import { testRuns, agents } from '@/lib/mockData';

// Linha 20 - ERRADO
const filteredTests = testRuns.filter(...)
```

**Solução Necessária:**
- Buscar todos os test_results do Supabase
- Implementar filtros usando dados reais
- Remover dependência de `mockData`

---

### 3. ✅ Páginas Que Funcionam:

| Página | Status | Observação |
|--------|--------|------------|
| `/` (Homepage) | ✅ OK | Usa Supabase corretamente |
| `/agents` (Lista) | ✅ OK | Usa Supabase corretamente |
| `/agents/[id]` (Detalhes) | ❌ ERRO | Usa mockData |
| `/tests` (Lista) | ❌ ERRO | Usa mockData |

---

## Funções do Supabase Disponíveis:

```typescript
// Em src/lib/supabaseData.ts

✅ fetchDashboardStats() - Dashboard stats
✅ fetchScoreHistory() - Gráfico de scores
✅ fetchRecentAgents(limit) - Agentes recentes
✅ fetchAllAgents() - Todos os agentes
✅ fetchAgentById(id) - Detalhes de um agente
✅ fetchTestResults() - Todos os testes
✅ fetchTestResultsByAgent(agentId) - Testes de um agente
```

---

## Funções da API Disponíveis:

```typescript
// Em src/lib/api.ts

✅ testAgent(request) - Executar teste de um agente
```

---

## Próximos Passos:

1. ✅ **Adicionar Navigation** (CONCLUÍDO)
2. 🔄 **Corrigir `/agents/[id]`** - Usar Supabase
3. 🔄 **Corrigir `/tests`** - Usar Supabase
4. ✅ **Testar integração E2E**

---

## Como Testar Após Correção:

```bash
# 1. Acessar dashboard
open https://dashboard-ks2jfjj6h-marcosdanielsfs-projects.vercel.app

# 2. Clicar em "Agents" (deve funcionar)
# 3. Clicar em um agente específico (deve mostrar dados reais)
# 4. Clicar em "Tests" (deve mostrar lista de testes reais)
# 5. Clicar em "Run Test" (deve executar teste via API)
```

---

**Status:** 2 páginas com bug identificadas, correção em andamento.
