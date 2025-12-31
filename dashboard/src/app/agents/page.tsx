'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Activity,
  Search,
  Filter,
  AlertCircle,
  CheckCircle2,
  PlayCircle,
  Clock,
  MessageSquare,
  TrendingUp,
} from 'lucide-react'
import { fetchAllAgents } from '@/lib/supabaseData'
import { testAgent } from '@/lib/api'
import type { AgentPerformanceSummary } from '@/types/database'

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentPerformanceSummary[]>([])
  const [filteredAgents, setFilteredAgents] = useState<AgentPerformanceSummary[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [testingAgent, setTestingAgent] = useState<string | null>(null)

  useEffect(() => {
    loadAgents()
  }, [])

  useEffect(() => {
    filterAgents()
  }, [agents, searchTerm, statusFilter])

  async function loadAgents() {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchAllAgents()
      setAgents(data)
      setFilteredAgents(data)
    } catch (err) {
      console.error('Error loading agents:', err)
      setError(err instanceof Error ? err.message : 'Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  function filterAgents() {
    let filtered = agents

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (agent) =>
          agent.agent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          agent.version.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((agent) => agent.status === statusFilter)
    }

    setFilteredAgents(filtered)
  }

  async function handleTestAgent(agentId: string) {
    try {
      setTestingAgent(agentId)
      const result = await testAgent({
        agent_version_id: agentId,
        test_mode: 'full',
        reflection_enabled: true,
      })

      alert(`Test started successfully!\nTest ID: ${result.test_id}\nStatus: ${result.status}`)

      // Reload agents after a delay
      setTimeout(() => {
        loadAgents()
      }, 2000)
    } catch (err) {
      alert(`Failed to start test: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setTestingAgent(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <Activity className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-muted-foreground">Loading agents...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4 text-center">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <div>
            <h3 className="text-lg font-semibold mb-2">Error Loading Agents</h3>
            <p className="text-muted-foreground">{error}</p>
            <Button onClick={loadAgents} className="mt-4">
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Agents</h1>
        <p className="text-muted-foreground">
          View and test all registered AI agents (Live from Supabase)
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={statusFilter === 'all' ? 'default' : 'outline'}
            onClick={() => setStatusFilter('all')}
            size="sm"
          >
            All
          </Button>
          <Button
            variant={statusFilter === 'active' ? 'default' : 'outline'}
            onClick={() => setStatusFilter('active')}
            size="sm"
          >
            Active
          </Button>
          <Button
            variant={statusFilter === 'draft' ? 'default' : 'outline'}
            onClick={() => setStatusFilter('draft')}
            size="sm"
          >
            Draft
          </Button>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        Showing {filteredAgents.length} of {agents.length} agents
      </div>

      {/* Agents Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredAgents.map((agent) => (
          <Link key={agent.agent_version_id} href={`/agents/${agent.agent_version_id}`}>
            <Card className="hover:shadow-lg transition-all cursor-pointer h-full">
              <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{agent.agent_name}</CardTitle>
                  <CardDescription>v{agent.version}</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Badge variant={agent.is_active ? 'default' : 'secondary'}>
                    {agent.status}
                  </Badge>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Score */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Test Score</span>
                <div className="flex items-center gap-2">
                  <div
                    className={`text-2xl font-bold ${
                      (agent.last_test_score || 0) >= 8
                        ? 'text-green-600'
                        : (agent.last_test_score || 0) >= 6
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}
                  >
                    {agent.last_test_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 pt-3 border-t">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-blue-500" />
                  <div>
                    <div className="text-sm font-medium">{agent.conversas_7d}</div>
                    <div className="text-xs text-muted-foreground">Conversations</div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <div>
                    <div className="text-sm font-medium">
                      {agent.conversas_7d > 0
                        ? Math.round((agent.resolvidas_7d / agent.conversas_7d) * 100)
                        : 0}%
                    </div>
                    <div className="text-xs text-muted-foreground">Resolution</div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                  <div>
                    <div className="text-sm font-medium">{agent.escalations_7d}</div>
                    <div className="text-xs text-muted-foreground">Escalations</div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-purple-500" />
                  <div>
                    <div className="text-sm font-medium">{agent.satisfacao_7d.toFixed(1)}</div>
                    <div className="text-xs text-muted-foreground">Satisfaction</div>
                  </div>
                </div>
              </div>

              {/* Last Tested */}
              <div className="flex items-center gap-2 text-xs text-muted-foreground pt-3 border-t">
                <Clock className="w-3 h-3" />
                {agent.last_test_at ? (
                  <span>Tested {new Date(agent.last_test_at).toLocaleDateString()}</span>
                ) : (
                  <span>Never tested</span>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button
                  size="sm"
                  className="flex-1"
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    handleTestAgent(agent.agent_version_id)
                  }}
                  disabled={testingAgent === agent.agent_version_id}
                >
                  {testingAgent === agent.agent_version_id ? (
                    <>
                      <Activity className="w-3 h-3 mr-2 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    <>
                      <PlayCircle className="w-3 h-3 mr-2" />
                      Run Test
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Empty State */}
      {filteredAgents.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Filter className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No agents found</h3>
            <p className="text-muted-foreground text-center max-w-md">
              {searchTerm || statusFilter !== 'all'
                ? 'Try adjusting your filters'
                : 'Create your first agent to get started'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
