// Supabase data fetchers - replacing mockData.ts
// Updated to use agent_versions table directly instead of views

import { supabase } from './supabase'
import type { AgentPerformanceSummary, LatestTestResult, E2ETestResult, TestExecution } from '@/types/database'

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

// Helper to map agent_versions row to AgentPerformanceSummary format
function mapToAgentPerformanceSummary(row: any): AgentPerformanceSummary {
  return {
    agent_version_id: row.id,
    agent_name: row.agent_name || 'Unnamed Agent',
    version: row.version || '1.0.0',
    status: row.status || 'draft',
    is_active: row.is_active || false,
    client_id: row.client_id || '',
    sub_account_id: row.sub_account_id || null,
    last_test_score: row.last_test_score || row.validation_score || null,
    last_test_at: row.last_test_at || row.validated_at || null,
    framework_approved: row.framework_approved || false,
    reflection_count: row.reflection_count || 0,
    test_report_url: row.test_report_url || null,
    conversas_7d: 0,
    resolvidas_7d: 0,
    escalations_7d: 0,
    satisfacao_7d: 0,
    tokens_7d: 0,
    custo_7d: 0,
    conversas_30d: 0,
    ultima_conversa_at: null,
    total_conversas_historico: 0,
    total_testes_executados: row.total_test_runs || 0,
    created_at: row.created_at,
    updated_at: row.updated_at,
    activated_at: row.activated_at || null,
  }
}

// Fetch dashboard statistics
export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data: agents, error: agentsError } = await supabase
    .from('agent_versions')
    .select('id, last_test_score, validation_score, total_test_runs')

  if (agentsError) throw agentsError

  const totalAgents = agents?.length || 0
  const validScores = agents?.filter(a => (a.last_test_score || a.validation_score) !== null) || []
  const averageScore = validScores.length > 0
    ? validScores.reduce((sum, a) => sum + (a.last_test_score || a.validation_score || 0), 0) / validScores.length
    : 0

  const testsRun = agents?.reduce((sum, a) => sum + (a.total_test_runs || 0), 0) || 0

  // Calculate pass rate (score >= 8.0)
  const passedTests = validScores.filter(a => ((a.last_test_score || a.validation_score) || 0) >= 8.0).length
  const passRate = validScores.length > 0 ? (passedTests / validScores.length) * 100 : 0

  return {
    totalAgents,
    averageScore: Number(averageScore.toFixed(1)),
    testsRun,
    passRate: Number(passRate.toFixed(1)),
  }
}

// Fetch score history (last 30 days average scores)
// Using agent_versions validated_at and validation_score as fallback
export async function fetchScoreHistory(): Promise<ScoreHistory[]> {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('validated_at, validation_score, last_test_at, last_test_score')
    .or('validated_at.not.is.null,last_test_at.not.is.null')
    .gte('created_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())
    .order('created_at', { ascending: true })

  if (error) throw error

  // Group by week and calculate average
  const weeklyScores = new Map<string, number[]>()

  data?.forEach(agent => {
    const testDate = agent.last_test_at || agent.validated_at
    const score = agent.last_test_score || agent.validation_score
    if (!testDate || !score) return

    const date = new Date(testDate)
    const weekStart = new Date(date)
    weekStart.setDate(date.getDate() - date.getDay()) // Start of week
    const key = weekStart.toISOString().split('T')[0]

    if (!weeklyScores.has(key)) {
      weeklyScores.set(key, [])
    }
    weeklyScores.get(key)!.push(score)
  })

  return Array.from(weeklyScores.entries())
    .map(([date, scores]) => ({
      date,
      score: Number((scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)),
    }))
    .slice(-5) // Last 5 weeks
}

// Fetch recent agents (using agent_versions table directly)
export async function fetchRecentAgents(limit = 5): Promise<AgentPerformanceSummary[]> {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('*')
    .or('last_test_at.not.is.null,validated_at.not.is.null')
    .order('created_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return (data || []).map(mapToAgentPerformanceSummary)
}

// Fetch all agents
export async function fetchAllAgents(): Promise<AgentPerformanceSummary[]> {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error
  return (data || []).map(mapToAgentPerformanceSummary)
}

// Fetch recent test runs (using agent_versions with validation data)
export async function fetchRecentTestRuns(limit = 10) {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('id, agent_name, version, status, validated_at, validation_score, validation_result')
    .not('validated_at', 'is', null)
    .order('validated_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data?.map(row => ({
    test_result_id: row.id,
    agent_version_id: row.id,
    overall_score: row.validation_score || 0,
    tested_at: row.validated_at,
    agent_name: row.agent_name,
    version: row.version,
    status: row.status,
  })) || []
}

// Fetch single agent by ID
export async function fetchAgentById(agentVersionId: string): Promise<AgentPerformanceSummary> {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('*')
    .eq('id', agentVersionId)
    .single()

  if (error) throw error
  return mapToAgentPerformanceSummary(data)
}

