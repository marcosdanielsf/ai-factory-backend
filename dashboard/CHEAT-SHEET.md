# Dashboard - Cheat Sheet

## Comandos Rápidos

### Rodar Dashboard
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
npm run dev
```

### Ativar Supabase
```bash
# Backup
mv src/app/page.tsx src/app/page-mock.tsx
mv src/app/agents/page.tsx src/app/agents/page-mock.tsx

# Ativar
mv src/app/page-supabase.tsx src/app/page.tsx
mv src/app/agents/page-supabase.tsx src/app/agents/page.tsx
```

### Reverter para Mock
```bash
mv src/app/page.tsx src/app/page-supabase.tsx
mv src/app/page-mock.tsx src/app/page.tsx

mv src/app/agents/page.tsx src/app/agents/page-supabase.tsx
mv src/app/agents/page-mock.tsx src/app/agents/page.tsx
```

### Testar Supabase
```bash
node -e "
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);
supabase.from('vw_agent_performance_summary').select('*').limit(5)
  .then(({ data }) => console.log(data));
"
```

---

## Estrutura de Arquivos

```
dashboard/
├── src/
│   ├── lib/
│   │   ├── supabase.ts         # Cliente Supabase
│   │   ├── api.ts              # API backend
│   │   └── supabaseData.ts     # Data fetching
│   │
│   ├── types/
│   │   └── database.ts         # Database types
│   │
│   ├── hooks/
│   │   └── useAgents.ts        # React Query hooks
│   │
│   ├── components/
│   │   ├── AgentCard.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── Providers.tsx
│   │
│   └── app/
│       ├── page-supabase.tsx
│       └── agents/
│           └── page-supabase.tsx
```

---

## Hooks Disponíveis

```typescript
import { 
  useAgents,              // Lista de agentes
  useAgent,               // Detalhes de um agente
  useLatestTestResults,   // Últimos testes
  useAgentsNeedingTesting,// Fila de testes
  useTestAgent,           // Mutation para testar
  useTestHistory,         // Histórico
  useRealtimeTestUpdates  // Realtime
} from '@/hooks/useAgents'

// Exemplo
const { data: agents, isLoading, error } = useAgents(50)
const testMutation = useTestAgent()

testMutation.mutate({
  agent_version_id: 'uuid',
  test_mode: 'full',
  reflection_enabled: true
})
```

---

## Supabase Views

```typescript
vw_agent_performance_summary    // Métricas de agentes
vw_latest_test_results          // Últimos testes
vw_test_results_history         // Histórico completo
vw_agents_needing_testing       // Fila de testes
vw_agent_conversations_summary  // Conversas
```

---

## API Endpoints

```typescript
// Backend API
POST http://localhost:8000/api/test-agent
GET  http://localhost:8000/api/test-status/:testId
POST http://localhost:8000/api/test-cancel/:testId

// Exemplo
import { testAgent } from '@/lib/api'

const result = await testAgent({
  agent_version_id: 'uuid',
  test_mode: 'full',
  reflection_enabled: true
})
```

---

## Variáveis de Ambiente

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=http://localhost:8000
API_KEY=dev-secret-key
```

---

## Troubleshooting

### Erro: Missing Supabase environment variables
Verificar se `.env.local` existe

### Erro: Failed to fetch
Backend API não está rodando

### Build falhou
```bash
rm -rf .next
npm run build
```

---

## Links Úteis

- Dashboard: http://localhost:3000
- Agents: http://localhost:3000/agents
- Supabase: https://bfumywvwubvernvhjehk.supabase.co

---

Veja `INTEGRATION-GUIDE.md` para documentação completa!
