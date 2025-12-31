-- ============================================
-- Migration 002: Create agenttest_test_results Table
-- ============================================
-- Description: Tabela para armazenar resultados detalhados
--              dos testes executados pelo framework
-- Author: AI Factory V4
-- Date: 2024-12-23
-- ============================================

CREATE TABLE IF NOT EXISTS agenttest_test_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_version_id UUID NOT NULL REFERENCES agent_versions(id) ON DELETE CASCADE,
  
  -- Scores principais
  overall_score DECIMAL(3,2) NOT NULL,
  
  -- Detalhes do teste (JSONB)
  test_details JSONB NOT NULL DEFAULT '{}',
  -- Estrutura esperada:
  -- {
  --   "scores": {
  --     "completeness": 8.5,
  --     "tone": 9.0,
  --     "engagement": 7.5,
  --     "compliance": 10.0,
  --     "conversion": 8.0
  --   },
  --   "test_cases": [
  --     {
  --       "name": "Lead frio - primeira mensagem",
  --       "passed": true,
  --       "score": 9.0,
  --       "feedback": "Excelente abordagem consultiva"
  --     }
  --   ],
  --   "failures": [],
  --   "warnings": ["Tom levemente robótico no cenário 3"],
  --   "strengths": ["BANT completo", "Empatia elevada"],
  --   "weaknesses": ["Não explorou dor profundamente"]
  -- }
  
  -- Relatório
  report_url TEXT,
  report_html TEXT, -- Opcional: armazenar HTML inline
  
  -- Metadados de execução
  test_duration_ms INTEGER,
  evaluator_model TEXT DEFAULT 'claude-opus-4',
  test_suite_version TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT valid_overall_score CHECK (overall_score >= 0 AND overall_score <= 10),
  CONSTRAINT valid_duration CHECK (test_duration_ms > 0)
);

-- Índices para queries rápidas
CREATE INDEX idx_test_results_agent_version 
  ON agenttest_test_results(agent_version_id, created_at DESC);

CREATE INDEX idx_test_results_score 
  ON agenttest_test_results(overall_score DESC, created_at DESC);

CREATE INDEX idx_test_results_created_at 
  ON agenttest_test_results(created_at DESC);

-- Índice GIN para busca em JSONB
CREATE INDEX idx_test_results_details 
  ON agenttest_test_results USING gin(test_details);

-- Comentários
COMMENT ON TABLE agenttest_test_results IS 
  '[AI Testing Framework] Resultados detalhados dos testes de agentes - SAFE TO DELETE';

COMMENT ON COLUMN agenttest_test_results.overall_score IS 
  'Score final agregado (0-10) considerando todos os critérios';

COMMENT ON COLUMN agenttest_test_results.test_details IS 
  'JSON com scores detalhados, casos de teste, failures, warnings e feedback';

COMMENT ON COLUMN agenttest_test_results.report_url IS 
  'URL pública do relatório HTML (storage/outputs)';

COMMENT ON COLUMN agenttest_test_results.evaluator_model IS 
  'Modelo LLM usado como judge (ex: claude-opus-4)';

-- Verificação
DO $$
BEGIN
  RAISE NOTICE 'Migration 002 completed successfully';
  RAISE NOTICE 'Created table: agenttest_test_results';
  RAISE NOTICE 'Created 4 indexes for optimal query performance';
END $$;
