// Database types based on Supabase schema

export interface AgentPerformanceSummary {
  agent_version_id: string
  agent_name: string
  version: string
  status: string
  is_active: boolean
  client_id: string
  sub_account_id: string | null
  last_test_score: number | null
  last_test_at: string | null
  framework_approved: boolean
  reflection_count: number
  test_report_url: string | null
  conversas_7d: number
  resolvidas_7d: number
  escalations_7d: number
  satisfacao_7d: number
  tokens_7d: number
  custo_7d: number
  conversas_30d: number
  ultima_conversa_at: string | null
  total_conversas_historico: number
  total_testes_executados: number
  created_at: string
  updated_at: string
  activated_at: string | null
}

export interface LatestTestResult {
  test_result_id: string
  agent_version_id: string
  overall_score: number
  test_details: any
  report_url: string | null
  test_duration_ms: number
  evaluator_model: string
  tested_at: string
  agent_name: string
  version: string
  status: string
  score_completeness: number | null
  score_tone: number | null
  score_engagement: number | null
  score_compliance: number | null
  score_conversion: number | null
  total_test_cases: number
  total_failures: number
  total_warnings: number
}

export interface AgentConversationSummary {
  conversation_id: string
  agent_version_id: string
  agent_name: string
  agent_version: string
  contact_id: string
  channel: string
  status: string
  started_at: string
  ended_at: string | null
  resolved_at: string | null
  escalated_at: string | null
  message_count: number
  lead_messages: number
  agent_messages: number
  first_message_at: string
  last_message_at: string
  duration_seconds: number
  response_time_avg_sec: number | null
  sentiment_score: number | null
  tokens_used: number
  cost_usd: number
}

export interface TestResultHistory {
  test_result_id: string
  agent_version_id: string
  agent_name: string
  version: string
  overall_score: number
  test_duration_ms: number
  evaluator_model: string
  tested_at: string
  completeness: number | null
  tone: number | null
  engagement: number | null
  compliance: number | null
  conversion: number | null
  cases_total: number
  cases_failed: number
  warnings_count: number
  strengths: string[]
  weaknesses: string[]
}

export interface AgentNeedingTesting {
  agent_version_id: string
  agent_name: string
  version: string
  status: string
  last_test_at: string | null
  last_test_score: number | null
  created_at: string
  updated_at: string
  test_reason: 'never_tested' | 'draft_status' | 'updated_since_test' | 'low_score' | 'needs_retest'
  priority: number
}

// E2E Test Results - Cenários individuais de teste
export interface E2ETestResult {
  id: string
  agent_version_id: string
  scenario_name: string
  scenario_description: string | null
  test_type: string
  lead_persona: string | null
  initial_agent: string | null
  expected_outcome: string | null
  status: 'passed' | 'failed' | 'timeout' | 'error'
  actual_outcome: string | null
  total_turns: number
  total_tokens: number
  duration_seconds: number | null
  score: number | null
  conversation: any[]
  modes_tested: string[]
  mode_transitions: any[]
  error_message: string | null
  model_used: string | null
  tags: string[]
  created_at: string
}

// Agrupamento de testes por execução (para o dashboard)
export interface TestExecution {
  execution_id: string  // agent_version_id + timestamp agrupado
  agent_version_id: string
  agent_name: string
  version: string
  tested_at: string
  overall_score: number
  total_scenarios: number
  passed_scenarios: number
  failed_scenarios: number
  scenarios: E2ETestResult[]
}
