# 🔄 Plano de Integração: Prompt Editor no AI Factory Dashboard

**Data:** 31/12/2025 15:05 BRT
**Objetivo:** Adicionar editor de prompts ao dashboard AI Factory

---

## 📊 ANÁLISE DOS DOIS PROJETOS:

### AI Factory Testing Framework (Atual)
**Tecnologia:** Next.js 14 (App Router)
**Estrutura:**
```
dashboard/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   ├── page.tsx           # Homepage
│   │   │   ├── agents/
│   │   │   │   ├── page.tsx       # Lista de agentes
│   │   │   │   └── [id]/page.tsx  # Detalhes
│   │   │   └── tests/page.tsx     # Lista de testes
│   ├── components/
│   ├── lib/
│   └── types/
```

### Front FactorAI (Novo - para integrar)
**Tecnologia:** React + Vite (SPA com HashRouter)
**Estrutura:**
```
front-factorai/
├── pages/
│   ├── Dashboard.tsx
│   ├── PromptEditor.tsx  ← ESTE é o que queremos!
│   ├── Validation.tsx
│   ├── Logs.tsx
│   └── ...
├── components/
│   ├── Layout.tsx
│   └── Sidebar.tsx
├── constants.ts
└── types.ts
```

---

## 🎯 FUNCIONALIDADES DO PROMPT EDITOR:

### 1. Interface Principal:
- ✅ Editor de código (Monaco-like textarea)
- ✅ Sidebar esquerdo: Lista de versões
- ✅ Sidebar direito: Configurações de hiperpersonalização
- ✅ Header com: versão ativa, botão Sandbox, botão Save

### 2. Funcionalidades:
- ✅ Editar system_prompt de cada versão
- ✅ Listar todas as versões (v2.1, v2.2-beta, etc)
- ✅ Indicador de status: active, failed, draft
- ✅ Score de validação
- ✅ Configurações de tom de voz
- ✅ Palavras proibidas
- ✅ Sandbox mode (testar prompt)

### 3. Dados Usados:
```typescript
// Do constants.ts
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

## 🔀 ESTRATÉGIAS DE INTEGRAÇÃO:

### Opção A: **Adicionar como Nova Página no AI Factory** (RECOMENDADO)

**Vantagens:**
- ✅ Mantém o Next.js 14
- ✅ Integração direta com Supabase
- ✅ URL limpa: `/prompt-editor` ou `/agents/[id]/edit`
- ✅ Server-side rendering (performance)
- ✅ Consistência visual com dashboard atual

**Desvantagens:**
- 🔧 Requer conversão de React (SPA) → Next.js (App Router)
- 🔧 Requer migrar de HashRouter → App Router

**Esforço:** ~2-3 horas

---

### Opção B: **Embedding via iframe**

**Vantagens:**
- ✅ Zero modificação no código do Prompt Editor
- ✅ Deploy separado (Vercel)
- ✅ Manutenção independente

**Desvantagens:**
- ❌ iframe = UX ruim
- ❌ Comunicação entre apps complexa
- ❌ Dados não compartilhados facilmente

**Esforço:** ~30 min (mas não recomendado)

---

### Opção C: **Micro-frontend (Module Federation)**

**Vantagens:**
- ✅ Apps independentes
- ✅ Deploy separado
- ✅ Sharing de componentes

**Desvantagens:**
- ❌ Complexidade alta
- ❌ Setup pesado (Webpack Module Federation)

**Esforço:** ~1 dia

---

## ✅ RECOMENDAÇÃO: **OPÇÃO A** - Adicionar como Página Next.js

---

## 🛠️ PLANO DE IMPLEMENTAÇÃO (OPÇÃO A):

### Fase 1: Criar Nova Rota `/agents/[id]/edit`

**Estrutura:**
```
dashboard/src/app/agents/[id]/
├── page.tsx           # Detalhes (já existe)
└── edit/
    └── page.tsx       # ← NOVO: Editor de prompts
```

**URL esperada:**
```
/agents/2c0f1c42-18a7-43c5-853d-b3ff80cb381f/edit
```

---

### Fase 2: Converter PromptEditor.tsx → Next.js

**Mudanças necessárias:**

#### 1. Remover SPA específico:
```typescript
// REMOVER:
import { HashRouter } from 'react-router-dom';
import { MOCK_AGENT_VERSIONS } from '../constants';

