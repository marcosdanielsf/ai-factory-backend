import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { testAgent, type TestAgentRequest } from '@/lib/api'
import type {
  AgentPerformanceSummary,
  LatestTestResult,
  AgentNeedingTesting
} from '@/types/database'

// Fetch all agents with performance data
export function useAgents(limit = 50) {
  return useQuery({
    queryKey: ['agents', limit],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vw_agent_performance_summary')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error
      return data as AgentPerformanceSummary[]
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refresh every minute
  })
}

// Fetch single agent details
export function useAgent(agentVersionId: string | null) {
  return useQuery({
    queryKey: ['agent', agentVersionId],
    queryFn: async () => {
      if (!agentVersionId) return null

      const { data, error } = await supabase
        .from('vw_agent_performance_summary')
        .select('*')
        .eq('agent_version_id', agentVersionId)
        .single()

      if (error) throw error
      return data as AgentPerformanceSummary
    },
    enabled: !!agentVersionId,
  })
}

// Fetch latest test results
export function useLatestTestResults(limit = 20) {
  return useQuery({
    queryKey: ['latest-tests', limit],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vw_latest_test_results')
        .select('*')
        .limit(limit)

      if (error) throw error
      return data as LatestTestResult[]
    },
    staleTime: 30000,
  })
}

// Fetch agents needing testing
export function useAgentsNeedingTesting() {
  return useQuery({
    queryKey: ['agents-needing-testing'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vw_agents_needing_testing')
        .select('*')
        .order('priority', { ascending: true })

      if (error) throw error
      return data as AgentNeedingTesting[]
    },
    staleTime: 60000, // 1 minute
  })
}

// Mutation to test an agent
export function useTestAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: TestAgentRequest) => testAgent(request),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      queryClient.invalidateQueries({ queryKey: ['latest-tests'] })
      queryClient.invalidateQueries({ queryKey: ['agents-needing-testing'] })
    },
  })
}

// Fetch test history for specific agent
export function useTestHistory(agentVersionId: string | null) {
  return useQuery({
    queryKey: ['test-history', agentVersionId],
    queryFn: async () => {
      if (!agentVersionId) return []

      const { data, error } = await supabase
        .from('vw_test_results_history')
        .select('*')
        .eq('agent_version_id', agentVersionId)
        .order('tested_at', { ascending: false })

      if (error) throw error
      return data
    },
    enabled: !!agentVersionId,
  })
}

// Subscribe to real-time test updates
export function useRealtimeTestUpdates() {
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: ['realtime-setup'],
    queryFn: async () => {
      const channel = supabase
        .channel('test-results-changes')
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'agenttest_test_results',
          },
          (payload) => {
            console.log('Test result updated:', payload)
            // Invalidate queries to refetch data
            queryClient.invalidateQueries({ queryKey: ['agents'] })
            queryClient.invalidateQueries({ queryKey: ['latest-tests'] })
          }
        )
        .subscribe()

      return () => {
        supabase.removeChannel(channel)
      }
    },
    staleTime: Infinity,
  })
}