// Fetch test results for a specific agent
export async function fetchTestResultsByAgent(agentVersionId: string): Promise<LatestTestResult[]> {
  // Since we don't have separate test results table populated, use validation data
  const { data, error } = await supabase
    .from('agent_versions')
    .select('id, agent_name, version, status, validated_at, validation_score, validation_result')
    .eq('id', agentVersionId)
    .not('validated_at', 'is', null)

  if (error) throw error

  return (data || []).map(row => ({
    test_result_id: row.id,
    agent_version_id: row.id,
    overall_score: row.validation_score || 0,
    test_details: row.validation_result || {},
    report_url: null,
    test_duration_ms: 0,
    evaluator_model: 'AI Factory v3',
    tested_at: row.validated_at,
    agent_name: row.agent_name,
    version: row.version,
    status: row.status,
    score_completeness: null,
    score_tone: null,
    score_engagement: null,
    score_compliance: null,
    score_conversion: null,
    total_test_cases: 0,
    total_failures: 0,
    total_warnings: 0,
  }))
}

// Fetch all test results with pagination
export async function fetchAllTestResults(limit = 50, offset = 0): Promise<LatestTestResult[]> {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('id, agent_name, version, status, validated_at, validation_score, validation_result')
    .not('validated_at', 'is', null)
    .order('validated_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) throw error

  return (data || []).map(row => ({
    test_result_id: row.id,
    agent_version_id: row.id,
    overall_score: row.validation_score || 0,
    test_details: row.validation_result || {},
    report_url: null,
    test_duration_ms: 0,
    evaluator_model: 'AI Factory v3',
    tested_at: row.validated_at,
    agent_name: row.agent_name,
    version: row.version,
    status: row.status,
    score_completeness: null,
    score_tone: null,
    score_engagement: null,
    score_compliance: null,
    score_conversion: null,
    total_test_cases: 0,
    total_failures: 0,
    total_warnings: 0,
  }))
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

// =============================================================================
// E2E TEST RESULTS - Cenários individuais
// =============================================================================

// Buscar todos os cenários E2E de um agente
export async function fetchE2EResultsByAgent(agentVersionId: string): Promise<E2ETestResult[]> {
  const { data, error } = await supabase
    .from('e2e_test_results')
    .select('*')
    .eq('agent_version_id', agentVersionId)
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching E2E results:', error)
    return []
  }

  return (data || []).map(row => ({
    id: row.id,
    agent_version_id: row.agent_version_id,
    scenario_name: row.scenario_name,
    scenario_description: row.scenario_description,
    test_type: row.test_type || 'e2e',
    lead_persona: row.lead_persona,
    initial_agent: row.initial_agent,
    expected_outcome: row.expected_outcome,
    status: row.status,
    actual_outcome: row.actual_outcome,
    total_turns: row.total_turns || 0,
    total_tokens: row.total_tokens || 0,
    duration_seconds: row.duration_seconds,
    score: row.score,
    conversation: row.conversation || [],
    modes_tested: row.modes_tested || [],
    mode_transitions: row.mode_transitions || [],
    error_message: row.error_message,
    model_used: row.model_used,
    tags: row.tags || [],
    created_at: row.created_at,
  }))
}

// Buscar execuções agrupadas (para lista principal)
export async function fetchTestExecutions(limit = 50): Promise<TestExecution[]> {
  // Primeiro, buscar os resultados E2E agrupados por agent + data aproximada
  const { data: e2eData, error: e2eError } = await supabase
    .from('e2e_test_results')
    .select(`
      id,
      agent_version_id,
      scenario_name,
      scenario_description,
      test_type,
      lead_persona,
      status,
      actual_outcome,
      total_turns,
      total_tokens,
      duration_seconds,
      score,
      model_used,
      tags,
      created_at
    `)
    .order('created_at', { ascending: false })
    .limit(500)  // Buscar mais para agrupar

  if (e2eError) {
    console.error('Error fetching E2E results:', e2eError)
    // Fallback para dados antigos se tabela não existir
    return await fetchLegacyTestExecutions(limit)
  }

  if (!e2eData || e2eData.length === 0) {
    // Se não tem dados E2E, usar dados antigos
    return await fetchLegacyTestExecutions(limit)
  }

  // Buscar info dos agentes
  const agentIds = [...new Set(e2eData.map(r => r.agent_version_id))]
  const { data: agentsData } = await supabase
    .from('agent_versions')
    .select('id, agent_name, version')
    .in('id', agentIds)

  const agentMap = new Map(agentsData?.map(a => [a.id, a]) || [])

  // Agrupar por agent + janela de tempo (5 minutos)
  const executions = new Map<string, TestExecution>()

  for (const result of e2eData) {
    const timestamp = new Date(result.created_at)
    // Agrupar por janela de 5 minutos
    const windowStart = new Date(Math.floor(timestamp.getTime() / (5 * 60 * 1000)) * (5 * 60 * 1000))
    const executionKey = `${result.agent_version_id}_${windowStart.toISOString()}`

    if (!executions.has(executionKey)) {
      const agent = agentMap.get(result.agent_version_id)
      executions.set(executionKey, {
        execution_id: executionKey,
        agent_version_id: result.agent_version_id,
        agent_name: agent?.agent_name || 'Unknown Agent',
        version: agent?.version || '?.?',
        tested_at: result.created_at,
        overall_score: 0,
        total_scenarios: 0,
        passed_scenarios: 0,
        failed_scenarios: 0,
        scenarios: [],
      })
    }

    const execution = executions.get(executionKey)!
    execution.scenarios.push({
      id: result.id,
      agent_version_id: result.agent_version_id,
      scenario_name: result.scenario_name,
      scenario_description: result.scenario_description,
      test_type: result.test_type || 'e2e',
      lead_persona: result.lead_persona,
      initial_agent: null,
      expected_outcome: null,
      status: result.status,
      actual_outcome: result.actual_outcome,
      total_turns: result.total_turns || 0,
      total_tokens: result.total_tokens || 0,
      duration_seconds: result.duration_seconds,
      score: result.score,
      conversation: [],
      modes_tested: [],
      mode_transitions: [],
      error_message: null,
      model_used: result.model_used,
      tags: result.tags || [],
      created_at: result.created_at,
    })

    execution.total_scenarios++
    if (result.status === 'passed') {
      execution.passed_scenarios++
    } else {
      execution.failed_scenarios++
    }
  }

  // Calcular score médio e ordenar
  const executionList = Array.from(executions.values())
    .map(exec => {
      const scores = exec.scenarios.filter(s => s.score !== null).map(s => s.score!)
      exec.overall_score = scores.length > 0
        ? scores.reduce((a, b) => a + b, 0) / scores.length
        : 0
      return exec
    })
    .sort((a, b) => new Date(b.tested_at).getTime() - new Date(a.tested_at).getTime())
    .slice(0, limit)

  return executionList
}

// Fallback para dados antigos (quando e2e_test_results está vazio)
async function fetchLegacyTestExecutions(limit: number): Promise<TestExecution[]> {
  const { data, error } = await supabase
    .from('agent_versions')
    .select('id, agent_name, version, status, validated_at, validation_score, validation_result')
    .not('validated_at', 'is', null)
    .order('validated_at', { ascending: false })
    .limit(limit)

  if (error) {
    console.error('Error fetching legacy test results:', error)
    return []
  }

  return (data || []).map(row => ({
    execution_id: row.id,
    agent_version_id: row.id,
    agent_name: row.agent_name,
    version: row.version,
    tested_at: row.validated_at,
    overall_score: row.validation_score || 0,
    total_scenarios: 1,  // Legacy: 1 teste por execução
    passed_scenarios: (row.validation_score || 0) >= 8 ? 1 : 0,
    failed_scenarios: (row.validation_score || 0) < 8 ? 1 : 0,
    scenarios: [],  // Sem cenários detalhados no formato antigo
  }))
}

// Buscar cenários de uma execução específica
export async function fetchScenariosForExecution(agentVersionId: string, testedAt: string): Promise<E2ETestResult[]> {
  const timestamp = new Date(testedAt)
  // Janela de 5 minutos
  const windowStart = new Date(Math.floor(timestamp.getTime() / (5 * 60 * 1000)) * (5 * 60 * 1000))
  const windowEnd = new Date(windowStart.getTime() + 5 * 60 * 1000)

  const { data, error } = await supabase
    .from('e2e_test_results')
    .select('*')
    .eq('agent_version_id', agentVersionId)
    .gte('created_at', windowStart.toISOString())
    .lt('created_at', windowEnd.toISOString())
    .order('created_at', { ascending: true })

  if (error) {
    console.error('Error fetching scenarios:', error)
    return []
  }

  return (data || []).map(row => ({
    id: row.id,
    agent_version_id: row.agent_version_id,
    scenario_name: row.scenario_name,
    scenario_description: row.scenario_description,
    test_type: row.test_type || 'e2e',
    lead_persona: row.lead_persona,
    initial_agent: row.initial_agent,
    expected_outcome: row.expected_outcome,
    status: row.status,
    actual_outcome: row.actual_outcome,
    total_turns: row.total_turns || 0,
    total_tokens: row.total_tokens || 0,
    duration_seconds: row.duration_seconds,
    score: row.score,
    conversation: row.conversation || [],
    modes_tested: row.modes_tested || [],
    mode_transitions: row.mode_transitions || [],
    error_message: row.error_message,
    model_used: row.model_used,
    tags: row.tags || [],
    created_at: row.created_at,
  }))
}
