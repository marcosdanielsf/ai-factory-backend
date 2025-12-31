# 🔍 Análise Completa: Front FactorAI vs AI Factory Dashboard

**Data:** 31/12/2025 15:15 BRT

---

## 📊 COMPARAÇÃO ENTRE PROJETOS:

### AI Factory Testing Framework (Atual - Next.js)
```
✅ FUNCIONANDO:
- Homepage com stats reais do Supabase
- Lista de agentes (/agents)
- Detalhes de agentes (/agents/[id])
- Lista de testes (/tests)
- Navegação entre páginas

❌ FALTANDO:
- Editor de prompts
- Página de validação/testes
- Logs de conversa
- Knowledge base
- Sistema de alertas
```

### Front FactorAI (Novo - React + Vite)
```
✅ TEM TUDO QUE O AI FACTORY PRECISA:
- Prompt Studio (editor de prompts)
- Testes & Qualidade (validação)
- Logs de Conversa
- Artifacts & Docs (knowledge base)
- Alertas & Monitor
- Funil de Leads (Sales OS)

✅ DESIGN SYSTEM COMPLETO:
- Sidebar com navegação estruturada
- Layout responsivo
- Sistema de cores customizado
```

---

## 🎯 ESTRUTURA DO SIDEBAR (Front FactorAI):

```typescript
// Seções da navegação:

1. COCKPIT
   └─ Cockpit (Dashboard)

2. SALES OS
   ├─ Funil de Leads (badge: 87)
   └─ Calls Realizadas

3. AI FACTORY ← ISTO É O QUE QUEREMOS!
   ├─ Prompt Studio       ← Editor de prompts
   ├─ Testes & Qualidade  ← Validação
   ├─ Logs de Conversa    ← Histórico
   └─ Artifacts & Docs    ← Knowledge base

4. SISTEMA
   └─ Configurações
```

---

## 📋 PÁGINAS DO FRONT FACTORAI:

### 1. **PromptEditor.tsx** (8.0 KB)
**Funcionalidades:**
- Editor de código para system_prompt
- Lista de versões (sidebar esquerdo)
- Configurações de hiperpersonalização (sidebar direito)
  - Tom de voz (Amigável, Profissional, Empático, Urgente)
  - Palavras proibidas (tags editáveis)
  - Origem: Git Repo (sincronizado via n8n)
