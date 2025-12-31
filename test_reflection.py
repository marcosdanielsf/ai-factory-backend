#!/usr/bin/env python3
"""
AI Factory Testing Framework - Reflection Loop Test
====================================================

Testa o ciclo completo:
1. Executa teste no agente
2. Se score < 8.0, executa reflection
3. Gera nova versão melhorada
4. (Opcional) Testa a nova versão

Usage:
    python test_reflection.py --agent-id <uuid>
    python test_reflection.py --agent-id <uuid> --auto-test
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carregar .env
load_dotenv(override=True)

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.supabase_requests import SupabaseRequestsClient
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator
from src.reflection_loop import ReflectionLoop

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test cases
TEST_CASES = [
    {
        'name': 'Lead frio - primeira mensagem',
        'input': 'Oi',
        'expected_behavior': 'Cumprimento + pergunta aberta',
        'rubric_focus': ['tone', 'engagement']
    },
    {
        'name': 'Lead pergunta preco',
        'input': 'Quanto custa?',
        'expected_behavior': 'Ancora valor + qualifica BANT',
        'rubric_focus': ['compliance', 'completeness']
    },
    {
        'name': 'Lead interessado',
        'input': 'Preciso de uma solucao para minha clinica, temos 5 medicos.',
        'expected_behavior': 'Qualifica Budget, Authority, Need, Timeline',
        'rubric_focus': ['completeness', 'engagement']
    },
    {
        'name': 'Lead com objecao',
        'input': 'Interessante mas nao tenho tempo agora',
        'expected_behavior': 'Trata objecao + oferece alternativa',
        'rubric_focus': ['tone', 'conversion']
    },
    {
        'name': 'Lead quente',
        'input': 'Vamos marcar uma reuniao',
        'expected_behavior': 'Confirma agendamento + coleta dados',
        'rubric_focus': ['conversion', 'completeness']
    }
]


async def simulate_agent(system_prompt: str, user_message: str, max_retries: int = 3) -> str:
    """Simula resposta do agente com retry"""
    from anthropic import Anthropic
    import time

    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                logger.warning(f"API error, retrying in {wait_time}s... ({e})")
                time.sleep(wait_time)
            else:
                raise


async def run_test_and_reflection(agent_id: str, auto_test: bool = False):
    """Executa teste e reflection se necessário"""

    logger.info("=" * 60)
    logger.info("TEST + REFLECTION LOOP")
    logger.info("=" * 60)

    # Inicializar componentes
    supabase = SupabaseRequestsClient()
    evaluator = Evaluator()
    reporter = ReportGenerator(output_dir='./reports')
    reflection = ReflectionLoop(supabase_client=supabase)

    # 1. Carregar agente
    logger.info(f"\n1. Loading agent: {agent_id}")
    agent = supabase.get_agent_version(agent_id)

    if not agent:
        logger.error("Agent not found!")
        return

    agent_name = agent.get('name') or agent.get('version', 'Unknown')
    logger.info(f"   Agent: {agent_name}")

    system_prompt = agent.get('system_prompt', '')
    if not system_prompt:
        logger.error("Agent has no system_prompt!")
        return

    # 2. Executar testes
    logger.info(f"\n2. Running {len(TEST_CASES)} tests...")

    test_results = []
    for i, test_case in enumerate(TEST_CASES):
        logger.info(f"   Test {i+1}: {test_case['name']}")

        response = await simulate_agent(system_prompt, test_case['input'])
        test_results.append({
            'name': test_case['name'],
            'input': test_case['input'],
            'expected_behavior': test_case['expected_behavior'],
            'agent_response': response,
            'rubric_focus': test_case.get('rubric_focus', [])
        })

    # 3. Avaliar
    logger.info("\n3. Evaluating with Claude Opus...")

    evaluation = await evaluator.evaluate(
        agent=agent,
        skill=None,
        test_results=test_results
    )

    overall_score = evaluation['overall_score']
    logger.info(f"   Overall Score: {overall_score}/10")

    # 4. Gerar relatório
    logger.info("\n4. Generating report...")

    report_url = await reporter.generate_html_report(
        agent=agent,
        evaluation=evaluation,
        test_results=test_results
    )
    logger.info(f"   Report: {report_url}")

    # Montar test_result completo
    full_test_result = {
        'overall_score': overall_score,
        'test_details': {
            'scores': evaluation['scores'],
            'strengths': evaluation.get('strengths', []),
            'weaknesses': evaluation.get('weaknesses', []),
            'failures': evaluation.get('failures', []),
            'recommendations': evaluation.get('recommendations', [])
        },
        'report_url': report_url
    }

    # 5. Verificar se precisa reflection
    logger.info("\n5. Checking if reflection needed...")

    if overall_score >= 8.0:
        logger.info(f"   Score {overall_score} >= 8.0 - APPROVED! No reflection needed.")
        return {
            'status': 'approved',
            'score': overall_score,
            'report_url': report_url
        }

    if overall_score < 6.0:
        logger.info(f"   Score {overall_score} < 6.0 - Too low for auto-reflection. Manual review needed.")
        return {
            'status': 'needs_manual_review',
            'score': overall_score,
            'report_url': report_url
        }

    # 6. Executar reflection
    logger.info(f"\n6. Score {overall_score} in range [6.0, 8.0) - Starting REFLECTION...")

    reflection_result = await reflection.run_reflection(
        agent=agent,
        test_result=full_test_result,
        auto_test=auto_test
    )

    # 7. Mostrar resultados
    logger.info("\n" + "=" * 60)
    logger.info("FINAL RESULTS")
    logger.info("=" * 60)

    logger.info(f"\nOriginal Score: {overall_score}/10")

    if reflection_result.get('status') == 'success':
        logger.info(f"New Version Created: {reflection_result.get('new_version')}")
        logger.info(f"New Version ID: {reflection_result.get('new_agent_id')}")
        logger.info(f"Status: {reflection_result.get('new_agent_status')}")

        if reflection_result.get('changes_summary'):
            logger.info("\nChanges Made:")
            for change in reflection_result['changes_summary'][:5]:
                logger.info(f"  - {change}")

        if reflection_result.get('expected_improvements'):
            logger.info("\nExpected Improvements:")
            for dim, imp in reflection_result['expected_improvements'].items():
                logger.info(f"  - {dim}: {imp}")

        if reflection_result.get('new_score'):
            logger.info(f"\nNew Version Score: {reflection_result['new_score']}/10")
            logger.info(f"Improvement: {reflection_result.get('improvement', 0):+.1f}")

    else:
        logger.warning(f"Reflection failed: {reflection_result.get('reason')}")

    logger.info("\n" + "=" * 60)
    logger.info("Next Steps:")
    logger.info("  1. Review the new version in the Dashboard")
    logger.info("  2. Test in Sandbox mode")
    logger.info("  3. Approve or reject the changes")
    logger.info("=" * 60)

    return reflection_result


def main():
    parser = argparse.ArgumentParser(description='Test + Reflection Loop')
    parser.add_argument('--agent-id', type=str, required=True, help='Agent UUID')
    parser.add_argument('--auto-test', action='store_true', help='Auto-test new version')

    args = parser.parse_args()

    result = asyncio.run(run_test_and_reflection(
        agent_id=args.agent_id,
        auto_test=args.auto_test
    ))

    print(f"\nFinal result: {result}")


if __name__ == '__main__':
    main()
