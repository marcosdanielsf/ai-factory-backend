// Supabase data fetchers - replacing mockData.ts

import { supabase } from './supabase'
import type { AgentPerformanceSummary, LatestTestResult } from '@/types/database'

export interface DashboardStats {
  totalAgents: number
  averageScore: number
  testsRun: number
  passRate: number
}

export interface ScoreHistory {
  date: string
  score: number
}

// Fetch dashboard statistics
export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data: agents, error: agentsError } = await supabase
    .from('vw_agent_performance_summary')
    .select('last_test_score, total_testes_executados')

  if (agentsError) throw agentsError

  const totalAgents = agents?.length || 0
  const validScores = agents?.filter(a => a.last_test_score !== null) || []
  const averageScore = validScores.length > 0
    ? validScores.reduce((sum, a) => sum + (a.last_test_score || 0), 0) / validScores.length
    : 0

  const testsRun = agents?.reduce((sum, a) => sum + a.total_testes_executados, 0) || 0

  // Calculate pass rate (score >= 8.0)
  const passedTests = validScores.filter(a => (a.last_test_score || 0) >= 8.0).length
  const passRate = validScores.length > 0 ? (passedTests / validScores.length) * 100 : 0

  return {
    totalAgents,
    averageScore: Number(averageScore.toFixed(1)),
    testsRun,
    passRate: Number(passRate.toFixed(1)),
  }
}

// Fetch score history (last 30 days average scores)
export async function fetchScoreHistory(): Promise<ScoreHistory[]> {
  const { data, error } = await supabase
    .from('vw_test_results_history')
    .select('tested_at, overall_score')
    .gte('tested_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())
    .order('tested_at', { ascending: true })

  if (error) throw error

  // Group by week and calculate average
  const weeklyScores = new Map<string, number[]>()

  data?.forEach(test => {
    const date = new Date(test.tested_at)
    const weekStart = new Date(date)
    weekStart.setDate(date.getDate() - date.getDay()) // Start of week
    const key = weekStart.toISOString().split('T')[0]

    if (!weeklyScores.has(key)) {
      weeklyScores.set(key, [])
    }
    weeklyScores.get(key)!.push(test.overall_score)
  })

  return Array.from(weeklyScores.entries())
    .map(([date, scores]) => ({
      date,
      score: Number((scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)),
    }))
    .slice(-5) // Last 5 weeks
}

// Fetch recent agents
export async function fetchRecentAgents(limit = 5) {
  const { data, error } = await supabase
    .from('vw_agent_performance_summary')
    .select('*')
    .not('last_test_at', 'is', null)
    .order('last_test_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data as AgentPerformanceSummary[]
}

// Fetch all agents
export async function fetchAllAgents() {
  const { data, error } = await supabase
    .from('vw_agent_performance_summary')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error
  return data as AgentPerformanceSummary[]
}

// Fetch recent test runs
export async function fetchRecentTestRuns(limit = 10) {
  const { data, error } = await supabase
    .from('vw_test_results_history')
    .select('*')
    .order('tested_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data
}

// Fetch single agent by ID
export async function fetchAgentById(agentVersionId: string) {
  const { data, error } = await supabase
    .from('vw_agent_performance_summary')
    .select('*')
    .eq('agent_version_id', agentVersionId)
    .single()

  if (error) throw error
  return data as AgentPerformanceSummary
}

// Fetch test results for a specific agent
export async function fetchTestResultsByAgent(agentVersionId: string) {
  const { data, error } = await supabase
    .from('vw_test_results_history')
    .select('*')
    .eq('agent_version_id', agentVersionId)
    .order('tested_at', { ascending: false })

  if (error) throw error
  return data as LatestTestResult[]
}

// Fetch all test results with pagination
export async function fetchAllTestResults(limit = 50, offset = 0) {
  const { data, error } = await supabase
    .from('vw_test_results_history')
    .select('*')
    .order('tested_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) throw error
  return data as LatestTestResult[]
}

// Map Supabase agent to legacy format for compatibility
export function mapAgentToLegacyFormat(agent: AgentPerformanceSummary) {
  return {
    id: agent.agent_version_id,
    name: agent.agent_name,
    version: agent.version,
    score: agent.last_test_score || 0,
    status: agent.status,
    lastEvaluation: agent.last_test_at || agent.created_at,
    // Note: dimensions, strengths, weaknesses would need to come from test_details JSONB
  }
}
