'use client'

import { GitBranch } from 'lucide-react'

interface HyperpersonalizationConfig {
  tone?: string
  forbidden_words?: string[]
  knowledge_base_ids?: string[]
}

interface ConfigPanelProps {
  config: HyperpersonalizationConfig
  onChange: (config: HyperpersonalizationConfig) => void
}

export function ConfigPanel({ config, onChange }: ConfigPanelProps) {
  const tones = [
    'Amigável (Padrão)',
    'Profissional',
    'Empático',
    'Urgente (Sales)'
  ]

  return (
    <div className="w-72 border-l border-border-default bg-bg-secondary flex flex-col overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-border-default">
        <h3 className="font-medium text-sm mb-1">Configurações de Hiperpersonalização</h3>
        <p className="text-xs text-text-muted">Parâmetros do V3 Engine</p>
      </div>

      {/* Config Options */}
      <div className="p-4 space-y-6">
        {/* Tom de Voz */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">
            Tom de Voz
          </label>
          <select
            value={config.tone || tones[0]}
            onChange={(e) => onChange({ ...config, tone: e.target.value })}
            className="w-full bg-bg-tertiary border border-border-default rounded px-3 py-2 text-sm focus:border-text-muted outline-none text-text-primary"
          >
            {tones.map(tone => (
              <option key={tone} value={tone}>{tone}</option>
            ))}
          </select>
        </div>

        {/* Palavras Proibidas */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">
            Palavras Proibidas
          </label>
          <div className="bg-bg-tertiary border border-border-default rounded p-2 text-sm text-text-primary min-h-[80px]">
            {(config.forbidden_words || []).map((word, index) => (
              <span
                key={index}
                className="inline-block bg-bg-primary border border-border-default px-1.5 py-0.5 rounded text-xs mr-1 mb-1"
              >
                {word}
              </span>
            ))}
            <input
              type="text"
              placeholder="+ add"
              className="bg-transparent outline-none text-xs w-16"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.currentTarget.value) {
                  onChange({
                    ...config,
                    forbidden_words: [...(config.forbidden_words || []), e.currentTarget.value]
                  })
                  e.currentTarget.value = ''
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Footer - Git Origin */}
      <div className="mt-auto p-4 border-t border-border-default">
        <div className="bg-bg-tertiary p-3 rounded text-xs text-text-muted">
          <div className="flex items-center gap-2 mb-1 text-text-secondary font-medium">
            <GitBranch size={12} />
            Origem: Git Repo
          </div>
          <p>Sincronizado via n8n webhook.</p>
        </div>
      </div>
    </div>
  )
}
