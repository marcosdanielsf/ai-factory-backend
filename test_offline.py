#!/usr/bin/env python3
"""
AI Factory Testing Framework - Offline Test
============================================

Testa o framework sem necessidade de conexao com Supabase.
Usa um agente mock para validar o pipeline completo.

Usage:
    ANTHROPIC_API_KEY=sk-ant-xxx python test_offline.py
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluator import Evaluator
from src.report_generator import ReportGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mock agent data
MOCK_AGENT = {
    'id': 'mock-agent-001',
    'name': 'Isabella SDR (Mock)',
    'version': 1,
    'description': 'Agente SDR mock para testes offline',
    'system_prompt': """Voce e Isabella, uma SDR virtual da Mottivme Sales.

SEU OBJETIVO:
- Qualificar leads usando metodologia BANT
- Agendar reunioes com leads qualificados
- Manter tom consultivo e profissional

REGRAS:
1. Sempre cumprimente de forma amigavel
2. Faca perguntas abertas para qualificar
3. Nunca fale mal de concorrentes
4. Ancora valor antes de falar preco
5. Seja empativo com objecoes

QUALIFICACAO BANT:
- Budget: Qual investimento esta disposto a fazer?
- Authority: Quem decide na empresa?
- Need: Qual problema quer resolver?
- Timeline: Quando precisa da solucao?
""",
    'agent_config': {
        'modos_identificados': ['qualificacao', 'objecoes', 'agendamento']
    }
}


# Test cases com respostas simuladas
TEST_CASES_WITH_RESPONSES = [
    {
        'name': 'Lead frio - primeira mensagem',
        'input': 'Oi',
        'expected_behavior': 'Cumprimento amigavel + pergunta aberta',
        'agent_response': 'Ola! Tudo bem? Sou a Isabella da Mottivme. Vi que voce demonstrou interesse em nossas solucoes de automacao. Me conta, o que te trouxe ate aqui hoje?',
        'rubric_focus': ['tone', 'engagement']
    },
    {
        'name': 'Lead pergunta preco',
        'input': 'Quanto custa?',
        'expected_behavior': 'Ancora valor + qualifica',
        'agent_response': 'Otima pergunta! Nossos planos variam de acordo com a necessidade de cada empresa. Para te dar um valor mais preciso, me conta: qual e o principal desafio que voce quer resolver com automacao? E quantas pessoas trabalham no seu time de vendas hoje?',
        'rubric_focus': ['compliance', 'completeness']
    },
    {
        'name': 'Lead interessado - qualificacao',
        'input': 'Preciso automatizar meu atendimento, temos 10 funcionarios',
        'expected_behavior': 'Qualifica BANT completo',
        'agent_response': 'Que legal! 10 funcionarios e um time de bom tamanho. Automacao de atendimento pode realmente fazer diferenca ai. Me conta mais: qual canal de atendimento e mais movimentado pra voces - WhatsApp, email ou telefone? E voce e quem decide sobre novas ferramentas na empresa?',
        'rubric_focus': ['completeness', 'engagement']
    },
    {
        'name': 'Lead com objecao',
        'input': 'Parece legal mas agora nao tenho tempo pra ver isso',
        'expected_behavior': 'Trata objecao + oferece alternativa',
        'agent_response': 'Entendo perfeitamente! O dia a dia de quem esta crescendo e sempre corrido. Que tal marcarmos uma call rapida de 15 minutos em um horario que funcione melhor pra voce? Assim consigo te mostrar exatamente como podemos economizar horas do seu time. Qual seria um bom dia essa semana?',
        'rubric_focus': ['tone', 'conversion']
    },
    {
        'name': 'Lead quente - quer agendar',
        'input': 'OK, vamos marcar uma reuniao',
        'expected_behavior': 'Confirma agendamento + coleta dados',
        'agent_response': 'Perfeito! Vou agendar nossa conversa. Tenho disponibilidade amanha as 10h ou quinta as 14h - qual funciona melhor pra voce? E ja me passa seu email e telefone para eu enviar o convite?',
        'rubric_focus': ['conversion', 'completeness']
    }
]


async def run_offline_test():
    """Executa teste offline (sem Supabase)"""

    logger.info("=" * 50)
    logger.info("AI Factory - Offline Test Mode")
    logger.info("=" * 50)

    # Verificar API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set!")
        return False

    # Criar diretorio de saida
    output_dir = Path('./reports')
    output_dir.mkdir(exist_ok=True)

    # Inicializar componentes
    logger.info("\n1. Initializing components...")

    evaluator = Evaluator(api_key=api_key)
    logger.info("   [OK] Evaluator (Claude Opus)")

    reporter = ReportGenerator(output_dir=str(output_dir))
    logger.info("   [OK] Report Generator")

    # Usar test cases com respostas pre-definidas
    logger.info("\n2. Using mock agent and pre-defined responses...")
    logger.info(f"   Agent: {MOCK_AGENT['name']}")
    logger.info(f"   Test cases: {len(TEST_CASES_WITH_RESPONSES)}")

    # Avaliar com Claude Opus
    logger.info("\n3. Evaluating with Claude Opus...")

    start_time = datetime.now()

    evaluation = await evaluator.evaluate(
        agent=MOCK_AGENT,
        skill=None,
        test_results=TEST_CASES_WITH_RESPONSES
    )

    eval_duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"   Evaluation completed in {eval_duration:.1f}s")

    # Gerar relatorio
    logger.info("\n4. Generating HTML report...")

    report_url = await reporter.generate_html_report(
        agent=MOCK_AGENT,
        evaluation=evaluation,
        test_results=TEST_CASES_WITH_RESPONSES
    )

    logger.info(f"   Report saved to: {report_url}")

    # Mostrar resultados
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS")
    logger.info("=" * 50)

    overall = evaluation.get('overall_score', 0)
    logger.info(f"\nOverall Score: {overall:.1f}/10")

    if overall >= 8.0:
        logger.info("Status: APPROVED")
    elif overall >= 6.0:
        logger.info("Status: NEEDS IMPROVEMENT")
    else:
        logger.info("Status: FAILED")

    # Score breakdown
    scores = evaluation.get('scores', {})
    logger.info("\nScore Breakdown:")
    logger.info(f"  - Completeness (25%): {scores.get('completeness', 0):.1f}")
    logger.info(f"  - Tone (20%):         {scores.get('tone', 0):.1f}")
    logger.info(f"  - Engagement (20%):   {scores.get('engagement', 0):.1f}")
    logger.info(f"  - Compliance (20%):   {scores.get('compliance', 0):.1f}")
    logger.info(f"  - Conversion (15%):   {scores.get('conversion', 0):.1f}")

    # Strengths
    if evaluation.get('strengths'):
        logger.info("\nStrengths:")
        for s in evaluation['strengths']:
            logger.info(f"  + {s}")

    # Weaknesses
    if evaluation.get('weaknesses'):
        logger.info("\nWeaknesses:")
        for w in evaluation['weaknesses']:
            logger.info(f"  - {w}")

    # Recommendations
    if evaluation.get('recommendations'):
        logger.info("\nRecommendations:")
        for r in evaluation['recommendations']:
            logger.info(f"  > {r}")

    logger.info("\n" + "=" * 50)
    logger.info(f"Report available at: {report_url}")
    logger.info("=" * 50)

    return True


def main():
    # Carregar .env
    load_dotenv()

    # Executar
    success = asyncio.run(run_offline_test())
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
