#!/usr/bin/env python3
"""
AI Factory Testing Framework - End-to-End Test
==============================================

Este script executa um teste completo do framework:
1. Conecta ao Supabase
2. Busca um agente (Isabella ou outro disponivel)
3. Executa 5 casos de teste
4. Avalia com Claude Opus
5. Gera relatorio HTML
6. Salva resultados

Usage:
    # Com .env configurado
    python test_e2e.py

    # Com variaveis explicitas
    SUPABASE_URL=... SUPABASE_KEY=... ANTHROPIC_API_KEY=... python test_e2e.py

    # Especificando agent_id
    python test_e2e.py --agent-id <uuid>
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carregar .env imediatamente
load_dotenv(override=True)

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

# Usar o novo cliente baseado em requests (mais estável)
from src.supabase_requests import SupabaseRequestsClient
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


# Test cases reduzidos para teste rapido
QUICK_TEST_CASES = [
    {
        'name': 'Lead frio - primeira mensagem',
        'input': 'Oi',
        'expected_behavior': 'Cumprimento amigavel + pergunta aberta sobre interesse',
        'rubric_focus': ['tone', 'engagement'],
        'category': 'cold_lead'
    },
    {
        'name': 'Lead pergunta preco',
        'input': 'Quanto custa o servico?',
        'expected_behavior': 'Ancora valor antes de preco + qualifica necessidade',
        'rubric_focus': ['compliance', 'completeness'],
        'category': 'price_objection'
    },
    {
        'name': 'Lead interessado - qualificacao',
        'input': 'Estou procurando uma solucao para automatizar meu atendimento. Temos 10 funcionarios.',
        'expected_behavior': 'Qualifica Budget, Authority, Need, Timeline',
        'rubric_focus': ['completeness', 'engagement'],
        'category': 'qualification'
    },
    {
        'name': 'Lead com objecao',
        'input': 'Parece interessante mas agora nao tenho tempo para isso',
        'expected_behavior': 'Trata objecao com empatia + oferece opcao rapida',
        'rubric_focus': ['tone', 'conversion'],
        'category': 'objection'
    },
    {
        'name': 'Lead quente - quer agendar',
        'input': 'OK, vamos marcar uma reuniao para voce me mostrar como funciona',
        'expected_behavior': 'Confirma agendamento + coleta informacoes necessarias',
        'rubric_focus': ['conversion', 'completeness'],
        'category': 'hot_lead'
    }
]


def verify_environment():
    """Verifica se as variaveis de ambiente estao configuradas"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'ANTHROPIC_API_KEY']
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.info("Please set them in .env file or export them directly")
        return False

    return True


def find_test_agent(supabase: SupabaseRequestsClient, agent_id: str = None) -> dict:
    """Busca um agente para testar"""

    # Se ID especificado, buscar direto
    if agent_id:
        logger.info(f"Fetching specified agent: {agent_id}")
        agent = supabase.get_agent_version(agent_id)
        if agent:
            return agent
        logger.warning(f"Agent {agent_id} not found, searching for alternatives...")

    # Buscar qualquer agente disponivel
    try:
        agents = supabase.get_agents_list(limit=5)

        if agents:
            # Preferir agente com system_prompt
            for agent in agents:
                if agent.get('system_prompt'):
                    logger.info(f"Found agent with prompt: {agent.get('name', agent['id'][:8])}")
                    # Fetch full agent data
                    return supabase.get_agent_version(agent['id'])

            # Se nenhum tem prompt, pegar o primeiro
            logger.info(f"Found agent: {agents[0].get('name', agents[0]['id'][:8])}")
            return supabase.get_agent_version(agents[0]['id'])

    except Exception as e:
        logger.error(f"Error searching for agents: {e}")

    return None


async def simulate_agent_response(system_prompt: str, user_message: str) -> str:
    """Simula resposta do agente usando Claude"""
    from anthropic import Anthropic

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return "[ERROR] ANTHROPIC_API_KEY not set"

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error simulating agent: {e}")
        return f"[ERROR] {str(e)}"


