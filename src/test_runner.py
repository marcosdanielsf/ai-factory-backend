"""
AI Factory Testing Framework - Test Runner
==========================================

Orquestrador principal de testes para agentes IA.
Coordena o fluxo completo de testes: carregamento de dados,
execução de casos de teste, avaliação e geração de relatórios.

Workflow do Test Runner:
    1. Carrega agent_version do Supabase
    2. Carrega skill (se existir)
    3. Carrega test cases (de arquivo, skill ou default)
    4. Executa cada caso de teste (simula conversa com Claude)
    5. Envia resultados para Evaluator (Claude Opus)
    6. Agrega resultados e calcula scores
    7. Gera relatório HTML
    8. Salva tudo no Supabase

Example:
    >>> from src import TestRunner, Evaluator, ReportGenerator, SupabaseClient
    >>>
    >>> runner = TestRunner(
    ...     supabase_client=SupabaseClient(),
    ...     evaluator=Evaluator(),
    ...     report_generator=ReportGenerator()
    ... )
    >>>
    >>> result = await runner.run_tests("agent-uuid-here")
    >>> print(f"Score: {result['overall_score']}")
    >>> print(f"Report: {result['report_url']}")

Environment Variables:
    ANTHROPIC_API_KEY: Para simulação de agentes
    SUPABASE_URL: URL do Supabase
    SUPABASE_KEY: API Key do Supabase
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

from .supabase_client import SupabaseClient
from .evaluator import Evaluator
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)


# Default test cases for SDR agents
# Cobrem cenários comuns de SDR: leads frios, objeções, qualificação, etc.
DEFAULT_SDR_TEST_CASES = [
    {
        'name': 'Lead frio - primeira mensagem',
        'input': 'Oi',
        'expected_behavior': 'Cumprimento amigavel + pergunta aberta sobre interesse',
        'rubric_focus': ['tone', 'engagement'],
        'category': 'cold_lead'
    },
    {
        'name': 'Lead pergunta preco direto',
        'input': 'Quanto custa?',
        'expected_behavior': 'Ancora valor antes de preco + qualifica necessidade',
        'rubric_focus': ['compliance', 'completeness'],
        'category': 'price_objection'
    },
    {
        'name': 'Lead interessado - qualificacao BANT',
        'input': 'Estou procurando uma solucao para automatizar meu atendimento. Temos uma equipe de 5 pessoas.',
        'expected_behavior': 'Qualifica Budget, Authority, Need, Timeline',
        'rubric_focus': ['completeness', 'engagement'],
        'category': 'qualification'
    },
    {
        'name': 'Lead com objecao - nao tenho tempo',
        'input': 'Parece interessante mas agora nao tenho tempo',
        'expected_behavior': 'Trata objecao com empatia + oferece opcao rapida',
        'rubric_focus': ['tone', 'conversion'],
        'category': 'objection'
    },
    {
        'name': 'Lead quente - quer agendar',
        'input': 'Ok, vamos marcar uma call para voce me mostrar como funciona',
        'expected_behavior': 'Confirma agendamento + coleta informacoes necessarias',
        'rubric_focus': ['conversion', 'completeness'],
        'category': 'hot_lead'
    },
    {
        'name': 'Lead testando limites - pergunta off-topic',
        'input': 'Voce sabe me dizer qual o melhor restaurante da cidade?',
        'expected_behavior': 'Redireciona educadamente para o foco da conversa',
        'rubric_focus': ['compliance', 'tone'],
        'category': 'guardrail_test'
    },
    {
        'name': 'Lead com duvida tecnica',
        'input': 'Como funciona a integracao com meu sistema atual?',
        'expected_behavior': 'Responde tecnicamente ou agenda call tecnica',
        'rubric_focus': ['completeness', 'engagement'],
        'category': 'technical'
    },
    {
        'name': 'Lead comparando concorrentes',
        'input': 'Ja uso o sistema X, por que deveria trocar para voces?',
        'expected_behavior': 'Diferenciacao sem falar mal do concorrente',
        'rubric_focus': ['compliance', 'tone'],
        'category': 'competition'
    },
    {
        'name': 'Lead solicita material',
        'input': 'Voce pode me enviar mais informacoes por email?',
        'expected_behavior': 'Coleta email + qualifica antes de enviar',
        'rubric_focus': ['completeness', 'conversion'],
        'category': 'material_request'
    },
    {
        'name': 'Lead nao qualificado',
        'input': 'Sou estudante universitario fazendo um trabalho de faculdade',
        'expected_behavior': 'Identifica que nao e lead qualificado, encerra educadamente',
        'rubric_focus': ['compliance', 'tone'],
        'category': 'disqualification'
    }
]


class TestRunner:
    """
    Executor principal de testes para agentes IA.

    Orquestra todo o fluxo de teste: carregamento de dados,
    simulação de conversas, avaliação LLM-as-Judge e persistência.

    Attributes:
        supabase (SupabaseClient): Cliente para acesso ao banco
        evaluator (Evaluator): Avaliador LLM-as-Judge
        reporter (ReportGenerator): Gerador de relatórios HTML
        config (Dict): Configurações extras
        anthropic_client (Anthropic): Cliente para simulação de agentes

    Workflow:
        1. Carrega agent_version do Supabase
        2. Carrega skill (se existir)
        3. Carrega test cases (arquivo > skill > default)
        4. Executa cada caso de teste (simula conversa)
        5. Envia para Evaluator (Claude Opus)
        6. Agrega resultados e calcula scores
        7. Gera relatório HTML
        8. Salva no Supabase

    Example:
        >>> runner = TestRunner(
        ...     supabase_client=SupabaseClient(),
        ...     evaluator=Evaluator(),
        ...     report_generator=ReportGenerator()
        ... )
        >>> result = await runner.run_tests("uuid")
        >>> print(f"Score: {result['overall_score']}")
    """

    def __init__(
        self,
        supabase_client: SupabaseClient,
        evaluator: Evaluator,
        report_generator: ReportGenerator,
        config: Dict = None,
        anthropic_api_key: str = None
    ):
        """
        Inicializa o TestRunner.

        Args:
            supabase_client: Cliente Supabase configurado.
            evaluator: Evaluator para LLM-as-Judge.
            report_generator: Gerador de relatórios.
            config: Configurações extras (opcional).
            anthropic_api_key: API key para simulação (opcional).
        """
        self.supabase = supabase_client
        self.evaluator = evaluator
        self.reporter = report_generator
        self.config = config or {}

        # Cliente Anthropic para simulacao local
        self.anthropic_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if self.anthropic_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        else:
            self.anthropic_client = None
            logger.warning("No Anthropic API key - agent simulation disabled")

    async def run_tests(
        self,
        agent_version_id: str,
        test_suite_path: str = None,
        test_cases: List[Dict] = None
    ) -> Dict:
        """
        Executa suite completa de testes.

        Args:
            agent_version_id: ID do agente no Supabase
            test_suite_path: Caminho opcional para arquivo de test cases
            test_cases: Lista opcional de test cases (override)

        Returns:
            {
                'overall_score': 8.5,
                'test_details': {...},
                'report_url': 'https://...',
                'duration_ms': 45000
            }
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting test suite for agent {agent_version_id}")

        try:
            # 1. Carregar agente
            agent = self.supabase.get_agent_version(agent_version_id)
            if not agent:
                raise ValueError(f"Agent {agent_version_id} not found")

            logger.info(f"Loaded agent: {agent.get('name', 'Unknown')}")

            # 2. Carregar skill
            skill = self.supabase.get_skill(agent_version_id)
            if skill:
                logger.info(f"Loaded skill v{skill.get('version', 1)}")

            # 3. Carregar test cases
            if test_cases:
                loaded_test_cases = test_cases
            else:
                loaded_test_cases = self._load_test_cases(agent, skill, test_suite_path)

            logger.info(f"Loaded {len(loaded_test_cases)} test cases")

            # 4. Executar testes
            results = []
            for i, test_case in enumerate(loaded_test_cases):
                logger.info(f"Running test {i+1}/{len(loaded_test_cases)}: {test_case.get('name', 'Test')}")
                result = await self._run_single_test(agent, skill, test_case)
                results.append(result)

            # 5. Avaliar com Claude Opus
            logger.info("Evaluating results with Claude Opus...")
            evaluation = await self.evaluator.evaluate(
                agent=agent,
                skill=skill,
                test_results=results
            )

            # 6. Gerar relatorio
            logger.info("Generating HTML report...")
            report_url = await self.reporter.generate_html_report(
                agent=agent,
                evaluation=evaluation,
                test_results=results
            )

            # 7. Calcular duracao
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # 8. Montar resultado final
            final_result = {
                'overall_score': evaluation['overall_score'],
                'test_details': {
                    'scores': evaluation['scores'],
                    'test_cases': results,
                    'failures': evaluation.get('failures', []),
                    'warnings': evaluation.get('warnings', []),
                    'strengths': evaluation.get('strengths', []),
                    'weaknesses': evaluation.get('weaknesses', []),
                    'recommendations': evaluation.get('recommendations', [])
                },
                'report_url': report_url,
                'duration_ms': duration_ms
            }

            # 9. Salvar no Supabase
            try:
                test_result_id = self.supabase.save_test_result(
                    agent_version_id=agent_version_id,
                    overall_score=evaluation['overall_score'],
                    test_details=final_result['test_details'],
                    report_url=report_url,
                    test_duration_ms=duration_ms
                )

                # 10. Atualizar agent_version
                self.supabase.update_agent_test_results(
                    agent_id=agent_version_id,
                    score=evaluation['overall_score'],
                    report_url=report_url,
                    test_result_id=test_result_id
                )
            except Exception as e:
                logger.warning(f"Could not save to Supabase: {e}")

            logger.info(
                f"Test suite completed: agent={agent_version_id}, "
                f"score={evaluation['overall_score']:.2f}, "
                f"duration={duration_ms}ms"
            )

            return final_result

        except Exception as e:
            logger.error(f"Error running tests: {e}", exc_info=True)
            raise

    def _load_test_cases(
        self,
        agent: Dict,
        skill: Optional[Dict],
        test_suite_path: str = None
    ) -> List[Dict]:
        """
        Carrega casos de teste com prioridade definida.

        Ordem de prioridade:
            1. test_suite_path: Arquivo JSON externo
            2. skill.test_cases: Casos definidos na skill
            3. DEFAULT_SDR_TEST_CASES: Casos padrão

        Args:
            agent: Dict com dados do agente.
            skill: Dict com skill do agente (pode ser None).
            test_suite_path: Caminho opcional para arquivo JSON.

        Returns:
            Lista de casos de teste a executar.
        """
        # Opcao 1: Arquivo de test suite
        if test_suite_path and Path(test_suite_path).exists():
            logger.info(f"Loading test cases from: {test_suite_path}")
            with open(test_suite_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif 'test_cases' in data:
                    return data['test_cases']

        # Opcao 2: Test cases do skill
        if skill and skill.get('test_cases'):
            logger.info("Using test cases from skill")
            return skill['test_cases']

        # Opcao 3: Default baseado no tipo de agente
        logger.info("Using default SDR test cases")
        return self._get_default_test_cases(agent)

    def _get_default_test_cases(self, agent: Dict) -> List[Dict]:
        """
        Retorna casos de teste padrão baseados no tipo de agente.

        Pode filtrar casos baseado nos modos identificados no agent_config.

        Args:
            agent: Dict com dados do agente.

        Returns:
            Lista de casos de teste apropriados para o agente.
        """
        # Por enquanto, sempre retorna SDR test cases
        # Futuramente: detectar tipo de agente e retornar casos apropriados

        agent_config = agent.get('agent_config', {})
        if isinstance(agent_config, str):
            try:
                agent_config = json.loads(agent_config)
            except:
                agent_config = {}

        # Verificar modos identificados
        modos = agent_config.get('modos_identificados', [])

        # Filtrar test cases por categoria se houver modos especificos
        if modos:
            relevant_tests = []
            for test in DEFAULT_SDR_TEST_CASES:
                # Sempre incluir alguns testes basicos
                if test['category'] in ['cold_lead', 'qualification', 'hot_lead']:
                    relevant_tests.append(test)
                # Incluir testes de objecao se modo inclui
                elif 'objecao' in str(modos).lower() and test['category'] == 'objection':
                    relevant_tests.append(test)
                # Incluir testes de preco se modo inclui
                elif 'preco' in str(modos).lower() and test['category'] == 'price_objection':
                    relevant_tests.append(test)

            if len(relevant_tests) >= 5:
                return relevant_tests

        # Retornar todos os testes default
        return DEFAULT_SDR_TEST_CASES

    async def _run_single_test(
        self,
        agent: Dict,
        skill: Optional[Dict],
        test_case: Dict
    ) -> Dict:
        """
        Executa um caso de teste individual.

        Simula conversa com o agente usando Claude e retorna
        a resposta para avaliação posterior.

        Args:
            agent: Dict com dados do agente.
            skill: Dict com skill do agente (pode ser None).
            test_case: Dict com caso de teste:
                - name: Nome do teste
                - input: Mensagem do lead
                - expected_behavior: Comportamento esperado
                - rubric_focus: Lista de dimensões a focar

        Returns:
            Dict com resultado do teste incluindo agent_response.
        """
        test_name = test_case.get('name', 'Unnamed Test')
        test_input = test_case.get('input', '')
        expected_behavior = test_case.get('expected_behavior', '')

        # Preparar system prompt do agente
        system_prompt = self._build_agent_prompt(agent, skill)

        # Simular resposta do agente
        try:
            agent_response = await self._simulate_agent_response(
                system_prompt=system_prompt,
                user_message=test_input
            )
        except Exception as e:
            logger.error(f"Error simulating agent for test '{test_name}': {e}")
            agent_response = f"[ERROR] Could not simulate agent: {str(e)}"

        return {
            'name': test_name,
            'input': test_input,
            'expected_behavior': expected_behavior,
            'agent_response': agent_response,
            'rubric_focus': test_case.get('rubric_focus', []),
            'category': test_case.get('category', 'general'),
            # Score e passed serao preenchidos pelo Evaluator
            'score': 0,
            'passed': False,
            'feedback': ''
        }

    def _build_agent_prompt(self, agent: Dict, skill: Optional[Dict]) -> str:
        """
        Constrói o system prompt completo para simular o agente.

        Combina o prompt base do agente com instruções da skill
        se disponível.

        Args:
            agent: Dict com dados do agente (deve conter system_prompt).
            skill: Dict com skill do agente (pode ser None).

        Returns:
            String com prompt completo para simulação.
        """
        # Prompt base do agente
        base_prompt = agent.get('system_prompt', '')

        # Se tiver skill com instructions, usar como complemento
        if skill and skill.get('instructions'):
            skill_instructions = skill['instructions']
            # Combinar prompt base com instructions do skill
            combined_prompt = f"""{base_prompt}

---
INSTRUCOES ADICIONAIS (SKILL):
{skill_instructions}
"""
            return combined_prompt

        return base_prompt

    async def _simulate_agent_response(
        self,
        system_prompt: str,
        user_message: str
    ) -> str:
        """
        Simula resposta do agente usando Claude.

        Usa Claude Sonnet para simular o agente de forma rápida
        e retorna a resposta que seria enviada ao lead.

        Args:
            system_prompt: Prompt completo do agente.
            user_message: Mensagem do lead/usuário.

        Returns:
            String com resposta simulada do agente.
        """
        if not self.anthropic_client:
            return "[MOCK] Simulacao desabilitada - API key nao configurada"

        if not system_prompt:
            return "[ERROR] Agent system prompt is empty"

        try:
            # Usar modelo mais rapido para simulacao
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",  # Modelo rapido para simulacao
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return f"[ERROR] API call failed: {str(e)}"


# Helper function for quick testing
async def run_quick_test(
    agent_version_id: str,
    supabase_url: str = None,
    supabase_key: str = None,
    anthropic_key: str = None,
    output_dir: str = None,
    test_cases: List[Dict] = None
) -> Dict:
    """
    Função helper para rodar teste rápido sem setup manual.

    Cria todos os componentes necessários e executa testes
    em uma única chamada.

    Args:
        agent_version_id: UUID do agente a testar.
        supabase_url: URL do Supabase (opcional, usa env var).
        supabase_key: Key do Supabase (opcional, usa env var).
        anthropic_key: Key Anthropic (opcional, usa env var).
        output_dir: Diretório para relatórios (opcional).
        test_cases: Lista de casos de teste (opcional).

    Returns:
        Dict com resultado completo do teste:
        - overall_score: Score geral (0-10)
        - test_details: Detalhes completos
        - report_url: URL do relatório HTML
        - duration_ms: Duração do teste

    Example:
        >>> result = await run_quick_test(
        ...     agent_version_id="uuid-here",
        ...     test_cases=[
        ...         {"name": "test1", "input": "Oi", "expected_behavior": "..."}
        ...     ]
        ... )
        >>> print(f"Score: {result['overall_score']}")
    """
    # Inicializar componentes
    supabase = SupabaseClient(
        url=supabase_url or os.getenv('SUPABASE_URL'),
        key=supabase_key or os.getenv('SUPABASE_KEY')
    )

    evaluator = Evaluator(
        api_key=anthropic_key or os.getenv('ANTHROPIC_API_KEY')
    )

    reporter = ReportGenerator(
        output_dir=output_dir or os.getenv('REPORTS_OUTPUT_DIR', './reports')
    )

    runner = TestRunner(
        supabase_client=supabase,
        evaluator=evaluator,
        report_generator=reporter
    )

    return await runner.run_tests(
        agent_version_id=agent_version_id,
        test_cases=test_cases
    )
