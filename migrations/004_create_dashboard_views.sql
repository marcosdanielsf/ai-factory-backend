-- ============================================
-- Migration 004: Create Dashboard Views
-- ============================================
-- Description: Views otimizadas para queries do dashboard
-- Author: AI Factory V4
-- Date: 2024-12-23
-- ============================================

-- ============================================
-- VIEW 1: Agent Performance Summary
-- ============================================
-- Agregação de métricas, conversas e testes por agente

CREATE OR REPLACE VIEW vw_agent_performance_summary AS
SELECT 
  av.id as agent_version_id,
  av.agent_name,
  av.version,
  av.status,
  av.is_active,
  av.client_id,
  av.sub_account_id,
  
  -- Scores de teste
  av.last_test_score,
  av.last_test_at,
  av.framework_approved,
  av.reflection_count,
  av.test_report_url,
  
  -- Métricas agregadas últimos 7 dias
  COALESCE(SUM(am.total_conversas) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '7 days'
  ), 0)::INTEGER AS conversas_7d,
  
  COALESCE(SUM(am.conversas_resolvidas) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '7 days'
  ), 0)::INTEGER AS resolvidas_7d,
  
  COALESCE(SUM(am.escalations) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '7 days'
  ), 0)::INTEGER AS escalations_7d,
  
  COALESCE(AVG(am.satisfacao_media) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '7 days'
  ), 0)::DECIMAL(3,2) AS satisfacao_7d,
  
  COALESCE(SUM(am.tokens_consumidos) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '7 days'
  ), 0)::BIGINT AS tokens_7d,
  
  COALESCE(SUM(am.custo_estimado) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '7 days'
  ), 0)::DECIMAL(10,4) AS custo_7d,
  
  -- Métricas últimos 30 dias
  COALESCE(SUM(am.total_conversas) FILTER (
    WHERE am.data >= CURRENT_DATE - INTERVAL '30 days'
  ), 0)::INTEGER AS conversas_30d,
  
  -- Última conversa
  MAX(ac.started_at) as ultima_conversa_at,
  
  -- Contadores totais
  COUNT(DISTINCT ac.id)::INTEGER as total_conversas_historico,
  COUNT(DISTINCT tr.id)::INTEGER as total_testes_executados,
  
  -- Timestamps
  av.created_at,
  av.updated_at,
  av.activated_at
  
FROM agent_versions av
LEFT JOIN agent_metrics am ON am.agent_version_id = av.id
LEFT JOIN agent_conversations ac ON ac.agent_version_id = av.id
LEFT JOIN agenttest_test_results tr ON tr.agent_version_id = av.id

GROUP BY 
  av.id, av.agent_name, av.version, av.status, av.is_active,
  av.client_id, av.sub_account_id, av.last_test_score, 
  av.last_test_at, av.framework_approved, av.reflection_count,
  av.test_report_url, av.created_at, av.updated_at, av.activated_at;

COMMENT ON VIEW vw_agent_performance_summary IS 
  '[AI Testing Framework] Resumo de performance por agente com métricas agregadas';


-- ============================================
-- VIEW 2: Latest Test Results
-- ============================================
-- Último teste executado para cada agente

CREATE OR REPLACE VIEW vw_latest_test_results AS
SELECT DISTINCT ON (tr.agent_version_id)
  tr.id as test_result_id,
  tr.agent_version_id,
  tr.overall_score,
  tr.test_details,
  tr.report_url,
  tr.test_duration_ms,
  tr.evaluator_model,
  tr.created_at as tested_at,
  
  -- Info do agente
  av.agent_name,
  av.version,
  av.status,
  
  -- Scores detalhados (extraídos do JSONB)
  (tr.test_details->'scores'->>'completeness')::DECIMAL(3,2) as score_completeness,
  (tr.test_details->'scores'->>'tone')::DECIMAL(3,2) as score_tone,
  (tr.test_details->'scores'->>'engagement')::DECIMAL(3,2) as score_engagement,
  (tr.test_details->'scores'->>'compliance')::DECIMAL(3,2) as score_compliance,
  (tr.test_details->'scores'->>'conversion')::DECIMAL(3,2) as score_conversion,
  
  -- Contadores
  jsonb_array_length(tr.test_details->'test_cases') as total_test_cases,
  jsonb_array_length(tr.test_details->'failures') as total_failures,
  jsonb_array_length(tr.test_details->'warnings') as total_warnings

FROM agenttest_test_results tr
JOIN agent_versions av ON av.id = tr.agent_version_id
ORDER BY tr.agent_version_id, tr.created_at DESC;

COMMENT ON VIEW vw_latest_test_results IS 
  '[AI Testing Framework] Último resultado de teste para cada agente';


-- ============================================
-- VIEW 3: Conversations with Message Stats
-- ============================================
-- Conversas com estatísticas de mensagens

