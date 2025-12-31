# 🔍 Contexto para Análise Detalhada do Dashboard - Claude Browser

**Data:** 31/12/2025 14:00 BRT
**Objetivo:** Identificar TODOS os erros, bugs e problemas de UX no dashboard deployado

---

## 📍 URLs PARA TESTAR:

### Dashboard Principal (Vercel)
```
https://dashboard-ks2jfjj6h-marcosdanielsfs-projects.vercel.app
```

### Backend API (Railway)
```
https://ai-factory-backend-production.up.railway.app
```

---

## 🎯 O QUE ACABOU DE SER CORRIGIDO:

### Commit Recente (há 5 minutos):
- ✅ Removida dependência de mockData de 2 páginas
- ✅ Implementadas 3 novas funções Supabase
- ✅ Páginas `/agents/[id]` e `/tests` agora buscam dados reais

### Arquivos Modificados:
1. `dashboard/src/lib/supabaseData.ts` (novas funções)
2. `dashboard/src/app/agents/[id]/page.tsx` (conversão para Supabase)
3. `dashboard/src/app/tests/page.tsx` (conversão para Supabase)

---

## 🔍 CHECKLIST DE ANÁLISE - EXECUTE CADA ITEM:

### 1. HOMEPAGE (`/`)

**O que verificar:**
- [ ] Dashboard Stats (Total Agents, Avg Score, Tests Run, Pass Rate)
- [ ] Score History Chart (últimas 5 semanas)
- [ ] Recent Agents Tested (lista de 5 agentes)
- [ ] Botão "Run Test" em cada agente funciona?
- [ ] Botão "View All Agents" leva para `/agents`?

**Erros a procurar:**
- [ ] Console errors (F12 → Console)
- [ ] Failed network requests (F12 → Network)
- [ ] Dados "undefined" ou "null" na tela
- [ ] Loading infinito
- [ ] Erro 500/400/401/403 na API

**Dados esperados:**
- Total Agents: número real do banco (não 0, não mock)
- Avg Score: entre 0.0 e 10.0
- Recent Agents: nomes reais (NÃO "Customer Support Agent", "Sales Assistant")

---

### 2. PÁGINA DE AGENTES (`/agents`)

**O que verificar:**
- [ ] Lista completa de agentes aparece
- [ ] Cards mostram: nome, versão, score, status
- [ ] Botão "Run Test" em cada card funciona
- [ ] Loading state funciona
- [ ] Navegação funciona (voltar para `/`)

**Erros a procurar:**
- [ ] Console errors
- [ ] Network failures
- [ ] Cards vazios ou com dados mock
- [ ] Botões não clicáveis

**Dados esperados:**
- Agentes reais do Supabase
- Scores reais (não 8.5, 9.2 fixos)
- Status: "active", "draft", "archived"

---

### 3. PÁGINA DE DETALHES DO AGENTE (`/agents/[id]`) ⚠️ RECÉM CORRIGIDA

**Como testar:**
1. Ir para `/agents`
2. Clicar em QUALQUER agente da lista
3. Deve abrir `/agents/[agent_version_id]`

**O que verificar:**
- [ ] Header: nome do agente, versão, status badge
- [ ] Overall Score (número grande no topo direito)
- [ ] Performance by Dimension (5 barras: completeness, tone, engagement, compliance, conversion)
- [ ] Strengths (lista de pontos fortes)
- [ ] Weaknesses (lista de pontos fracos)
- [ ] Test History (lista de testes anteriores)
- [ ] Botão "View Full HTML Report" (se existir report_url)

**Erros a procurar:**
- [ ] **CRÍTICO:** Erro 404 ou "notFound()"
- [ ] **CRÍTICO:** Console error "Cannot read property of undefined"
- [ ] **CRÍTICO:** Dados mock aparecendo (Customer Support Agent, etc)
- [ ] Dimensions não aparecem (0 barras)
- [ ] Strengths/Weaknesses vazios quando deveriam ter dados
- [ ] Test History vazio quando deveria ter histórico
- [ ] Erro de Supabase no console

**Dados esperados:**
- Nome real do agente (ex: "Agent Vendas BPO", "Atendimento WhatsApp")
- Score real (ex: 7.8, 8.9, não 9.5 fixo)
- Dimensions com valores diferentes (não todos 8.5)
- Strengths/Weaknesses do último teste
- Test History com múltiplos testes (se existirem)

**Se der erro, capture:**
1. Console completo (F12 → Console → screenshot)
2. Network tab com request falhado (F12 → Network → screenshot)
3. Mensagem de erro exata na tela
4. URL completa que está acessando
5. ID do agente que está tentando acessar

---

### 4. PÁGINA DE TESTES (`/tests`) ⚠️ RECÉM CORRIGIDA

**Como testar:**
1. Clicar em "Tests" na navegação
2. Deve abrir `/tests`