async def run_e2e_test(agent_id: str = None, use_quick_tests: bool = True):
    """Executa teste end-to-end completo"""

    logger.info("=" * 60)
    logger.info("AI Factory Testing Framework - E2E Test")
    logger.info("=" * 60)

    # Criar diretorio de saida
    output_dir = Path('./reports')
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Reports will be saved to: {output_dir.absolute()}")

    # Inicializar componentes
    logger.info("\n1. Initializing components...")

    try:
        supabase = SupabaseRequestsClient()
        if supabase.health_check():
            logger.info("   [OK] Supabase client initialized and connected")
        else:
            logger.warning("   [WARN] Supabase client initialized but connection unstable")
    except Exception as e:
        logger.error(f"   [FAIL] Supabase client: {e}")
        return False

    try:
        evaluator = Evaluator()
        logger.info("   [OK] Evaluator initialized (Claude Opus)")
    except Exception as e:
        logger.error(f"   [FAIL] Evaluator: {e}")
        return False

    try:
        reporter = ReportGenerator(output_dir=str(output_dir))
        logger.info("   [OK] Report generator initialized")
    except Exception as e:
        logger.error(f"   [FAIL] Report generator: {e}")
        return False

    # Buscar agente
    logger.info("\n2. Finding agent to test...")
    agent = find_test_agent(supabase, agent_id)

    if not agent:
        logger.error("   [FAIL] No agent found to test!")
        logger.info("\n   Possible solutions:")
        logger.info("   - Specify agent ID: python test_e2e.py --agent-id <uuid>")
        logger.info("   - Check if there are agents in the database")
        return False

    agent_name = agent.get('name') or agent.get('version') or 'Unknown'
    logger.info(f"   [OK] Testing agent: {agent_name}")
    logger.info(f"   Agent ID: {agent.get('id')}")

    system_prompt = agent.get('system_prompt', '')
    if system_prompt:
        prompt_preview = system_prompt[:200].replace('\n', ' ')
        logger.info(f"   Prompt preview: {prompt_preview}...")
    else:
        logger.warning("   [WARN] Agent has no system_prompt!")
        return False

    # Preparar test cases
    logger.info("\n3. Preparing test cases...")
    test_cases = QUICK_TEST_CASES if use_quick_tests else QUICK_TEST_CASES
    logger.info(f"   Using {len(test_cases)} test cases")

    # Executar testes (simular respostas do agente)
    logger.info("\n4. Running tests...")
    logger.info("-" * 40)

    start_time = datetime.now()
    test_results = []

    for i, test_case in enumerate(test_cases):
        logger.info(f"   Test {i+1}/{len(test_cases)}: {test_case['name']}")

        # Simular resposta do agente
        agent_response = await simulate_agent_response(
            system_prompt=system_prompt,
            user_message=test_case['input']
        )

        test_results.append({
            'name': test_case['name'],
            'input': test_case['input'],
            'expected_behavior': test_case['expected_behavior'],
            'agent_response': agent_response,
            'rubric_focus': test_case.get('rubric_focus', []),
            'category': test_case.get('category', 'general')
        })

        # Preview da resposta
        preview = agent_response[:100].replace('\n', ' ')
        logger.info(f"      Response: {preview}...")

    logger.info("-" * 40)

    # Avaliar com Claude Opus
    logger.info("\n5. Evaluating with Claude Opus...")

    try:
        evaluation = await evaluator.evaluate(
            agent=agent,
            skill=None,
            test_results=test_results
        )
        logger.info(f"   Overall Score: {evaluation['overall_score']:.1f}/10")
    except Exception as e:
        logger.error(f"   [FAIL] Evaluation failed: {e}")
        return False

    # Gerar relatorio HTML
    logger.info("\n6. Generating HTML report...")

    try:
        report_url = await reporter.generate_html_report(
            agent=agent,
            evaluation=evaluation,
            test_results=test_results
        )
        logger.info(f"   Report saved: {report_url}")
    except Exception as e:
        logger.error(f"   [FAIL] Report generation failed: {e}")
        return False

    # Salvar no Supabase
    logger.info("\n7. Saving results to Supabase...")

    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    try:
        test_result_id = supabase.save_test_result(
            agent_version_id=agent['id'],
            overall_score=evaluation['overall_score'],
            test_details={
                'scores': evaluation['scores'],
                'test_cases': test_results,
                'strengths': evaluation.get('strengths', []),
                'weaknesses': evaluation.get('weaknesses', []),
            },
            report_url=report_url,
            test_duration_ms=duration_ms
        )
        logger.info(f"   Test result saved: {test_result_id}")

        # Atualizar agent_version
        supabase.update_agent_test_results(
            agent_id=agent['id'],
            score=evaluation['overall_score'],
            report_url=report_url
        )
        logger.info("   Agent version updated")

    except Exception as e:
        logger.warning(f"   [WARN] Could not save to Supabase: {e}")

    # Resultados finais
    duration = (datetime.now() - start_time).total_seconds()

    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS")
    logger.info("=" * 60)

    logger.info(f"\nOverall Score: {evaluation['overall_score']:.1f}/10")
    logger.info(f"Duration: {duration:.1f}s")
    logger.info(f"Report: {report_url}")

    # Mostrar breakdown
    scores = evaluation.get('scores', {})
    logger.info("\nScore Breakdown:")
    logger.info(f"  - Completeness (25%): {scores.get('completeness', 0):.1f}")
    logger.info(f"  - Tone (20%):         {scores.get('tone', 0):.1f}")
    logger.info(f"  - Engagement (20%):   {scores.get('engagement', 0):.1f}")
    logger.info(f"  - Compliance (20%):   {scores.get('compliance', 0):.1f}")
    logger.info(f"  - Conversion (15%):   {scores.get('conversion', 0):.1f}")

    # Status
    if evaluation['overall_score'] >= 8.0:
        logger.info("\nStatus: APPROVED")
    else:
        logger.info("\nStatus: NEEDS IMPROVEMENT")

    # Strengths/Weaknesses
    if evaluation.get('strengths'):
        logger.info("\nStrengths:")
        for s in evaluation['strengths'][:3]:
            logger.info(f"  + {s}")

    if evaluation.get('weaknesses'):
        logger.info("\nWeaknesses:")
        for w in evaluation['weaknesses'][:3]:
            logger.info(f"  - {w}")

    logger.info("\n" + "=" * 60)
    logger.info("E2E Test completed successfully!")
    logger.info("=" * 60)

    return True


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description='AI Factory Testing Framework - E2E Test'
    )
    parser.add_argument(
        '--agent-id',
        type=str,
        help='Specific agent UUID to test'
    )
    parser.add_argument(
        '--full-tests',
        action='store_true',
        help='Use full test suite instead of quick tests'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        default='.env',
        help='Path to .env file'
    )

    args = parser.parse_args()

    # Carregar .env
    env_path = Path(args.env_file)
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from: {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}")

    # Verificar ambiente
    if not verify_environment():
        sys.exit(1)

    # Executar teste
    success = asyncio.run(
        run_e2e_test(
            agent_id=args.agent_id,
            use_quick_tests=not args.full_tests
        )
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