CREATE OR REPLACE VIEW vw_agent_conversations_summary AS
SELECT 
  ac.id as conversation_id,
  ac.agent_version_id,
  av.agent_name,
  av.version as agent_version,
  ac.contact_id,
  ac.channel,
  ac.status,
  ac.started_at,
  ac.ended_at,
  ac.resolved_at,
  ac.escalated_at,
  
  -- Contadores de mensagens
  COUNT(m.id)::INTEGER as message_count,
  COUNT(m.id) FILTER (WHERE m.is_from_lead)::INTEGER as lead_messages,
  COUNT(m.id) FILTER (WHERE NOT m.is_from_lead)::INTEGER as agent_messages,
  
  -- Primeira e última mensagem
  MIN(m.created_at) as first_message_at,
  MAX(m.created_at) as last_message_at,
  
  -- Duração da conversa
  EXTRACT(EPOCH FROM (MAX(m.created_at) - MIN(m.created_at)))::INTEGER as duration_seconds,
  
  -- Métricas do agent_conversations
  ac.response_time_avg_sec,
  ac.sentiment_score,
  ac.tokens_used,
  ac.cost_usd
  
FROM agent_conversations ac
JOIN agent_versions av ON av.id = ac.agent_version_id
LEFT JOIN agent_conversation_messages m ON m.conversation_id = ac.id

GROUP BY 
  ac.id, ac.agent_version_id, av.agent_name, av.version,
  ac.contact_id, ac.channel, ac.status, ac.started_at, ac.ended_at,
  ac.resolved_at, ac.escalated_at, ac.response_time_avg_sec,
  ac.sentiment_score, ac.tokens_used, ac.cost_usd;

COMMENT ON VIEW vw_agent_conversations_summary IS 
  '[AI Testing Framework] Resumo de conversas com estatísticas de mensagens';


-- ============================================
-- VIEW 4: Test Results History
-- ============================================
-- Histórico completo de testes para análise temporal

CREATE OR REPLACE VIEW vw_test_results_history AS
SELECT 
  tr.id as test_result_id,
  tr.agent_version_id,
  av.agent_name,
  av.version,
  tr.overall_score,
  tr.test_duration_ms,
  tr.evaluator_model,
  tr.created_at as tested_at,
  
  -- Scores detalhados
  (tr.test_details->'scores'->>'completeness')::DECIMAL(3,2) as completeness,
  (tr.test_details->'scores'->>'tone')::DECIMAL(3,2) as tone,
  (tr.test_details->'scores'->>'engagement')::DECIMAL(3,2) as engagement,
  (tr.test_details->'scores'->>'compliance')::DECIMAL(3,2) as compliance,
  (tr.test_details->'scores'->>'conversion')::DECIMAL(3,2) as conversion,
  
  -- Contadores
  jsonb_array_length(tr.test_details->'test_cases') as cases_total,
  jsonb_array_length(tr.test_details->'failures') as cases_failed,
  jsonb_array_length(tr.test_details->'warnings') as warnings_count,
  
  -- Arrays como texto para facilitar query
  ARRAY(SELECT jsonb_array_elements_text(tr.test_details->'strengths')) as strengths,
  ARRAY(SELECT jsonb_array_elements_text(tr.test_details->'weaknesses')) as weaknesses

FROM agenttest_test_results tr
JOIN agent_versions av ON av.id = tr.agent_version_id
ORDER BY tr.created_at DESC;

COMMENT ON VIEW vw_test_results_history IS 
  '[AI Testing Framework] Histórico completo de testes para análise de evolução';


-- ============================================
-- VIEW 5: Agents Needing Testing
-- ============================================
-- Agentes que precisam ser testados

CREATE OR REPLACE VIEW vw_agents_needing_testing AS
SELECT 
  av.id as agent_version_id,
  av.agent_name,
  av.version,
  av.status,
  av.last_test_at,
  av.last_test_score,
  av.created_at,
  av.updated_at,
  
  -- Razão para testar
  CASE 
    WHEN av.last_test_at IS NULL THEN 'never_tested'
    WHEN av.status = 'draft' THEN 'draft_status'
    WHEN av.updated_at > av.last_test_at THEN 'updated_since_test'
    WHEN av.last_test_score < 8.0 THEN 'low_score'
    ELSE 'needs_retest'
  END as test_reason,
  
  -- Prioridade (1 = mais urgente)
  CASE 
    WHEN av.last_test_at IS NULL THEN 1
    WHEN av.status = 'draft' THEN 2
    WHEN av.last_test_score < 6.0 THEN 2
    WHEN av.last_test_score < 8.0 THEN 3
    ELSE 4
  END as priority

FROM agent_versions av
WHERE 
  av.last_test_at IS NULL
  OR av.status = 'draft'
  OR av.updated_at > av.last_test_at
  OR av.last_test_score < 8.0
  
ORDER BY priority, av.created_at DESC;

COMMENT ON VIEW vw_agents_needing_testing IS 
  '[AI Testing Framework] Agentes que precisam ser testados com priorização';


-- Verificação final
DO $$
BEGIN
  RAISE NOTICE 'Migration 004 completed successfully';
  RAISE NOTICE 'Created 5 dashboard views:';
  RAISE NOTICE '  - vw_agent_performance_summary';
  RAISE NOTICE '  - vw_latest_test_results';
  RAISE NOTICE '  - vw_agent_conversations_summary';
  RAISE NOTICE '  - vw_test_results_history';
  RAISE NOTICE '  - vw_agents_needing_testing';
END $$;