- Botão "Sandbox" (testar prompt)
- Botão "Salvar" (com dirty state)
- Line numbers no editor
- Dark theme (#1e1e1e)

**Dados usados:**
```typescript
MOCK_AGENT_VERSIONS = [
  {
    id: 'v2.1',
    version_number: 'v2.1',
    system_prompt: 'Você é a Nina...',
    validation_status: 'active',
    validation_score: 98,
    created_at: '2024-12-18T10:00:00Z',
    is_active: true,
    hyperpersonalization_config: {
      tone: 'Friendly',
      forbidden_words: ['Desculpe'],
      knowledge_base_ids: []
    }
  }
]
```

---

### 2. **Validation.tsx** (5.7 KB)
**Funcionalidades:**
- Header com "V4 Framework de Validação"
- Botão "Rodar Nova Bateria de Testes"
- 3 cards de status:
  - Versão em Produção (v2.1 - 98%)
  - Versão em Staging (v2.2-beta - 65%)
  - Cobertura de Testes (25 cenários)
- Tabela de histórico:
  - Status (Passou/Falhou)
  - Versão
  - Data/Hora
  - Resultados (X Pass / Y Fail)
  - Botão "Ver HTML" (relatório)

**Dados usados:**
```typescript
MOCK_TEST_RUNS = [
  {
    id: 'run-123',
    version_id: 'v2.2-beta',
    run_at: '2024-12-19T14:05:00Z',
    total_tests: 25,
    passed_tests: 18,
    failed_tests: 7,
    status: 'completed',
    summary: 'Falha crítica em detecção de objeção de preço.'
  }
]
```

---

### 3. **Dashboard.tsx** (5.5 KB)
**Funcionalidades:**
- 4 cards de métricas:
  - Leads Ativos (87)
  - Versão Estável (v2.1 - Score 98/100)
  - Testes Executados (1.240)
  - Alertas Críticos (1)
- Lista de alertas recentes
- Seção "Recém-Aprovado (V4)" com status de versões

---

### 4. **Logs.tsx** (4.0 KB)
**Funcionalidades:**
- Filtros: Cliente, Canal (WhatsApp/SMS/Email), Status
- Tabela de conversas:
  - ID da conversa
  - Cliente
  - Canal
  - Mensagens (total)
  - Status (Resolvido/Escalado)
  - Data
  - Botão "Ver Transcrição"

---

### 5. **KnowledgeBase.tsx** (5.4 KB)
**Funcionalidades:**
- Lista de documentos/artifacts
- Upload de novos documentos
- Categorias (FAQ, Preços, Técnico, Legal)
- Status de sincronização

---

### 6. **Leads.tsx** (4.6 KB)
**Funcionalidades:**
- Funil de leads do Sales OS
- Cards com informações do lead
- Tags (hot, warm, cold)
- Status (demo_booked, contacted)
- Dados de contato

---

### 7. **Notifications.tsx** (4.2 KB)
**Funcionalidades:**
- Sistema de alertas
- Severidade (critical, high, medium, low)
- Filtro por tipo
- Fonte do alerta (python_validator, n8n_monitor)

---

### 8. **ClientDetail.tsx** (4.9 KB)
**Funcionalidades:**
- Detalhes do cliente
- Histórico de interações
- Configurações específicas

---

### 9. **Approvals.tsx** (2.4 KB)
**Funcionalidades:**
- Sistema de aprovação de mudanças
- Aprovar/Rejeitar alterações de prompt
- Log de mudanças

---

## 🎨 DESIGN SYSTEM:

### Cores Customizadas:
```css
/* Background */
bg-bg-primary       /* Fundo principal */
bg-bg-secondary     /* Fundo cards/sidebar */
bg-bg-tertiary      /* Fundo hover/seleção */
bg-bg-hover         /* Estado hover */

/* Text */
text-text-primary   /* Texto principal */
text-text-secondary /* Texto secundário */
text-text-muted     /* Texto desbotado */

/* Border */
border-border-default /* Borda padrão */

/* Accent */
text-accent-primary   /* Azul primário */
text-accent-success   /* Verde sucesso */
text-accent-error     /* Vermelho erro */
text-accent-warning   /* Amarelo aviso */
```

### Componentes:
```
components/
├── Layout.tsx     # Layout principal com sidebar
├── Sidebar.tsx    # Navegação lateral
└── MetricCard.tsx # Cards de métricas
```

---

## 🔄 PLANO DE MESCLAGEM:

### Estratégia RECOMENDADA: **Migração Incremental**

**Por que?**
- ✅ Mantém Next.js 14 (melhor performance)
- ✅ Integração real com Supabase
- ✅ SEO e SSR
- ✅ Aproveita código existente

---

## 📋 IMPLEMENTAÇÃO EM FASES:

### FASE 1: SETUP INICIAL (30 min)

#### 1.1 Copiar Design System
```bash
# Criar arquivo de cores
dashboard/src/styles/factorai-colors.css
```

#### 1.2 Criar componentes base
```
dashboard/src/components/factorai/
├── Sidebar.tsx           # Navegação lateral
├── MetricCard.tsx        # Cards de métricas
└── Layout.tsx            # Layout wrapper
```

---

### FASE 2: NAVEGAÇÃO (30 min)

#### 2.1 Atualizar Sidebar
```typescript
// dashboard/src/components/factorai/Sidebar.tsx

export function Sidebar() {
  return (
    <aside className="w-[260px] bg-bg-secondary border-r">
      {/* Cockpit */}
      <Link href="/">Cockpit</Link>

      {/* Sales OS */}
      <div className="text-xs text-text-muted">SALES OS</div>
      <Link href="/leads">Funil de Leads</Link>

      {/* AI Factory */}
      <div className="text-xs text-text-muted">AI FACTORY</div>
      <Link href="/prompt-studio">Prompt Studio</Link>
      <Link href="/validation">Testes & Qualidade</Link>
      <Link href="/logs">Logs de Conversa</Link>
      <Link href="/knowledge-base">Artifacts & Docs</Link>
    </aside>
  )
}
```

#### 2.2 Criar rotas
```
dashboard/src/app/
├── (dashboard)/
│   ├── page.tsx              # Cockpit (já existe)
│   ├── prompt-studio/
│   │   └── page.tsx          # Editor de prompts
│   ├── validation/
│   │   └── page.tsx          # Testes
│   ├── logs/
│   │   └── page.tsx          # Logs
│   └── knowledge-base/
│       └── page.tsx          # Artifacts
```

---

### FASE 3: PROMPT STUDIO (1 hora)

#### 3.1 Converter PromptEditor.tsx
```typescript
// dashboard/src/app/prompt-studio/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { fetchAllAgents } from '@/lib/supabaseData'

export default function PromptStudioPage() {
  const [agents, setAgents] = useState([])
  const [activeAgent, setActiveAgent] = useState(null)
  const [systemPrompt, setSystemPrompt] = useState('')

  // Código do editor aqui...
}
```

#### 3.2 Componentes do editor
```
dashboard/src/components/prompt-studio/
├── VersionList.tsx      # Lista de versões (sidebar esquerdo)
├── CodeEditor.tsx       # Editor de código
├── ConfigPanel.tsx      # Config de hiperpersonalização
└── EditorHeader.tsx     # Header com botões
```

---

### FASE 4: VALIDAÇÃO (1 hora)

#### 4.1 Converter Validation.tsx
```typescript
// dashboard/src/app/validation/page.tsx
'use client'

import { fetchAllTestResults } from '@/lib/supabaseData'

export default function ValidationPage() {
  const [testRuns, setTestRuns] = useState([])

  // Código da página aqui...
}
```

#### 4.2 Componentes de validação
```
dashboard/src/components/validation/
├── TestRunCard.tsx      # Card de execução
├── StatusBadge.tsx      # Badge de status
└── TestResultsTable.tsx # Tabela de resultados
```

---

### FASE 5: LOGS (30 min)

#### 5.1 Criar página de logs
```typescript
// dashboard/src/app/logs/page.tsx
'use client'

import { useState } from 'react'

export default function LogsPage() {
  // Filtros e tabela de conversas
}
```

---

### FASE 6: KNOWLEDGE BASE (30 min)

#### 6.1 Criar página de knowledge base
```typescript
// dashboard/src/app/knowledge-base/page.tsx
'use client'

export default function KnowledgeBasePage() {
  // Upload e lista de documentos
}
```

---

## ⏱️ TEMPO TOTAL ESTIMADO:

| Fase | Tarefa | Tempo |
|------|--------|-------|
| 1 | Setup inicial | 30 min |
| 2 | Navegação | 30 min |
| 3 | Prompt Studio | 1 hora |
| 4 | Validação | 1 hora |
| 5 | Logs | 30 min |
| 6 | Knowledge Base | 30 min |
| **TOTAL** | **4 horas** |

---

## 🎯 PRIORIZAÇÃO:

### Alta Prioridade (fazer AGORA):
1. ✅ Prompt Studio (editor de prompts)
2. ✅ Validação (página de testes)
3. ✅ Sidebar com navegação

### Média Prioridade (depois):
4. ⚠️ Logs de conversa
5. ⚠️ Knowledge base

### Baixa Prioridade (futuro):
6. 📋 Sales OS (leads, calls)
7. 📋 Alertas
8. 📋 Aprovações

---

## 🚀 AÇÃO IMEDIATA:

Quer que eu comece implementando:

### Opção A: **Prompt Studio Completo** (1 hora)
- Editor de código
- Lista de versões
- Config de hiperpersonalização
- Integração com Supabase

### Opção B: **Sidebar + 3 Páginas Principais** (2 horas)
- Sidebar com navegação
- Prompt Studio (básico)
- Validação
- Logs (básico)

### Opção C: **Só a Estrutura** (30 min)
- Pastas criadas
- Arquivos vazios
- Comentários explicativos

---

**Qual você prefere?** E sobre o **problema do Vercel** (dashboard não atualizando), quer que eu resolva isso primeiro?