**O que verificar:**
- [ ] Stats Cards (Total Tests, Pass Rate, Avg Duration)
- [ ] Filtros funcionam:
  - [ ] Busca por nome de agente
  - [ ] Filtro de Status (all, passed, warning, failed)
  - [ ] Filtro de Score (all, high, medium, low)
- [ ] Tabela com todos os testes:
  - [ ] Coluna "Agent" (clicável)
  - [ ] Coluna "Date & Time"
  - [ ] Coluna "Score" (badge colorido)
  - [ ] Coluna "Status" (badge colorido)
  - [ ] Coluna "Duration"
- [ ] Clicar em um agente da tabela leva para `/agents/[id]`

**Erros a procurar:**
- [ ] **CRÍTICO:** Console error ao carregar
- [ ] **CRÍTICO:** Tabela vazia quando deveria ter dados
- [ ] **CRÍTICO:** Dados mock aparecendo
- [ ] Loading infinito
- [ ] Filtros não funcionam
- [ ] Stats incorretos (0 tests quando há testes)
- [ ] Links para agentes quebrados

**Dados esperados:**
- Total Tests: número real > 0
- Pass Rate: % real
- Tabela com testes reais do banco
- Filtros alterando a tabela em tempo real
- Links funcionais para páginas de agentes

**Se der erro, capture:**
1. Console completo
2. Network tab (procurar por fetchAllTestResults)
3. Erro exato
4. Screenshot da tabela vazia ou com erro

---

### 5. NAVEGAÇÃO GERAL

**O que verificar:**
- [ ] Menu superior existe (Overview, Agents, Tests)
- [ ] Clicar em "Overview" volta para `/`
- [ ] Clicar em "Agents" vai para `/agents`
- [ ] Clicar em "Tests" vai para `/tests`
- [ ] Navegação funciona em todas as páginas
- [ ] Botão "Back to Agents" funciona em `/agents/[id]`

---

### 6. CONSOLE DO NAVEGADOR (F12 → Console)

**Procure por:**

#### ❌ Erros CRÍTICOS que IMPEDEM funcionamento:
```
- TypeError: Cannot read property 'X' of undefined
- Error fetching agent: [mensagem]
- Failed to fetch
- 500 Internal Server Error
- 401 Unauthorized
- 404 Not Found
```

#### ⚠️ Avisos MÉDIOS (funcionam mas têm problemas):
```
- Warning: Each child in a list should have a unique "key" prop
- DialogContent requires a DialogTitle (já documentado em ACCESSIBILITY-FIXES.md)
- CORS error
- Cache miss
```

#### ✅ Avisos BAIXOS (podem ignorar):
```
- Deprecated API warnings
- Performance suggestions
```

---

### 7. NETWORK TAB (F12 → Network)

**Verificar requests para:**

#### Supabase (https://bfumywvwubvernvhjehk.supabase.co):
- [ ] `POST /rest/v1/rpc/vw_agent_performance_summary`
- [ ] `POST /rest/v1/rpc/vw_test_results_history`
- Status esperado: **200 OK**
- Se falhar: copiar response completo

#### API Railway (https://ai-factory-backend-production.up.railway.app):
- [ ] `POST /api/test` (quando clicar em Run Test)
- Status esperado: **200 OK** ou **202 Accepted**
- Se falhar: copiar response completo

**Procure por:**
- ❌ Status 400, 401, 403, 404, 500
- ❌ CORS errors
- ❌ Timeout errors
- ❌ Requests que ficam "pending" para sempre

---

### 8. DADOS MOCK vs DADOS REAIS

**Como identificar dados MOCK (BAD):**
```
❌ "Customer Support Agent"
❌ "Sales Assistant"
❌ "Test Agent 1"
❌ Score sempre 8.5 ou 9.2
❌ Dimensions todos iguais
❌ Test runs com IDs sequenciais (1, 2, 3)
```

**Como identificar dados REAIS (GOOD):**
```
✅ Nomes únicos de agentes (ex: "Agent Vendas BPO")
✅ Scores variados (7.2, 8.9, 6.5)
✅ Dimensions com valores diferentes
✅ UUIDs nos IDs (ex: "abc-123-def-456")
✅ Datas reais (não todas "2024-01-15")
```

---

### 9. TESTES DE INTEGRAÇÃO E2E

**Fluxo completo a testar:**

#### Teste 1: Ver agente e executar teste
```
1. Acesse /
2. Veja os Recent Agents
3. Clique em um agente
4. Deve abrir /agents/[id] com dados reais
5. Clique em "Back to Agents"
6. Deve voltar para /agents
7. Clique em "Run Test" em algum agente
8. Deve mostrar loading/confirmação
```

#### Teste 2: Navegar por testes
```
1. Acesse /tests
2. Veja a lista completa
3. Use o filtro de busca (digite parte do nome)
4. Tabela deve filtrar
5. Clique em um agente da tabela
6. Deve abrir /agents/[id] correto
```

