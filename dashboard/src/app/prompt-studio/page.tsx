'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Save, Play, ArrowLeft, Box } from 'lucide-react'
import { fetchAllAgents } from '@/lib/supabaseData'
import { updateAgentPrompt } from '@/lib/agentActions'
import { VersionList } from '@/components/prompt-studio/VersionList'
import { CodeEditor } from '@/components/prompt-studio/CodeEditor'
import { ConfigPanel } from '@/components/prompt-studio/ConfigPanel'
import '@/styles/factorai-colors.css'

interface HyperpersonalizationConfig {
  tone?: string
  forbidden_words?: string[]
  knowledge_base_ids?: string[]
}

export default function PromptStudioPage() {
  const router = useRouter()
  const [agents, setAgents] = useState<any[]>([])
  const [activeAgentId, setActiveAgentId] = useState<string | null>(null)
  const [systemPrompt, setSystemPrompt] = useState('')
  const [config, setConfig] = useState<HyperpersonalizationConfig>({
    tone: 'Amigável (Padrão)',
    forbidden_words: [],
    knowledge_base_ids: []
  })
  const [isDirty, setIsDirty] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const activeAgent = agents.find(a => a.agent_version_id === activeAgentId)

  useEffect(() => {
    loadAgents()
  }, [])

  async function loadAgents() {
    try {
      const data = await fetchAllAgents()
      setAgents(data)

      // Select first agent by default
      if (data.length > 0) {
        const first = data[0]
        setActiveAgentId(first.agent_version_id)
        setSystemPrompt(first.system_prompt || '')

        // Load hyperpersonalization config if available
        if (first.hyperpersonalization_config) {
          setConfig(first.hyperpersonalization_config)
        }
      }
    } catch (error) {
      console.error('Error loading agents:', error)
    } finally {
      setLoading(false)
    }
  }

  function handleSelectAgent(agentId: string) {
    const agent = agents.find(a => a.agent_version_id === agentId)
    if (agent) {
      setActiveAgentId(agentId)
      setSystemPrompt(agent.system_prompt || '')
      setConfig(agent.hyperpersonalization_config || {
        tone: 'Amigável (Padrão)',
        forbidden_words: [],
        knowledge_base_ids: []
      })
      setIsDirty(false)
    }
  }

  function handlePromptChange(newValue: string) {
    setSystemPrompt(newValue)
    setIsDirty(true)
  }

  function handleConfigChange(newConfig: HyperpersonalizationConfig) {
    setConfig(newConfig)
    setIsDirty(true)
  }

  async function handleSave() {
    if (!activeAgentId) return

    setSaving(true)
    try {
      await updateAgentPrompt(activeAgentId, systemPrompt, config)
      setIsDirty(false)
      alert('✅ Prompt salvo com sucesso!')

      // Reload agents to update the list
      await loadAgents()
    } catch (error: any) {
      alert('❌ Erro ao salvar: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  function handleSandbox() {
    alert('🚀 Sandbox mode em desenvolvimento!\n\nEm breve você poderá testar o prompt em tempo real.')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-bg-primary">
        <div className="text-text-secondary">Carregando agentes...</div>
      </div>
    )
  }

  if (agents.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-bg-primary">
        <div className="text-center">
          <div className="text-text-secondary mb-4">Nenhum agente encontrado</div>
          <button
            onClick={() => router.push('/agents')}
            className="px-4 py-2 bg-accent-primary text-white rounded hover:bg-accent-primary/90"
          >
            Ir para Agentes
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-bg-primary">
      {/* Header */}
      <div className="h-14 border-b border-border-default flex items-center justify-between px-6 bg-bg-secondary shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/agents')}
            className="hover:bg-bg-hover p-2 rounded text-text-secondary hover:text-text-primary"
          >
            <ArrowLeft size={20} />
          </button>
          <h1 className="font-semibold text-text-primary flex items-center gap-2">
            <Box size={18} />
            Prompt Studio
          </h1>
          <div className="h-4 w-px bg-border-default"></div>
          <div className="flex items-center gap-2 text-sm text-text-muted">
            <span>Editando:</span>
            <span className="text-text-primary font-mono bg-bg-tertiary px-1.5 py-0.5 rounded border border-border-default">
              {activeAgent?.agent_name || 'N/A'}
            </span>
            <span className="text-text-muted">•</span>
            <span className="text-text-primary font-mono bg-bg-tertiary px-1.5 py-0.5 rounded border border-border-default">
              {activeAgent?.version || 'N/A'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSandbox}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-text-secondary hover:bg-bg-hover rounded transition-colors"
          >
            <Play size={16} />
            <span className="hidden sm:inline">Sandbox</span>
          </button>
          <button
            onClick={handleSave}
            disabled={!isDirty || saving}
            className={`
              flex items-center gap-2 px-4 py-1.5 text-sm rounded transition-colors ml-2
              ${isDirty && !saving
                ? 'bg-text-primary text-bg-primary hover:bg-white/90'
                : 'bg-bg-tertiary text-text-muted cursor-not-allowed'}
            `}
          >
            <Save size={16} />
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Versions */}
        <VersionList
          versions={agents}
          activeId={activeAgentId || ''}
          onSelect={handleSelectAgent}
        />

        {/* Main Editor */}
        <CodeEditor
          value={systemPrompt}
          onChange={handlePromptChange}
        />

        {/* Right Sidebar: Config */}
        <ConfigPanel
          config={config}
          onChange={handleConfigChange}
        />
      </div>
    </div>
  )
}
