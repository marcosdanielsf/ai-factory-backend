-- ============================================
-- Migration 003: Create agenttest_skills Table
-- ============================================
-- Description: Tabela para armazenar skills dos agentes
--              (instruções, exemplos, rubrica) sincronizados
--              do Obsidian/arquivos locais
-- Author: AI Factory V4
-- Date: 2024-12-23
-- ============================================

CREATE TABLE IF NOT EXISTS agenttest_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_version_id UUID NOT NULL REFERENCES agent_versions(id) ON DELETE CASCADE,
  
  -- Conteúdo do skill (Markdown)
  instructions TEXT NOT NULL,  -- INSTRUCTIONS.md (Custom Instructions)
  examples TEXT,               -- EXAMPLES.md (Few-shot examples)
  rubric TEXT,                 -- RUBRIC.md (Evaluation criteria)
  test_cases JSONB,            -- test-cases.json (Test scenarios)
  
  -- Versionamento
  version INTEGER NOT NULL DEFAULT 1,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Sync info (para integração com Obsidian)
  local_file_path TEXT,        -- skills/isabella-sdr/
  last_synced_at TIMESTAMPTZ,
  sync_source TEXT,            -- 'manual', 'obsidian', 'api'
  
  -- Metadados
  metadata JSONB DEFAULT '{}', -- Info adicional flexível
  
  -- Constraint: apenas uma skill ativa por agent_version
  UNIQUE(agent_version_id, version)
);

-- Índices
CREATE INDEX idx_skills_agent_version 
  ON agenttest_skills(agent_version_id, version DESC);

CREATE INDEX idx_skills_updated_at 
  ON agenttest_skills(updated_at DESC);

CREATE INDEX idx_skills_sync_source 
  ON agenttest_skills(sync_source, last_synced_at DESC);

-- Índice para busca full-text nas instruções
CREATE INDEX idx_skills_instructions_search 
  ON agenttest_skills USING gin(to_tsvector('english', instructions));

-- Function para auto-update do updated_at
CREATE OR REPLACE FUNCTION update_agenttest_skills_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trigger_update_agenttest_skills_timestamp
  BEFORE UPDATE ON agenttest_skills
  FOR EACH ROW
  EXECUTE FUNCTION update_agenttest_skills_updated_at();

-- Comentários
COMMENT ON TABLE agenttest_skills IS 
  '[AI Testing Framework] Skills dos agentes (instruções, exemplos, rubrica) - SAFE TO DELETE';

COMMENT ON COLUMN agenttest_skills.instructions IS 
  'Instruções customizadas (Custom Instructions do Claude Project)';

COMMENT ON COLUMN agenttest_skills.examples IS 
  'Exemplos de conversas excelentes (few-shot learning)';

COMMENT ON COLUMN agenttest_skills.rubric IS 
  'Critérios de avaliação detalhados por dimensão';

COMMENT ON COLUMN agenttest_skills.test_cases IS 
  'JSON array com cenários de teste (20+ casos)';

COMMENT ON COLUMN agenttest_skills.local_file_path IS 
  'Caminho local no Obsidian/Dropbox para sincronização';

-- Verificação
DO $$
BEGIN
  RAISE NOTICE 'Migration 003 completed successfully';
  RAISE NOTICE 'Created table: agenttest_skills';
  RAISE NOTICE 'Created 4 indexes and 1 trigger';
END $$;
