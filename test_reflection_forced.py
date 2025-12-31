#!/usr/bin/env python3
"""
AI Factory Testing Framework - Forced Reflection Test
======================================================

Testa o reflection loop forçando um cenário de melhoria.
Simula um test_result com score baixo para testar a geração
de nova versão melhorada.

Usage:
    python test_reflection_forced.py --agent-id <uuid>
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
from src.reflection_loop import ReflectionLoop

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test result simulado com problemas específicos
MOCK_TEST_RESULT = {
    'overall_score': 6.5,  # Score que dispara reflection
    'test_details': {
        'scores': {
            'completeness': 6.0,
            'tone': 7.5,
            'engagement': 6.5,
            'compliance': 5.5,
            'conversion': 6.0
        },
        'strengths': [
            'Tom amigável e acolhedor',
            'Boa abertura de conversa'
        ],
        'weaknesses': [
            'Não qualifica BANT completo - pula Budget frequentemente',
            'Respostas muito longas, perdem engajamento',
            'Não ancora valor antes de falar preço',
            'Falta urgência no fechamento'
        ],
        'failures': [
            {
                'test_name': 'Lead pergunta preço',
                'expected': 'Ancora valor antes de preço',
                'actual': 'Respondeu preço direto sem qualificar',
                'severity': 'high'
            },
            {
                'test_name': 'Lead quente',
                'expected': 'Coleta dados para agendamento',
                'actual': 'Não pediu telefone/email para confirmar',
                'severity': 'medium'
            }
        ],
        'recommendations': [
            'Adicionar regra explícita para NUNCA dar preço sem qualificar',
            'Limitar respostas a 3-4 frases máximo',
            'Incluir script de fechamento com coleta de dados'
        ]
    },
    'report_url': './reports/mock_report.html'
}


async def run_forced_reflection(agent_id: str):
    """Executa reflection forçado para testar o loop"""

    logger.info("=" * 60)
    logger.info("FORCED REFLECTION TEST")
    logger.info("=" * 60)

    # Inicializar componentes
    supabase = SupabaseRequestsClient()
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

    logger.info(f"   Prompt length: {len(system_prompt)} chars")

    # 2. Mostrar test result simulado
    logger.info(f"\n2. Using MOCK test result:")
    logger.info(f"   Overall Score: {MOCK_TEST_RESULT['overall_score']}/10")
    logger.info(f"   Weaknesses: {len(MOCK_TEST_RESULT['test_details']['weaknesses'])}")
    logger.info(f"   Failures: {len(MOCK_TEST_RESULT['test_details']['failures'])}")

    # 3. Verificar se reflection seria disparado
    logger.info("\n3. Checking reflection conditions...")

    should_reflect = await reflection.should_reflect(MOCK_TEST_RESULT)
    logger.info(f"   Should reflect: {should_reflect}")

    if not should_reflect:
        logger.info("   Reflection not needed based on score.")
        return

    # 4. Executar reflection
    logger.info("\n4. Running REFLECTION LOOP...")

    reflection_result = await reflection.run_reflection(
        agent=agent,
        test_result=MOCK_TEST_RESULT,
        auto_test=False  # Não testar automaticamente
    )

    # 5. Mostrar resultados
    logger.info("\n" + "=" * 60)
    logger.info("REFLECTION RESULTS")
    logger.info("=" * 60)

    if reflection_result.get('status') == 'success':
        logger.info(f"\n✅ SUCCESS!")
        logger.info(f"   New Version: {reflection_result.get('new_version')}")
        logger.info(f"   New Agent ID: {reflection_result.get('new_agent_id')}")
        logger.info(f"   Status: {reflection_result.get('new_agent_status')}")

        if reflection_result.get('changes_summary'):
            logger.info("\n📝 Changes Made:")
            for i, change in enumerate(reflection_result['changes_summary'][:10], 1):
                logger.info(f"   {i}. {change}")

        if reflection_result.get('expected_improvements'):
            logger.info("\n📈 Expected Improvements:")
            for dim, improvement in reflection_result['expected_improvements'].items():
                logger.info(f"   - {dim}: {improvement}")

        logger.info("\n" + "-" * 40)
        logger.info("📋 NEXT STEPS:")
        logger.info("   1. Go to Dashboard → Agents")
        logger.info("   2. Find the new version (status: pending_approval)")
        logger.info("   3. Review the changes")
        logger.info("   4. Approve or Reject")
        logger.info("-" * 40)

    else:
        logger.error(f"\n❌ FAILED: {reflection_result.get('reason')}")

    return reflection_result


def main():
    parser = argparse.ArgumentParser(description='Forced Reflection Test')
    parser.add_argument('--agent-id', type=str, required=True, help='Agent UUID')

    args = parser.parse_args()

    result = asyncio.run(run_forced_reflection(agent_id=args.agent_id))

    print(f"\nFinal result: {result}")


if __name__ == '__main__':
    main()
