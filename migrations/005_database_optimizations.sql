-- ============================================
-- Migration 005: Database Optimizations
-- ============================================
-- Description: Otimizações de performance incluindo:
--   - Soft delete em todas as tabelas do framework
--   - Índices compostos otimizados
--   - Índices parciais para queries frequentes
--   - Índices para ordenação comum
--   - Estatísticas e vacuum settings
-- Author: AI Factory V4
-- Date: 2025-01-03
-- ============================================

-- ============================================
-- PART 1: SOFT DELETE COLUMNS
-- ============================================

-- Adicionar colunas de soft delete em agent_versions
ALTER TABLE agent_versions
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by UUID;

-- Adicionar colunas de soft delete em agenttest_test_results
ALTER TABLE agenttest_test_results
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by UUID;

-- Adicionar colunas de soft delete em agenttest_skills
ALTER TABLE agenttest_skills
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by UUID;

-- Adicionar colunas de soft delete em agent_conversations
ALTER TABLE agent_conversations
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by UUID;

-- Adicionar colunas de soft delete em agent_metrics
ALTER TABLE agent_metrics
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by UUID;

-- Comentários para documentação
COMMENT ON COLUMN agent_versions.deleted_at IS
    '[Soft Delete] Timestamp da exclusão lógica';
COMMENT ON COLUMN agent_versions.deleted_by IS
    '[Soft Delete] ID do usuário que excluiu';

COMMENT ON COLUMN agenttest_test_results.deleted_at IS
    '[Soft Delete] Timestamp da exclusão lógica';
COMMENT ON COLUMN agenttest_test_results.deleted_by IS
    '[Soft Delete] ID do usuário que excluiu';

COMMENT ON COLUMN agenttest_skills.deleted_at IS
    '[Soft Delete] Timestamp da exclusão lógica';
COMMENT ON COLUMN agenttest_skills.deleted_by IS
    '[Soft Delete] ID do usuário que excluiu';

-- ============================================
-- PART 2: PERFORMANCE INDEXES
-- ============================================

-- === AGENT_VERSIONS ===

-- Índice parcial para agentes ativos (query mais comum)
CREATE INDEX IF NOT EXISTS idx_agent_versions_active
    ON agent_versions(status, is_active, last_test_at DESC)
    WHERE deleted_at IS NULL AND is_active = true;