// ADICIONAR:
'use client' // Next.js client component
import { useParams } from 'next/navigation'
import { fetchAgentById } from '@/lib/supabaseData'
```

#### 2. Buscar dados reais do Supabase:
```typescript
// ANTES (MOCK):
const [activeVersionId, setActiveVersionId] = useState(MOCK_AGENT_VERSIONS[0].id);

// DEPOIS (SUPABASE):
const params = useParams()
const agent = await fetchAgentById(params.id)
const [systemPrompt, setSystemPrompt] = useState(agent.system_prompt)
```

#### 3. Criar função para salvar prompt:
```typescript
// Novo arquivo: dashboard/src/lib/agentActions.ts
export async function updateAgentPrompt(agentId: string, newPrompt: string) {
  const { data, error } = await supabase
    .from('agent_versions')
    .update({
      system_prompt: newPrompt,
      updated_at: new Date().toISOString()
    })
    .eq('agent_version_id', agentId)

  if (error) throw error
  return data
}
```

---

### Fase 3: Criar Componentes Necessários

#### 1. VersionList.tsx (Sidebar Esquerdo)
```typescript
// dashboard/src/components/prompt-editor/VersionList.tsx
'use client'

export function VersionList({ versions, activeId, onSelect }) {
  return (
    <div className="w-64 border-r border-border-default bg-bg-secondary">
      {versions.map(v => (
        <div key={v.id} onClick={() => onSelect(v.id)}>
          {v.version} - Score: {v.last_test_score}
        </div>
      ))}
    </div>
  )
}
```

#### 2. CodeEditor.tsx (Editor Principal)
```typescript
// dashboard/src/components/prompt-editor/CodeEditor.tsx
'use client'

export function CodeEditor({ value, onChange }) {
  return (
    <div className="flex-1 bg-[#1e1e1e]">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-full font-mono text-sm p-4"
        spellCheck={false}
      />
    </div>
  )
}
```

#### 3. ConfigPanel.tsx (Sidebar Direito)
```typescript
// dashboard/src/components/prompt-editor/ConfigPanel.tsx
'use client'

export function ConfigPanel({ config, onChange }) {
  return (
    <div className="w-72 border-l border-border-default">
      <div className="p-4">
        <label>Tom de Voz</label>
        <select value={config.tone} onChange={e => onChange({ ...config, tone: e.target.value })}>
          <option>Amigável</option>
          <option>Profissional</option>
        </select>
      </div>
    </div>
  )
}
```

---

### Fase 4: Estrutura Final do Arquivo

```typescript
// dashboard/src/app/agents/[id]/edit/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { fetchAgentById } from '@/lib/supabaseData'
import { updateAgentPrompt } from '@/lib/agentActions'
import { VersionList } from '@/components/prompt-editor/VersionList'
import { CodeEditor } from '@/components/prompt-editor/CodeEditor'
import { ConfigPanel } from '@/components/prompt-editor/ConfigPanel'
import { Save, Play, ArrowLeft } from 'lucide-react'

