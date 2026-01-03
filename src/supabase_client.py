"""
AI Factory Testing Framework - Supabase Client
==============================================
Cliente Supabase com retry logic, logging estruturado e error handling robusto.
"""

import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from datetime import datetime, timezone

from src.core.logging_config import get_logger, LogContext, Timer
from src.core.retry import with_retry, SUPABASE_RETRY_CONFIG
from src.core.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    NotFoundError,
)

logger = get_logger(__name__)


class SupabaseClient:
    """
    Cliente Supabase com retry logic e logging estruturado.

    Features:
    - Retry automático em operações de banco
    - Logging estruturado com contexto
    - Exception handling específico
    - Métricas de performance
    """

    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')

        if not self.url or not self.key:
            raise DatabaseConnectionError(
                message="SUPABASE_URL and SUPABASE_KEY must be set",
                details={"url_set": bool(self.url), "key_set": bool(self.key)},
            )

        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info(
                "Supabase client initialized",
                extra_fields={"url": self._mask_url(self.url)},
            )
        except Exception as e:
            raise DatabaseConnectionError(
                message="Failed to create Supabase client",
                original_error=e,
            )

    def _mask_url(self, url: str) -> str:
        """Mask sensitive parts of URL for logging."""
        if not url:
            return ""
        # Show only domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/..."

    def _handle_response(
        self,
        response,
        operation: str,
        resource: str = "Resource",
        resource_id: str = None,
    ) -> Any:
        """
        Handle Supabase response with proper error checking.

        Args:
            response: Supabase response object
            operation: Name of the operation for logging
            resource: Resource type for error messages
            resource_id: Resource ID for not found errors
        """
        if not response.data:
            if resource_id:
                raise NotFoundError(
                    resource=resource,
                    resource_id=resource_id,
                )
            return None
        return response.data

    # ============================================
    # AGENT VERSIONS
    # ============================================

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def get_agent_version(self, agent_id: str) -> Optional[Dict]:
        """Busca agent_version por ID com retry."""
        with LogContext(operation="get_agent_version", agent_id=agent_id):
            with Timer() as timer:
                try:
                    response = self.client.table('agent_versions')\
                        .select('*, clients(*), sub_accounts(*)')\
                        .eq('id', agent_id)\
                        .single()\
                        .execute()

                    logger.info(
                        "Agent version fetched",
                        extra_fields={
                            "agent_id": agent_id,
                            "duration_ms": timer.duration_ms,
                            "found": bool(response.data),
                        },
                    )
                    return response.data

                except Exception as e:
                    # Check if it's a "not found" error
                    error_msg = str(e).lower()
                    if "no rows" in error_msg or "0 rows" in error_msg:
                        logger.warning(
                            "Agent version not found",
                            extra_fields={"agent_id": agent_id},
                        )
                        return None

                    logger.error(
                        "Failed to fetch agent version",
                        extra_fields={
                            "agent_id": agent_id,
                            "error": str(e),
                        },
                    )
                    raise DatabaseQueryError(
                        message=f"Failed to fetch agent {agent_id}",
                        details={"agent_id": agent_id},
                        original_error=e,
                    )

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def get_agents_needing_testing(self, limit: int = 100) -> List[Dict]:
        """Busca agentes que precisam ser testados com retry."""
        with LogContext(operation="get_agents_needing_testing"):
            with Timer() as timer:
                try:
                    response = self.client.table('vw_agents_needing_testing')\
                        .select('*')\
                        .limit(limit)\
                        .execute()

                    count = len(response.data) if response.data else 0
                    logger.info(
                        "Fetched agents needing testing",
                        extra_fields={
                            "count": count,
                            "limit": limit,
                            "duration_ms": timer.duration_ms,
                        },
                    )
                    return response.data or []

                except Exception as e:
                    logger.error(
                        "Failed to fetch agents needing testing",
                        extra_fields={"error": str(e)},
                    )
                    raise DatabaseQueryError(
                        message="Failed to fetch agents needing testing",
                        original_error=e,
                    )

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def update_agent_test_results(
        self,
        agent_id: str,
        score: float,
        report_url: str,
        test_result_id: str,
    ) -> None:
        """Atualiza agent_version com resultados do teste."""
        with LogContext(
            operation="update_agent_test_results",
            agent_id=agent_id,
            score=score,
        ):
            with Timer() as timer:
                try:
                    approved = score >= 8.0
                    status = 'active' if approved else 'needs_improvement'

                    self.client.table('agent_versions').update({
                        'last_test_score': score,
                        'last_test_at': datetime.now(timezone.utc).isoformat(),
                        'test_report_url': report_url,
                        'framework_approved': approved,
                        'status': status,
                    }).eq('id', agent_id).execute()

                    logger.info(
                        "Agent test results updated",
                        extra_fields={
                            "agent_id": agent_id,
                            "score": score,
                            "approved": approved,
                            "status": status,
                            "test_result_id": test_result_id,
                            "duration_ms": timer.duration_ms,
                        },
                    )

                except Exception as e:
                    logger.error(
                        "Failed to update agent test results",
                        extra_fields={
                            "agent_id": agent_id,
                            "score": score,
                            "error": str(e),
                        },
                    )
                    raise DatabaseQueryError(
                        message=f"Failed to update agent {agent_id} test results",
                        details={"agent_id": agent_id, "score": score},
                        original_error=e,
                    )

    # ============================================
    # TEST RESULTS
    # ============================================

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def save_test_result(
        self,
        agent_version_id: str,
        overall_score: float,
        test_details: Dict,
        report_url: str,
        test_duration_ms: int,
        evaluator_model: str = 'claude-opus-4',
    ) -> str:
        """Salva resultado de teste com retry."""
        with LogContext(
            operation="save_test_result",
            agent_version_id=agent_version_id,
            score=overall_score,
        ):
            with Timer() as timer:
                try:
                    response = self.client.table('agenttest_test_results').insert({
                        'agent_version_id': agent_version_id,
                        'overall_score': overall_score,
                        'test_details': test_details,
                        'report_url': report_url,
                        'test_duration_ms': test_duration_ms,
                        'evaluator_model': evaluator_model,
                    }).execute()

                    if not response.data:
                        raise DatabaseQueryError(
                            message="Insert returned no data",
                            details={"agent_version_id": agent_version_id},
                        )

                    test_result_id = response.data[0]['id']

                    logger.info(
                        "Test result saved",
                        extra_fields={
                            "test_result_id": test_result_id,
                            "agent_version_id": agent_version_id,
                            "score": overall_score,
                            "evaluator_model": evaluator_model,
                            "duration_ms": timer.duration_ms,
                        },
                    )
                    return test_result_id

                except DatabaseError:
                    raise
                except Exception as e:
                    logger.error(
                        "Failed to save test result",
                        extra_fields={
                            "agent_version_id": agent_version_id,
                            "error": str(e),
                        },
                    )
                    raise DatabaseQueryError(
                        message="Failed to save test result",
                        details={"agent_version_id": agent_version_id},
                        original_error=e,
                    )

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def get_test_results_history(
        self,
        agent_version_id: str,
        limit: int = 20,
    ) -> List[Dict]:
        """Busca histórico de testes de um agente com retry."""
        with LogContext(
            operation="get_test_results_history",
            agent_version_id=agent_version_id,
        ):
            try:
                response = self.client.table('agenttest_test_results')\
                    .select('*')\
                    .eq('agent_version_id', agent_version_id)\
                    .order('created_at', desc=True)\
                    .limit(limit)\
                    .execute()

                count = len(response.data) if response.data else 0
                logger.info(
                    "Test results history fetched",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "count": count,
                        "limit": limit,
                    },
                )
                return response.data or []

            except Exception as e:
                logger.error(
                    "Failed to fetch test results history",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "error": str(e),
                    },
                )
                raise DatabaseQueryError(
                    message="Failed to fetch test results history",
                    details={"agent_version_id": agent_version_id},
                    original_error=e,
                )

    # ============================================
    # SKILLS
    # ============================================

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def get_skill(self, agent_version_id: str) -> Optional[Dict]:
        """Busca skill de um agente (versão mais recente) com retry."""
        with LogContext(operation="get_skill", agent_version_id=agent_version_id):
            try:
                response = self.client.table('agenttest_skills')\
                    .select('*')\
                    .eq('agent_version_id', agent_version_id)\
                    .order('version', desc=True)\
                    .limit(1)\
                    .execute()

                if response.data:
                    skill = response.data[0]
                    logger.info(
                        "Skill fetched",
                        extra_fields={
                            "agent_version_id": agent_version_id,
                            "skill_id": skill.get('id'),
                            "version": skill.get('version'),
                        },
                    )
                    return skill

                logger.info(
                    "No skill found",
                    extra_fields={"agent_version_id": agent_version_id},
                )
                return None

            except Exception as e:
                logger.error(
                    "Failed to fetch skill",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "error": str(e),
                    },
                )
                raise DatabaseQueryError(
                    message="Failed to fetch skill",
                    details={"agent_version_id": agent_version_id},
                    original_error=e,
                )

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def save_skill(
        self,
        agent_version_id: str,
        instructions: str,
        examples: str = None,
        rubric: str = None,
        test_cases: List[Dict] = None,
        local_file_path: str = None,
    ) -> str:
        """Salva ou atualiza skill com retry."""
        with LogContext(operation="save_skill", agent_version_id=agent_version_id):
            with Timer() as timer:
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
                        'last_synced_at': datetime.now(timezone.utc).isoformat(),
                    }).execute()

                    if not response.data:
                        raise DatabaseQueryError(
                            message="Insert returned no data",
                            details={"agent_version_id": agent_version_id},
                        )

                    skill_id = response.data[0]['id']

                    logger.info(
                        "Skill saved",
                        extra_fields={
                            "skill_id": skill_id,
                            "agent_version_id": agent_version_id,
                            "version": new_version,
                            "duration_ms": timer.duration_ms,
                        },
                    )
                    return skill_id

                except DatabaseError:
                    raise
                except Exception as e:
                    logger.error(
                        "Failed to save skill",
                        extra_fields={
                            "agent_version_id": agent_version_id,
                            "error": str(e),
                        },
                    )
                    raise DatabaseQueryError(
                        message="Failed to save skill",
                        details={"agent_version_id": agent_version_id},
                        original_error=e,
                    )

    # ============================================
    # CONVERSATIONS (para gerar exemplos)
    # ============================================

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def get_recent_conversations(
        self,
        agent_version_id: str,
        limit: int = 50,
        min_score: float = 8.0,
    ) -> List[Dict]:
        """Busca conversas recentes de alta qualidade com retry."""
        with LogContext(
            operation="get_recent_conversations",
            agent_version_id=agent_version_id,
        ):
            try:
                response = self.client.table('agent_conversations')\
                    .select('*, agent_conversation_messages(*)')\
                    .eq('agent_version_id', agent_version_id)\
                    .gte('sentiment_score', min_score)\
                    .order('started_at', desc=True)\
                    .limit(limit)\
                    .execute()

                count = len(response.data) if response.data else 0
                logger.info(
                    "Recent conversations fetched",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "count": count,
                        "min_score": min_score,
                        "limit": limit,
                    },
                )
                return response.data or []

            except Exception as e:
                logger.error(
                    "Failed to fetch conversations",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "error": str(e),
                    },
                )
                raise DatabaseQueryError(
                    message="Failed to fetch conversations",
                    details={"agent_version_id": agent_version_id},
                    original_error=e,
                )

    # ============================================
    # METRICS (para KNOWLEDGE.md)
    # ============================================

    @with_retry(config=SUPABASE_RETRY_CONFIG)
    def get_agent_metrics(
        self,
        agent_version_id: str,
        days: int = 30,
    ) -> List[Dict]:
        """Busca métricas diárias do agente com retry."""
        with LogContext(
            operation="get_agent_metrics",
            agent_version_id=agent_version_id,
        ):
            try:
                response = self.client.table('agent_metrics')\
                    .select('*')\
                    .eq('agent_version_id', agent_version_id)\
                    .gte('data', f'now() - interval \'{days} days\'')\
                    .order('data', desc=False)\
                    .execute()

                count = len(response.data) if response.data else 0
                logger.info(
                    "Agent metrics fetched",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "count": count,
                        "days": days,
                    },
                )
                return response.data or []

            except Exception as e:
                logger.error(
                    "Failed to fetch metrics",
                    extra_fields={
                        "agent_version_id": agent_version_id,
                        "error": str(e),
                    },
                )
                raise DatabaseQueryError(
                    message="Failed to fetch agent metrics",
                    details={"agent_version_id": agent_version_id, "days": days},
                    original_error=e,
                )

    # ============================================
    # HEALTH CHECK
    # ============================================

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Supabase connection.

        Returns:
            Dict with status, latency, and any errors
        """
        with Timer() as timer:
            try:
                # Simple query to check connectivity
                self.client.table('agent_versions').select('id').limit(1).execute()

                return {
                    "status": "healthy",
                    "latency_ms": timer.duration_ms,
                    "connected": True,
                }
            except Exception as e:
                logger.error(
                    "Supabase health check failed",
                    extra_fields={"error": str(e)},
                )
                return {
                    "status": "unhealthy",
                    "latency_ms": timer.duration_ms,
                    "connected": False,
                    "error": str(e),
                }