#### Teste 3: Filtros na página de testes
```
1. Acesse /tests
2. Selecione Status: "Passed"
3. Tabela deve mostrar só tests com score >= 8
4. Selecione Score: "High"
5. Tabela deve mostrar só tests com score >= 8
6. Digite nome de agente na busca
7. Tabela deve filtrar
```

---

## 📋 FORMATO DO RELATÓRIO A RETORNAR:

```markdown
# Análise Completa - Dashboard AI Factory

## ✅ O QUE ESTÁ FUNCIONANDO:
- Homepage: [OK/ERRO]
- Agents page: [OK/ERRO]
- Agent details: [OK/ERRO]
- Tests page: [OK/ERRO]
- Navigation: [OK/ERRO]

## ❌ ERROS CRÍTICOS ENCONTRADOS:

### Erro 1: [Título]
**Página:** /url/da/pagina
**Tipo:** Console Error / Network Error / Visual Bug
**Erro exato:**
```
[copiar erro do console]
```
**Screenshot:** [se possível]
**Como reproduzir:**
1. Passo 1
2. Passo 2
3. Erro acontece

**Dados esperados:** X
**Dados recebidos:** Y

---

### Erro 2: [Título]
...

## ⚠️ PROBLEMAS MÉDIOS:
[lista de avisos/warnings]

## 💡 SUGESTÕES DE CORREÇÃO:

Para cada erro crítico:
**Erro X:** [explicação]
**Provável causa:** [hipótese]
**Arquivo suspeito:** [caminho/arquivo.tsx]
**Correção sugerida:** [o que mudar]

## 📊 DADOS COLETADOS:

### Console Logs:
```
[principais logs relevantes]
```

### Network Requests:
```
Request: GET /api/x
Status: 500
Response: {...}
```

### Dados da Página:
- Total Agents: X
- Avg Score: Y
- Recent Agents: [nomes]
```

---

## 🎯 PONTOS CRÍTICOS A FOCAR:

1. **Página `/agents/[id]` (RECÉM CORRIGIDA):**
   - Esta página foi 100% reescrita há 5 minutos
   - Busca dados com `fetchAgentById(params.id)`
   - Se der erro, é PRIORITÁRIO corrigir

2. **Página `/tests` (RECÉM CORRIGIDA):**
   - Esta página foi 100% reescrita há 5 minutos
   - Busca dados com `fetchAllTestResults(100)`
   - Se der erro, é PRIORITÁRIO corrigir

3. **Funções Supabase (NOVAS):**
   - `fetchAgentById()` - nova
   - `fetchTestResultsByAgent()` - nova
   - `fetchAllTestResults()` - nova
   - Se alguma falhar, erro vem daqui

---

## 🔧 INFORMAÇÕES TÉCNICAS:

### Stack:
- Frontend: Next.js 14 (App Router)
- Backend: FastAPI (Railway)
- Database: Supabase (PostgreSQL)
- Deploy: Vercel

### Variáveis de Ambiente (Vercel):
```
NEXT_PUBLIC_SUPABASE_URL=https://bfumywvwubvernvhjehk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon key]
NEXT_PUBLIC_API_URL=https://ai-factory-backend-production.up.railway.app
```

### Views do Supabase usadas:
- `vw_agent_performance_summary`
- `vw_test_results_history`

### Autenticação:
- Supabase usa **Anon Key** (público)
- Row Level Security (RLS) desabilitado para views

---

## 🚨 SE ENCONTRAR ESTES ERROS ESPECÍFICOS:

### Erro: "Cannot read property of undefined"
**Provável causa:** Dados do Supabase vazios ou estrutura diferente
**Verificar:** console.log do retorno de fetch

### Erro: "Failed to fetch" / CORS
**Provável causa:** Supabase URL errada ou API offline
**Verificar:** Network tab, testar URL diretamente

### Erro: "notFound()" / 404 page
**Provável causa:** ID do agente não existe ou formato errado
**Verificar:** ID sendo passado, se existe no banco

### Erro: Tabela vazia quando deveria ter dados
**Provável causa:** Query Supabase retornando []
**Verificar:** Response da API no Network tab

### Erro: Dados mock aparecendo
**Provável causa:** Import de mockData ainda existe
**Verificar:** Grep por "mockData" nos arquivos

---

## ✅ CRITÉRIOS DE SUCESSO:

Dashboard está **100% funcional** se:
- [x] Todas as páginas carregam sem erros
- [x] Todos os dados vêm do Supabase (0 mock)
- [x] Navegação funciona em todos os links
- [x] Filtros funcionam na página de tests
- [x] Clicar em agentes abre detalhes corretos
- [x] Console sem erros críticos
- [x] Network requests todos 200 OK

---

**IMPORTANTE:**
- Execute TODOS os testes listados
- Capture screenshots de TODOS os erros
- Copie TEXTO COMPLETO dos erros do console
- Teste em modo incognito (limpar cache)
- Aguarde 3-5 minutos após deploy antes de testar

---

**Data da última correção:** 31/12/2025 14:00 BRT
**Commit hash:** 7feac9f
**Deploy estimado:** 2-3 minutos após push
