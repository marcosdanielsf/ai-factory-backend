'use client'

import { CheckCircle2, AlertCircle, FileCode, Plus } from 'lucide-react'

interface AgentVersion {
  agent_version_id: string
  version: string
  validation_status: string
  last_test_score: number | null
  created_at: string
  is_active: boolean
}

interface VersionListProps {
  versions: AgentVersion[]
  activeId: string
  onSelect: (id: string) => void
}

export function VersionList({ versions, activeId, onSelect }: VersionListProps) {
  const getStatusColor = (status: string) => {
    switch(status) {
      case 'active': return 'text-accent-success'
      case 'failed': return 'text-accent-error'
      default: return 'text-text-muted'
    }
  }

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'active': return <CheckCircle2 size={14} />
      case 'failed': return <AlertCircle size={14} />
      default: return <FileCode size={14} />
    }
  }

  return (
    <div className="w-64 border-r border-border-default bg-bg-secondary flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-border-default flex items-center justify-between">
        <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
          Versões
        </span>
        <button className="p-1 hover:bg-bg-hover rounded text-text-muted hover:text-text-primary">
          <Plus size={14} />
        </button>
      </div>

      {/* Version List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {versions.map(v => (
          <div
            key={v.agent_version_id}
            onClick={() => onSelect(v.agent_version_id)}
            className={`
              group flex items-center gap-3 p-2 rounded-md cursor-pointer transition-colors
              ${activeId === v.agent_version_id ? 'bg-bg-hover' : 'hover:bg-bg-hover'}
            `}
          >
            <div className={`text-xs ${getStatusColor(v.validation_status)}`}>
              {getStatusIcon(v.validation_status)}
            </div>
            <div className="flex-1 min-w-0">
              <div className={`text-sm font-medium ${activeId === v.agent_version_id ? 'text-text-primary' : 'text-text-secondary'}`}>
                {v.version}
              </div>
              <div className="text-xs text-text-muted truncate">
                Score: {v.last_test_score || 'N/A'} • {new Date(v.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