export default function PromptEditorPage() {
  const params = useParams()
  const router = useRouter()
  const [agent, setAgent] = useState(null)
  const [systemPrompt, setSystemPrompt] = useState('')
  const [isDirty, setIsDirty] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgent()
  }, [params.id])

  async function loadAgent() {
    try {
      const data = await fetchAgentById(params.id as string)
      setAgent(data)
      setSystemPrompt(data.system_prompt || '')
    } catch (error) {
      console.error('Error loading agent:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleSave() {
    try {
      await updateAgentPrompt(params.id as string, systemPrompt)
      setIsDirty(false)
      alert('Prompt salvo com sucesso!')
    } catch (error) {
      alert('Erro ao salvar: ' + error.message)
    }
  }

  function handleChange(newValue: string) {
    setSystemPrompt(newValue)
    setIsDirty(true)
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="flex flex-col h-[calc(100vh-52px)]">
      {/* Header */}
      <div className="h-14 border-b flex items-center justify-between px-6 bg-bg-secondary">
        <div className="flex items-center gap-4">
          <button onClick={() => router.back()} className="hover:bg-bg-hover p-2 rounded">
            <ArrowLeft size={20} />
          </button>
          <h1 className="font-semibold">Prompt Studio</h1>
          <span className="text-sm text-muted-foreground">
            Editando: <code className="bg-bg-tertiary px-2 py-1 rounded">{agent?.agent_name}</code>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-3 py-1.5 hover:bg-bg-hover rounded">
            <Play size={16} />
            Sandbox
          </button>
          <button
            onClick={handleSave}
            disabled={!isDirty}
            className={`flex items-center gap-2 px-4 py-1.5 rounded ${
              isDirty
                ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                : 'bg-secondary text-secondary-foreground cursor-not-allowed'
            }`}
          >
            <Save size={16} />
            Salvar
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Versions */}
        <VersionList
          versions={[agent]} // Por enquanto só a versão atual
          activeId={params.id}
          onSelect={() => {}}
        />

        {/* Main Editor */}
        <CodeEditor
          value={systemPrompt}
          onChange={handleChange}
        />

        {/* Right Sidebar: Config */}
        <ConfigPanel
          config={{
            tone: 'Amigável',
            forbidden_words: []
          }}
          onChange={() => {}}
        />
      </div>
    </div>
  )
}
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO:

### Passo 1: Preparação
- [ ] Criar pasta `dashboard/src/components/prompt-editor/`
- [ ] Criar pasta `dashboard/src/app/agents/[id]/edit/`
- [ ] Copiar CSS/Tailwind classes do front-factorai

### Passo 2: Componentes Base
- [ ] Criar `VersionList.tsx`
- [ ] Criar `CodeEditor.tsx`
- [ ] Criar `ConfigPanel.tsx`

### Passo 3: Lógica de Dados
- [ ] Criar `dashboard/src/lib/agentActions.ts`
- [ ] Implementar `updateAgentPrompt()`
- [ ] Implementar `fetchAgentVersions()` (para lista de versões)

### Passo 4: Página Principal
- [ ] Criar `dashboard/src/app/agents/[id]/edit/page.tsx`
- [ ] Integrar componentes
- [ ] Testar navegação

### Passo 5: Navegação
- [ ] Adicionar botão "Edit Prompt" em `/agents/[id]`
- [ ] Adicionar link no menu sidebar
- [ ] Testar fluxo completo

### Passo 6: Features Avançadas (Opcional)
- [ ] Implementar Sandbox mode (testar prompt)
- [ ] Histórico de versões
- [ ] Diff entre versões
- [ ] Integração com Python Framework (validação)

---

## ⏱️ TEMPO ESTIMADO:

| Tarefa | Tempo |
|--------|-------|
| Criar componentes base | 1 hora |
| Integrar com Supabase | 1 hora |
| Estilização | 30 min |
| Testes | 30 min |
| **TOTAL** | **3 horas** |

---

## 🎨 DESIGN SYSTEM:

O front-factorai usa classes customizadas. Precisamos mapear para Tailwind:

```css
/* MAPPING */
bg-bg-primary       → bg-background
bg-bg-secondary     → bg-secondary
bg-bg-tertiary      → bg-muted
text-text-primary   → text-foreground
text-text-secondary → text-muted-foreground
border-border-default → border-border
```

---

## 🚀 IMPLEMENTAÇÃO IMEDIATA:

Quer que eu:

1. **Crie todos os componentes agora** (30 min)
2. **Integre com Supabase** (30 min)
3. **Deploy e teste** (30 min)

**OU**

Prefere que eu:
- Crie um **protótipo simplificado** primeiro (15 min)?
- Mostre como ficaria a **navegação**?

---

## 📊 RESULTADO ESPERADO:

Após implementação, o usuário poderá:

1. Ir em `/agents` → Ver lista de agentes
2. Clicar em um agente → Ver detalhes
3. Clicar em **"Edit Prompt"** → Abrir editor
4. Editar o `system_prompt` em um editor de código
5. Clicar em **"Salvar"** → Atualizar no Supabase
6. Ver **score de validação** ao lado
7. Configurar **tom de voz** e **palavras proibidas**

---

**Quer que eu comece agora?** Qual preferência:
- **A:** Implementação completa (3 horas)?
- **B:** Protótipo rápido (30 min)?
- **C:** Apenas criar a estrutura e você termina depois?