-- Índice para busca por cliente
CREATE INDEX IF NOT EXISTS idx_agent_versions_client_lookup
    ON agent_versions(client_id, status, created_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para busca por sub_account
CREATE INDEX IF NOT EXISTS idx_agent_versions_subaccount_lookup
    ON agent_versions(sub_account_id, status)
    WHERE deleted_at IS NULL;

-- Índice para soft delete queries
CREATE INDEX IF NOT EXISTS idx_agent_versions_deleted
    ON agent_versions(deleted_at)
    WHERE deleted_at IS NOT NULL;

-- Índice composto para dashboard de performance
CREATE INDEX IF NOT EXISTS idx_agent_versions_performance
    ON agent_versions(framework_approved, last_test_score DESC, last_test_at DESC)
    WHERE deleted_at IS NULL;

-- === AGENTTEST_TEST_RESULTS ===

-- Índice para histórico de testes por agente (com soft delete)
DROP INDEX IF EXISTS idx_test_results_agent_version;
CREATE INDEX idx_test_results_agent_version_v2
    ON agenttest_test_results(agent_version_id, created_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para busca por score (ranking)
DROP INDEX IF EXISTS idx_test_results_score;
CREATE INDEX idx_test_results_score_v2
    ON agenttest_test_results(overall_score DESC, created_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para relatórios diários/semanais
CREATE INDEX IF NOT EXISTS idx_test_results_daily
    ON agenttest_test_results(DATE(created_at), overall_score)
    WHERE deleted_at IS NULL;

-- Índice para buscar testes por modelo avaliador
CREATE INDEX IF NOT EXISTS idx_test_results_evaluator
    ON agenttest_test_results(evaluator_model, created_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para soft delete queries
CREATE INDEX IF NOT EXISTS idx_test_results_deleted
    ON agenttest_test_results(deleted_at)
    WHERE deleted_at IS NOT NULL;

-- === AGENTTEST_SKILLS ===

-- Índice para busca de skill mais recente (com soft delete)
DROP INDEX IF EXISTS idx_skills_agent_version;
CREATE INDEX idx_skills_agent_version_v2
    ON agenttest_skills(agent_version_id, version DESC)
    WHERE deleted_at IS NULL;

-- Índice para sincronização
DROP INDEX IF EXISTS idx_skills_sync_source;
CREATE INDEX idx_skills_sync_v2
    ON agenttest_skills(sync_source, last_synced_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para soft delete queries
CREATE INDEX IF NOT EXISTS idx_skills_deleted
    ON agenttest_skills(deleted_at)
    WHERE deleted_at IS NOT NULL;

-- === AGENT_CONVERSATIONS ===

-- Índice para conversas recentes por agente
CREATE INDEX IF NOT EXISTS idx_conversations_agent_recent
    ON agent_conversations(agent_version_id, started_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para conversas por status
CREATE INDEX IF NOT EXISTS idx_conversations_status
    ON agent_conversations(status, started_at DESC)
    WHERE deleted_at IS NULL;

-- Índice para busca por sentiment score (boas conversas)
CREATE INDEX IF NOT EXISTS idx_conversations_sentiment
    ON agent_conversations(agent_version_id, sentiment_score DESC)
    WHERE deleted_at IS NULL AND sentiment_score >= 8.0;

-- Índice para canal de comunicação
CREATE INDEX IF NOT EXISTS idx_conversations_channel
    ON agent_conversations(channel, started_at DESC)
    WHERE deleted_at IS NULL;

-- === AGENT_METRICS ===

-- Índice para métricas por período
CREATE INDEX IF NOT EXISTS idx_metrics_period
    ON agent_metrics(agent_version_id, data DESC)
    WHERE deleted_at IS NULL;

-- Índice para agregação diária
CREATE INDEX IF NOT EXISTS idx_metrics_daily_agg
    ON agent_metrics(data, agent_version_id)
    WHERE deleted_at IS NULL;

-- ============================================
-- PART 3: COMPOSITE INDEXES FOR COMMON QUERIES
-- ============================================

-- Índice para view vw_agents_needing_testing
CREATE INDEX IF NOT EXISTS idx_agents_testing_queue
    ON agent_versions(
        last_test_at NULLS FIRST,
        status,
        last_test_score NULLS LAST,
        updated_at DESC
    )
    WHERE deleted_at IS NULL
      AND (last_test_at IS NULL
           OR status = 'draft'
           OR last_test_score < 8.0);

-- Índice para dashboard de performance geral
CREATE INDEX IF NOT EXISTS idx_agents_dashboard
    ON agent_versions(
        client_id,
        is_active,
        framework_approved,
        last_test_score DESC
    )
    WHERE deleted_at IS NULL;

-- ============================================
-- PART 4: COVERING INDEXES (INCLUDE)
-- ============================================

-- Covering index para listagem de agentes (evita table lookup)
CREATE INDEX IF NOT EXISTS idx_agents_list_covering
    ON agent_versions(client_id, status)
    INCLUDE (agent_name, version, last_test_score, last_test_at, framework_approved)
    WHERE deleted_at IS NULL;

-- Covering index para resultados de teste
CREATE INDEX IF NOT EXISTS idx_test_results_covering
    ON agenttest_test_results(agent_version_id, created_at DESC)
    INCLUDE (overall_score, test_duration_ms, evaluator_model)
    WHERE deleted_at IS NULL;

-- ============================================
-- PART 5: STATISTICS AND VACUUM SETTINGS
-- ============================================

-- Aumentar estatísticas para colunas frequentemente filtradas
ALTER TABLE agent_versions
    ALTER COLUMN status SET STATISTICS 1000,
    ALTER COLUMN is_active SET STATISTICS 1000,
    ALTER COLUMN framework_approved SET STATISTICS 500,
    ALTER COLUMN last_test_score SET STATISTICS 500;

ALTER TABLE agenttest_test_results
    ALTER COLUMN overall_score SET STATISTICS 500,
    ALTER COLUMN evaluator_model SET STATISTICS 200;

-- Configurar autovacuum mais agressivo para tabelas com muita escrita
ALTER TABLE agenttest_test_results SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

ALTER TABLE agent_conversations SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

ALTER TABLE agent_metrics SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

-- ============================================
-- PART 6: UPDATE VIEWS FOR SOFT DELETE
-- ============================================

-- Atualizar view para considerar soft delete
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
    av.deleted_at IS NULL  -- Soft delete filter
    AND (
        av.last_test_at IS NULL
        OR av.status = 'draft'
        OR av.updated_at > av.last_test_at
        OR av.last_test_score < 8.0
    )
ORDER BY priority, av.created_at DESC;

-- Atualizar view de performance para soft delete
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
LEFT JOIN agent_metrics am ON am.agent_version_id = av.id AND am.deleted_at IS NULL
LEFT JOIN agent_conversations ac ON ac.agent_version_id = av.id AND ac.deleted_at IS NULL
LEFT JOIN agenttest_test_results tr ON tr.agent_version_id = av.id AND tr.deleted_at IS NULL

WHERE av.deleted_at IS NULL  -- Soft delete filter

GROUP BY
    av.id, av.agent_name, av.version, av.status, av.is_active,
    av.client_id, av.sub_account_id, av.last_test_score,
    av.last_test_at, av.framework_approved, av.reflection_count,
    av.test_report_url, av.created_at, av.updated_at, av.activated_at;

-- ============================================
-- PART 7: HELPER FUNCTIONS
-- ============================================

-- Função para soft delete com cascade
CREATE OR REPLACE FUNCTION soft_delete_cascade(
    p_table_name TEXT,
    p_record_id UUID,
    p_deleted_by UUID DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    EXECUTE format(
        'UPDATE %I SET deleted_at = NOW(), deleted_by = $2 WHERE id = $1 AND deleted_at IS NULL',
        p_table_name
    ) USING p_record_id, p_deleted_by;

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    RETURN affected_rows > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para restaurar soft delete
CREATE OR REPLACE FUNCTION restore_soft_delete(
    p_table_name TEXT,
    p_record_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    EXECUTE format(
        'UPDATE %I SET deleted_at = NULL, deleted_by = NULL WHERE id = $1 AND deleted_at IS NOT NULL',
        p_table_name
    ) USING p_record_id;

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    RETURN affected_rows > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para purgar registros deletados antigos
CREATE OR REPLACE FUNCTION purge_old_deleted_records(
    p_table_name TEXT,
    p_days_old INTEGER DEFAULT 90
) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    EXECUTE format(
        'DELETE FROM %I WHERE deleted_at IS NOT NULL AND deleted_at < NOW() - ($1 || '' days'')::INTERVAL',
        p_table_name
    ) USING p_days_old;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Purged % records from % older than % days',
        deleted_count, p_table_name, p_days_old;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- PART 8: ANALYZE TABLES
-- ============================================

-- Atualizar estatísticas após criar índices
ANALYZE agent_versions;
ANALYZE agenttest_test_results;
ANALYZE agenttest_skills;
ANALYZE agent_conversations;
ANALYZE agent_metrics;

-- ============================================
-- VERIFICATION
-- ============================================

DO $$
DECLARE
    idx_count INTEGER;
BEGIN
    -- Conta índices criados
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE tablename IN ('agent_versions', 'agenttest_test_results', 'agenttest_skills', 'agent_conversations', 'agent_metrics');

    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Migration 005 completed successfully';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Added soft delete columns to 5 tables';
    RAISE NOTICE 'Created/updated % total indexes', idx_count;
    RAISE NOTICE 'Updated 2 views with soft delete support';
    RAISE NOTICE 'Created 3 helper functions';
    RAISE NOTICE 'Analyzed all affected tables';
    RAISE NOTICE '==========================================';
END $$;
