'use client'

import { useState } from 'react'
import { Activity, MessageSquare, AlertTriangle, CheckCircle2, Clock, TrendingUp } from 'lucide-react'
import type { AgentPerformanceSummary } from '@/types/database'
import { useTestAgent } from '@/hooks/useAgents'

interface AgentCardProps {
  agent: AgentPerformanceSummary
  onSelect?: (agent: AgentPerformanceSummary) => void
}

export function AgentCard({ agent, onSelect }: AgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const testMutation = useTestAgent()

  const handleTestAgent = () => {
    testMutation.mutate({
      agent_version_id: agent.agent_version_id,
      test_mode: 'full',
      reflection_enabled: true,
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'draft':
        return 'bg-yellow-100 text-yellow-800'
      case 'archived':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  const getScoreColor = (score: number | null) => {
    if (!score) return 'text-gray-400'
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3
                className="font-semibold text-gray-900 cursor-pointer hover:text-blue-600"
                onClick={() => onSelect?.(agent)}
              >
                {agent.agent_name}
              </h3>
              <span className="text-sm text-gray-500">v{agent.version}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(agent.status)}`}>
                {agent.status}
              </span>
              {agent.framework_approved && (
                <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  Framework Approved
                </span>
              )}
            </div>
          </div>

          {/* Score Badge */}
          {agent.last_test_score !== null && (
            <div className="text-center">
              <div className={`text-2xl font-bold ${getScoreColor(agent.last_test_score)}`}>
                {agent.last_test_score.toFixed(1)}
              </div>
              <div className="text-xs text-gray-500">score</div>
            </div>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 p-4">
        {/* Conversations */}
        <div className="flex items-start gap-2">
          <MessageSquare className="w-4 h-4 text-blue-500 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-gray-900">{agent.conversas_7d}</div>
            <div className="text-xs text-gray-500">conversas (7d)</div>
          </div>
        </div>

        {/* Resolution Rate */}
        <div className="flex items-start gap-2">
          <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-gray-900">
              {agent.conversas_7d > 0
                ? Math.round((agent.resolvidas_7d / agent.conversas_7d) * 100)
                : 0}%
            </div>
            <div className="text-xs text-gray-500">resolução</div>
          </div>
        </div>

        {/* Escalations */}
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-gray-900">{agent.escalations_7d}</div>
            <div className="text-xs text-gray-500">escalações</div>
          </div>
        </div>

        {/* Satisfaction */}
        <div className="flex items-start gap-2">
          <TrendingUp className="w-4 h-4 text-purple-500 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-gray-900">{agent.satisfacao_7d.toFixed(1)}</div>
            <div className="text-xs text-gray-500">satisfação</div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Clock className="w-3 h-3" />
          {agent.last_test_at ? (
            <span>Testado {new Date(agent.last_test_at).toLocaleDateString()}</span>
          ) : (
            <span>Nunca testado</span>
          )}
        </div>

        <button
          onClick={handleTestAgent}
          disabled={testMutation.isPending}
          className="px-3 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {testMutation.isPending ? (
            <span className="flex items-center gap-1">
              <Activity className="w-3 h-3 animate-spin" />
              Testando...
            </span>
          ) : (
            'Testar Agente'
          )}
        </button>
      </div>

      {/* Success/Error Messages */}
      {testMutation.isSuccess && (
        <div className="px-4 py-2 bg-green-50 border-t border-green-100 text-xs text-green-700">
          Teste iniciado com sucesso!
        </div>
      )}
      {testMutation.isError && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100 text-xs text-red-700">
          Erro ao iniciar teste: {testMutation.error?.message}
        </div>
      )}
    </div>
  )
}
