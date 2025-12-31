-- ============================================
-- Migration 001: Add Testing Columns to agent_versions
-- ============================================
-- Description: Adiciona colunas necessárias para integração
--              com o testing framework em agent_versions
-- Author: AI Factory V4
-- Date: 2024-12-23
-- ============================================

-- Adicionar colunas de teste
ALTER TABLE agent_versions ADD COLUMN IF NOT EXISTS
  test_suite_id UUID,
  last_test_score DECIMAL(3,2),
  last_test_at TIMESTAMPTZ,
  test_report_url TEXT,
  framework_approved BOOLEAN DEFAULT false,
  reflection_count INTEGER DEFAULT 0;

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_agent_versions_test_score 
  ON agent_versions(last_test_score DESC)
  WHERE last_test_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_versions_framework_approved 
  ON agent_versions(framework_approved, status)
  WHERE framework_approved = true;

CREATE INDEX IF NOT EXISTS idx_agent_versions_needs_testing
  ON agent_versions(status, last_test_at)
  WHERE status = 'draft' OR last_test_at IS NULL;

-- Comentários para documentação
COMMENT ON COLUMN agent_versions.test_suite_id IS 
  '[AI Testing Framework] ID da suite de testes utilizada para validação';

COMMENT ON COLUMN agent_versions.last_test_score IS 
  '[AI Testing Framework] Score do último teste executado (0.00 - 10.00)';

COMMENT ON COLUMN agent_versions.last_test_at IS 
  '[AI Testing Framework] Timestamp do último teste executado';

COMMENT ON COLUMN agent_versions.test_report_url IS 
  '[AI Testing Framework] URL do relatório HTML do último teste';

COMMENT ON COLUMN agent_versions.framework_approved IS 
  '[AI Testing Framework] Se foi aprovado automaticamente (score >= 8.0)';

COMMENT ON COLUMN agent_versions.reflection_count IS 
  '[AI Testing Framework] Quantas vezes o agente foi melhorado automaticamente';

-- Verificação
DO $$
BEGIN
  RAISE NOTICE 'Migration 001 completed successfully';
  RAISE NOTICE 'Added 6 new columns to agent_versions';
  RAISE NOTICE 'Created 3 performance indexes';
END $$;
