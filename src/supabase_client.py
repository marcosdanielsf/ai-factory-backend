"""
AI Factory Testing Framework - Supabase Client
==============================================
Cliente Supabase com métodos helpers para o framework.
"""

import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Cliente Supabase com métodos específicos para o testing framework"""
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info(f"Supabase client initialized: {self.url}")
    
    # ============================================
    # AGENT VERSIONS
    # ============================================
    
    def get_agent_version(self, agent_id: str) -> Optional[Dict]:
        """Busca agent_version por ID"""
        try:
            response = self.client.table('agent_versions')\
                .select('*, clients(*), sub_accounts(*)')\
                .eq('id', agent_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {e}")
            return None
    
    def get_agents_needing_testing(self, limit: int = 100) -> List[Dict]:
        """Busca agentes que precisam ser testados"""
        try:
            response = self.client.table('vw_agents_needing_testing')\
                .select('*')\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching agents needing testing: {e}")
            return []
    
    def update_agent_test_results(
        self, 
        agent_id: str, 
        score: float, 
        report_url: str,
        test_result_id: str
    ):
        """Atualiza agent_version com resultados do teste"""
        try:
            self.client.table('agent_versions').update({
                'last_test_score': score,
                'last_test_at': datetime.utcnow().isoformat(),
                'test_report_url': report_url,
                'framework_approved': score >= 8.0,
                'status': 'active' if score >= 8.0 else 'needs_improvement'
            }).eq('id', agent_id).execute()
            
            logger.info(f"Updated agent {agent_id}: score={score}, approved={score >= 8.0}")
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise
    
    # ============================================
    # TEST RESULTS
    # ============================================
    
    def save_test_result(
        self, 
        agent_version_id: str,
        overall_score: float,
        test_details: Dict,
        report_url: str,
        test_duration_ms: int,
        evaluator_model: str = 'claude-opus-4'
    ) -> str:
        """Salva resultado de teste"""
        try:
            response = self.client.table('agenttest_test_results').insert({
                'agent_version_id': agent_version_id,
                'overall_score': overall_score,
                'test_details': test_details,
                'report_url': report_url,
                'test_duration_ms': test_duration_ms,
                'evaluator_model': evaluator_model
            }).execute()
            
            test_result_id = response.data[0]['id']
            logger.info(f"Saved test result {test_result_id} for agent {agent_version_id}")
            return test_result_id
        except Exception as e:
            logger.error(f"Error saving test result: {e}")
            raise
    
    def get_test_results_history(
        self, 
        agent_version_id: str, 
        limit: int = 20
    ) -> List[Dict]:
        """Busca histórico de testes de um agente"""
        try:
            response = self.client.table('agenttest_test_results')\
                .select('*')\
                .eq('agent_version_id', agent_version_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching test history: {e}")
            return []
    
    # ============================================
    # SKILLS
    # ============================================
    
    def get_skill(self, agent_version_id: str) -> Optional[Dict]:
        """Busca skill de um agente (versão mais recente)"""
        try:
            response = self.client.table('agenttest_skills')\
                .select('*')\
                .eq('agent_version_id', agent_version_id)\
                .order('version', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching skill: {e}")
            return None
    
    def save_skill(
        self,
        agent_version_id: str,
        instructions: str,
        examples: str = None,
        rubric: str = None,
        test_cases: List[Dict] = None,
        local_file_path: str = None
    ) -> str:
        """Salva ou atualiza skill"""
        try:
            # Busca versão atual
            current = self.get_skill(agent_version_id)
            new_version = (current['version'] + 1) if current else 1
            
            response = self.client.table('agenttest_skills').insert({
                'agent_version_id': agent_version_id,
                'version': new_version,
                'instructions': instructions,
                'examples': examples,
                'rubric': rubric,
                'test_cases': test_cases,
                'local_file_path': local_file_path,
                'last_synced_at': datetime.utcnow().isoformat()
            }).execute()
            
            skill_id = response.data[0]['id']
            logger.info(f"Saved skill {skill_id} v{new_version} for agent {agent_version_id}")
            return skill_id
        except Exception as e:
            logger.error(f"Error saving skill: {e}")
            raise
    
    # ============================================
    # CONVERSATIONS (para gerar exemplos)
    # ============================================
    
    def get_recent_conversations(
        self, 
        agent_version_id: str, 
        limit: int = 50,
        min_score: float = 8.0
    ) -> List[Dict]:
        """Busca conversas recentes de alta qualidade"""
        try:
            response = self.client.table('agent_conversations')\
                .select('*, agent_conversation_messages(*)')\
                .eq('agent_version_id', agent_version_id)\
                .gte('sentiment_score', min_score)\
                .order('started_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []
    
    # ============================================
    # METRICS (para KNOWLEDGE.md)
    # ============================================
    
    def get_agent_metrics(
        self, 
        agent_version_id: str, 
        days: int = 30
    ) -> List[Dict]:
        """Busca métricas diárias do agente"""
        try:
            response = self.client.table('agent_metrics')\
                .select('*')\
                .eq('agent_version_id', agent_version_id)\
                .gte('data', f'now() - interval \'{days} days\'')\
                .order('data', desc=False)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return []
