"""
AI Factory Testing Framework - Supabase Client
==============================================

Cliente Supabase otimizado para o AI Factory Testing Framework.
Fornece métodos helpers para gerenciar agentes, resultados de testes,
skills e métricas no banco de dados Supabase.

Example:
    >>> from src import SupabaseClient
    >>> client = SupabaseClient()
    >>> agent = client.get_agent_version("uuid-do-agente")
    >>> print(agent['name'])

Environment Variables:
    SUPABASE_URL: URL do projeto Supabase (ex: https://xxx.supabase.co)
    SUPABASE_KEY: API Key do Supabase (anon ou service_role)

Tables Used:
    - agent_versions: Versões de agentes IA
    - agenttest_test_results: Resultados de testes
    - agenttest_skills: Skills dos agentes (instructions, rubric, examples)
    - agent_conversations: Conversas para geração de exemplos
    - agent_metrics: Métricas diárias dos agentes
    - vw_agents_needing_testing: View de agentes pendentes de teste
"""

import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Cliente Supabase com métodos específicos para o AI Factory Testing Framework.

    Gerencia todas as operações de banco de dados necessárias para:
    - Buscar e atualizar agentes (agent_versions)
    - Salvar e consultar resultados de testes
    - Gerenciar skills dos agentes
    - Buscar conversas e métricas para análise

    Attributes:
        url (str): URL do projeto Supabase
        key (str): API Key do Supabase
        client (Client): Instância do cliente Supabase

    Example:
        >>> client = SupabaseClient()
        >>> # Buscar agente
        >>> agent = client.get_agent_version("uuid-here")
        >>> # Salvar resultado de teste
        >>> test_id = client.save_test_result(
        ...     agent_version_id="uuid",
        ...     overall_score=8.5,
        ...     test_details={"scores": {...}},
        ...     report_url="https://...",
        ...     test_duration_ms=45000
        ... )
    """

    def __init__(self, url: str = None, key: str = None):
        """
        Inicializa o cliente Supabase.

        Args:
            url: URL do projeto Supabase. Se não fornecido, usa SUPABASE_URL.
            key: API Key do Supabase. Se não fornecido, usa SUPABASE_KEY.

        Raises:
            ValueError: Se URL ou Key não estiverem configurados.

        Example:
            >>> # Usando variáveis de ambiente
            >>> client = SupabaseClient()
            >>>
            >>> # Ou passando explicitamente
            >>> client = SupabaseClient(
            ...     url="https://xxx.supabase.co",
            ...     key="eyJhb..."
            ... )
        """
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
        """
        Busca uma versão de agente pelo ID.

        Retorna dados completos do agente incluindo relacionamentos
        com clients e sub_accounts.

        Args:
            agent_id: UUID do agent_version no Supabase.

        Returns:
            Dict com dados do agente ou None se não encontrado.
            Estrutura típica:
            {
                "id": "uuid",
                "name": "Isabella SDR",
                "system_prompt": "...",
                "agent_config": {...},
                "last_test_score": 8.5,
                "clients": {...},
                "sub_accounts": {...}
            }

        Example:
            >>> agent = client.get_agent_version("abc-123-def")
            >>> if agent:
            ...     print(f"Agente: {agent['name']}")
            ...     print(f"Score: {agent['last_test_score']}")
        """
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
        """
        Busca agentes que precisam ser testados.

        Consulta a view vw_agents_needing_testing que retorna agentes
        sem teste recente ou com score abaixo do threshold.

        Args:
            limit: Número máximo de agentes a retornar (default: 100).

        Returns:
            Lista de dicts com agentes pendentes de teste.

        Example:
            >>> pending = client.get_agents_needing_testing(limit=10)
            >>> for agent in pending:
            ...     print(f"{agent['name']} - último teste: {agent['last_test_at']}")
        """
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
    ) -> None:
        """
        Atualiza agent_version com resultados do teste.

        Atualiza campos de teste no agente e define status baseado no score.
        Score >= 8.0 marca o agente como 'active' e framework_approved=True.

        Args:
            agent_id: UUID do agent_version.
            score: Score geral do teste (0-10).
            report_url: URL do relatório HTML gerado.
            test_result_id: ID do registro em agenttest_test_results.

        Raises:
            Exception: Se falhar ao atualizar o banco.

        Example:
            >>> client.update_agent_test_results(
            ...     agent_id="uuid",
            ...     score=8.5,
            ...     report_url="https://reports.example.com/report_123.html",
            ...     test_result_id="test-uuid"
            ... )
        """
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
        """
        Salva resultado de teste na tabela agenttest_test_results.

        Args:
            agent_version_id: UUID do agente testado.
            overall_score: Score geral (0-10).
            test_details: Dict com detalhes completos do teste:
                - scores: {completeness, tone, engagement, compliance, conversion}
                - test_cases: Lista de casos de teste executados
                - strengths: Pontos fortes identificados
                - weaknesses: Pontos fracos identificados
                - failures: Falhas críticas
                - recommendations: Recomendações de melhoria
            report_url: URL do relatório HTML.
            test_duration_ms: Duração do teste em milissegundos.
            evaluator_model: Modelo usado para avaliação (default: claude-opus-4).

        Returns:
            UUID do test_result criado.

        Raises:
            Exception: Se falhar ao salvar no banco.

        Example:
            >>> test_id = client.save_test_result(
            ...     agent_version_id="uuid",
            ...     overall_score=8.5,
            ...     test_details={
            ...         "scores": {"completeness": 9.0, "tone": 8.0},
            ...         "strengths": ["Boa qualificação BANT"],
            ...         "weaknesses": ["Tom às vezes agressivo"]
            ...     },
            ...     report_url="https://...",
            ...     test_duration_ms=45000
            ... )
        """
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
        """
        Busca histórico de testes de um agente.

        Retorna testes ordenados do mais recente para o mais antigo.

        Args:
            agent_version_id: UUID do agente.
            limit: Número máximo de resultados (default: 20).

        Returns:
            Lista de dicts com histórico de testes.

        Example:
            >>> history = client.get_test_results_history("uuid", limit=5)
            >>> for test in history:
            ...     print(f"Score: {test['overall_score']} em {test['created_at']}")
        """
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
        """
        Busca skill mais recente de um agente.

        Skills contêm instruções, exemplos, rubrica e casos de teste
        que definem como o agente deve se comportar.

        Args:
            agent_version_id: UUID do agente.

        Returns:
            Dict com a skill mais recente ou None se não existir.
            Estrutura:
            {
                "id": "uuid",
                "version": 3,
                "instructions": "Você é um SDR...",
                "examples": "Exemplo 1: ...",
                "rubric": "## Critérios...",
                "test_cases": [{...}],
                "local_file_path": "/path/to/skill"
            }

        Example:
            >>> skill = client.get_skill("uuid")
            >>> if skill:
            ...     print(f"Skill v{skill['version']}")
            ...     print(skill['instructions'][:100])
        """
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
        """
        Salva ou cria nova versão de skill para um agente.

        Sempre cria uma nova versão (não atualiza a existente),
        permitindo histórico completo de mudanças.

        Args:
            agent_version_id: UUID do agente.
            instructions: Instruções do sistema (system prompt).
            examples: Exemplos few-shot (opcional).
            rubric: Critérios de avaliação customizados (opcional).
            test_cases: Lista de casos de teste (opcional).
            local_file_path: Caminho local para sync com Obsidian (opcional).

        Returns:
            UUID da skill criada.

        Raises:
            Exception: Se falhar ao salvar.

        Example:
            >>> skill_id = client.save_skill(
            ...     agent_version_id="uuid",
            ...     instructions="Você é um SDR especializado...",
            ...     examples="Exemplo: Lead pergunta preço...",
            ...     test_cases=[{"name": "Test1", "input": "Oi"}]
            ... )
        """
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
        """
        Busca conversas recentes de alta qualidade para geração de exemplos.

        Filtra por sentiment_score para pegar apenas conversas bem-sucedidas
        que podem servir como exemplos few-shot.

        Args:
            agent_version_id: UUID do agente.
            limit: Número máximo de conversas (default: 50).
            min_score: Score mínimo de sentimento (default: 8.0).

        Returns:
            Lista de conversas com suas mensagens incluídas.
            Cada conversa contém agent_conversation_messages.

        Example:
            >>> convs = client.get_recent_conversations("uuid", min_score=9.0)
            >>> for conv in convs:
            ...     messages = conv['agent_conversation_messages']
            ...     print(f"Conversa com {len(messages)} mensagens")
        """
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
        """
        Busca métricas diárias do agente para análise de performance.

        Usado para gerar KNOWLEDGE.md com dados reais de performance.

        Args:
            agent_version_id: UUID do agente.
            days: Número de dias a buscar (default: 30).

        Returns:
            Lista de métricas diárias ordenadas por data.

        Example:
            >>> metrics = client.get_agent_metrics("uuid", days=7)
            >>> for m in metrics:
            ...     print(f"{m['data']}: {m['conversas_total']} conversas")
        """
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

    # ============================================
    # UTILITY METHODS
    # ============================================

    def ping(self) -> bool:
        """
        Testa conexão com o Supabase.

        Returns:
            True se conexão está funcionando.

        Raises:
            Exception: Se conexão falhar.

        Example:
            >>> if client.ping():
            ...     print("Conectado!")
        """
        try:
            self.client.table('agent_versions').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            raise

    def get_batch_status(self, run_id: str) -> Dict:
        """
        Busca status de um batch de testes.

        Args:
            run_id: ID do batch (formato: batch_timestamp).

        Returns:
            Dict com status e resultados do batch.
        """
        # TODO: Implementar quando tabela de batch jobs existir
        return {"run_id": run_id, "status": "unknown"}

    def save_batch_job(
        self,
        run_id: str,
        agent_id: str,
        test_count: int,
        status: str
    ) -> None:
        """
        Salva informações de um batch job.

        Args:
            run_id: ID único do batch.
            agent_id: UUID do agente sendo testado.
            test_count: Número de testes no batch.
            status: Status inicial (processing, completed, failed).
        """
        # TODO: Implementar quando tabela de batch jobs existir
        logger.info(f"Batch job {run_id}: {test_count} tests for {agent_id}")

    def save_batch_results(
        self,
        run_id: str,
        results: List[Dict],
        status: str,
        error: str = None
    ) -> None:
        """
        Salva resultados de um batch de testes.

        Args:
            run_id: ID do batch.
            results: Lista de resultados dos testes.
            status: Status final (completed, failed).
            error: Mensagem de erro se status=failed.
        """
        # TODO: Implementar quando tabela de batch jobs existir
        logger.info(f"Batch {run_id} {status}: {len(results)} results")

    def get_agent_results(
        self,
        agent_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """
        Busca resultados de testes de um agente com paginação.

        Args:
            agent_id: UUID do agente.
            limit: Resultados por página.
            offset: Número de resultados a pular.

        Returns:
            Lista paginada de resultados.
        """
        return self.get_test_results_history(agent_id, limit=limit)

    def get_metrics(self) -> Dict:
        """
        Busca métricas gerais do sistema.

        Returns:
            Dict com métricas agregadas.
        """
        # TODO: Implementar métricas reais
        return {
            "total_agents": 0,
            "total_tests": 0,
            "avg_score": 0.0
        }
