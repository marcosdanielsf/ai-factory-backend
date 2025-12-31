import { createClient } from '@/lib/supabase/client'

/**
 * Update the system_prompt and hyperpersonalization config of an agent
 */
export async function updateAgentPrompt(
  agentVersionId: string,
  systemPrompt: string,
  hyperpersonalizationConfig?: {
    tone?: string
    forbidden_words?: string[]
    knowledge_base_ids?: string[]
  }
) {
  const supabase = createClient()

  const updateData: any = {
    system_prompt: systemPrompt,
    updated_at: new Date().toISOString()
  }

  // Add hyperpersonalization config if provided
  if (hyperpersonalizationConfig) {
    updateData.hyperpersonalization_config = hyperpersonalizationConfig
  }

  const { data, error } = await supabase
    .from('agent_versions')
    .update(updateData)
    .eq('agent_version_id', agentVersionId)
    .select()
    .single()

  if (error) throw error
  return data
}

/**
 * Create a new version of an agent (for version control)
 */
export async function createAgentVersion(
  baseAgentId: string,
  versionNumber: string,
  systemPrompt: string
) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('agent_versions')
    .insert({
      agent_id: baseAgentId,
      version: versionNumber,
      system_prompt: systemPrompt,
      validation_status: 'draft',
      is_active: false
    })
    .select()
    .single()

  if (error) throw error
  return data
}
