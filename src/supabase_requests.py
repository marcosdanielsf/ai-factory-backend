"""
AI Factory Testing Framework - Supabase Client (requests-based)
================================================================
Cliente Supabase usando requests com retry logic para conexões instáveis.
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class SupabaseRequestsClient:
    """
    Cliente Supabase baseado em requests com retry automático.

    Solução para problemas de conexão intermitente com httpx/supabase-py.
    """

    def __init__(
        self,
        url: str = None,
        key: str = None,
        service_role_key: str = None,
        max_retries: int = 5,
        backoff_factor: float = 0.5
    ):
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        self.service_role_key = service_role_key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        # Base URL for REST API
        self.rest_url = f"{self.url}/rest/v1"

        # Configure session with retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Default headers
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        logger.info(f"SupabaseRequestsClient initialized: {self.url}")

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None,
        use_service_role: bool = False,
        max_attempts: int = 3
    ) -> requests.Response:
        """Execute request with retry logic for connection errors."""
        url = f"{self.rest_url}/{endpoint}"
        headers = self.headers.copy()

        if use_service_role and self.service_role_key:
            headers['Authorization'] = f'Bearer {self.service_role_key}'

        last_error = None
        for attempt in range(max_attempts):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=30
                )
                return response
            except requests.exceptions.ConnectionError as e:
                last_error = e
                wait_time = (attempt + 1) * 2
                logger.warning(f"Connection error (attempt {attempt + 1}/{max_attempts}), retrying in {wait_time}s...")
                time.sleep(wait_time)

        raise last_error

    # ============================================
    # AGENT VERSIONS
    # ============================================

    def get_agent_version(self, agent_id: str) -> Optional[Dict]:
        """Busca agent_version por ID"""
        try:
            response = self._request(
                'GET',
                'agent_versions',
                params={'id': f'eq.{agent_id}', 'select': '*'}
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            logger.error(f"Error fetching agent {agent_id}: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {e}")
            return None

    def get_agents_list(self, limit: int = 10) -> List[Dict]:
        """Lista agentes"""
        try:
            response = self._request(
                'GET',
                'agent_versions',
                params={'select': 'id,name,status,last_test_score', 'limit': limit}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return []

    def update_agent_test_results(
        self,
        agent_id: str,
        score: float,
        report_url: str,
        test_result_id: str = None
    ):
        """Atualiza agent_version com resultados do teste"""
        try:
            data = {
                'last_test_score': score,
                'last_test_at': datetime.utcnow().isoformat(),
                'test_report_url': report_url,
                'framework_approved': score >= 8.0,
                'status': 'active' if score >= 8.0 else 'needs_improvement'
            }

            response = self._request(
                'PATCH',
                'agent_versions',
                params={'id': f'eq.{agent_id}'},
                json_data=data,
                use_service_role=True
            )

            if response.status_code in [200, 204]:
                logger.info(f"Updated agent {agent_id}: score={score}")
            else:
                logger.error(f"Error updating agent: {response.status_code} - {response.text}")

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
            data = {
                'agent_version_id': agent_version_id,
                'overall_score': overall_score,
                'test_details': test_details,
                'report_url': report_url,
                'test_duration_ms': test_duration_ms,
                'evaluator_model': evaluator_model
            }

            response = self._request(
                'POST',
                'agenttest_test_results',
                json_data=data,
                use_service_role=True
            )

            if response.status_code in [200, 201]:
                result = response.json()
                test_result_id = result[0]['id'] if result else None
                logger.info(f"Saved test result {test_result_id}")
                return test_result_id
            else:
                logger.error(f"Error saving test result: {response.status_code}")
                raise Exception(f"Failed to save test result: {response.text}")

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
            response = self._request(
                'GET',
                'agenttest_test_results',
                params={
                    'agent_version_id': f'eq.{agent_version_id}',
                    'select': '*',
                    'order': 'created_at.desc',
                    'limit': limit
                }
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error fetching test history: {e}")
            return []

    # ============================================
    # SKILLS
    # ============================================

    def get_skill(self, agent_version_id: str) -> Optional[Dict]:
        """Busca skill de um agente"""
        try:
            response = self._request(
                'GET',
                'agenttest_skills',
                params={
                    'agent_version_id': f'eq.{agent_version_id}',
                    'select': '*',
                    'order': 'version.desc',
                    'limit': 1
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
        except Exception as e:
            logger.error(f"Error fetching skill: {e}")
            return None

    # ============================================
    # HEALTH CHECK
    # ============================================

    def health_check(self) -> bool:
        """Verifica se conexão está funcionando"""
        try:
            response = self._request('GET', '', params={'limit': 1})
            return response.status_code in [200, 404]  # 404 is ok for root
        except Exception:
            return False


# Test function
def test_connection():
    """Testa conexão com Supabase"""
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing SupabaseRequestsClient...")

    try:
        client = SupabaseRequestsClient()

        # Health check
        print("Health check:", "OK" if client.health_check() else "FAILED")

        # List agents
        agents = client.get_agents_list(limit=3)
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent.get('name', 'Unknown')} (score: {agent.get('last_test_score', 'N/A')})")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    test_connection()
