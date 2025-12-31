#!/usr/bin/env python3
"""
AI Factory V4 - Comprehensive Test Runner Demo
===============================================

Demonstra o uso completo do TestRunner com:
1. Agente mock
2. Test cases customizados
3. Simulação de respostas com Claude
4. Avaliação com Claude Opus
5. Geração de relatório HTML

Usage:
    ANTHROPIC_API_KEY=sk-ant-xxx python test_runner_comprehensive.py
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from src.supabase_client import SupabaseClient
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator
from src.test_runner import TestRunner, DEFAULT_SDR_TEST_CASES

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mock agent data (simulating agent_version from Supabase)
MOCK_AGENT_COMPLETE = {
    'id': 'mock-agent-isabella-001',
    'name': 'Isabella SDR v1.0',
    'version': 1,
    'agent_name': 'Isabella SDR',
    'description': 'Agente SDR especializado em qualificação BANT e agendamento',
    'purpose': 'Qualificar leads usando metodologia BANT e agendar reuniões',
    'system_prompt': """Você é Isabella, uma SDR (Sales Development Representative) virtual.

SEU PAPEL:
Você é uma consultora de vendas experiente, amigável e profissional.
Seu objetivo é qualificar leads em potencial e agendar reuniões de discovery.

METODOLOGIA BANT:
Você SEMPRE qualifica usando BANT:
- B: Budget (capacidade de investimento)
- A: Authority (quem decide)
- N: Need (problema/necessidade)
- T: Timeline (prazo de implementação)

REGRAS OBRIGATÓRIAS:
1. Cumprimente sempre de forma amigável e pessoal
2. Comece perguntando sobre o desafio/interesse do lead
3. Nunca mencione preço sem antes entender o valor (anchoring)
4. Trate objeções com empatia e ofereça alternativas
5. Qualifique ANTES de oferecer solução
6. Nunca fale mal de concorrentes
7. Mantenha tom consultivo, não vendedor agressivo
8. Se o lead não for qualificado, termine educadamente

ESTRUTURA DA CONVERSA:
1. Abertura amigável + pergunta aberta
2. Qualificação BANT (2-3 perguntas)
3. Oferta de próximo passo (reunião/call)
4. Agendamento ou follow-up

EXEMPLOS DE COMPORTAMENTO ESPERADO:
- Lead frio: "Oi! Vi seu interesse em automação. O que te trouxe aqui?"
- Pergunta de preço: "Ótima pergunta! Antes de citar valores, me conta - qual é o principal desafio?"
- Objeção: "Entendo! O dia é corrido mesmo. E se fosse apenas 15 minutos?"
- Qualificado: "Perfeito! Vamos marcar uma call? Que tal amanhã às 10h?"

Sempre seja genuinamente interessado no sucesso do lead, não apenas na venda.
""",
    'agent_config': {
        'modos_identificados': ['qualificacao', 'objecoes', 'agendamento'],
        'target_audience': 'Empresas com 5-50 funcionários',
        'industry': 'SaaS, Tech, Agências'
    }
}

# Mock skill (instrções adicionais)
MOCK_SKILL = {
    'id': 'skill-isabella-001',
    'agent_version_id': 'mock-agent-isabella-001',
    'version': 1,
    'instructions': """## Instruções Especiais para Isabella

### Contexto do Negócio
Estamos vendendo Mottivme Sales - uma plataforma de automação de vendas.

### Proposição de Valor
- Automatiza 80% das tarefas repetitivas
- Integração com WhatsApp, Email, SMS
- Relatórios em tempo real
- Suporte dedicado

### Segmentação
- Leads B2B (empresas, agências, consultorias)
- Budget mínimo: R$ 500/mês
- Timeline ideal: 30-60 dias

### Táticas por Situação
**Se pergunta sobre preço:**
"Nossos planos começam em R$ 500/mês para pequenas equipes e vão até R$ 2000+.
Mas antes, qual é o volume de contatos que você manipula por mês?"

**Se recusa por "não ter tempo":**
"Entendo! Mas sabe, o tempo que você gasta manualmente em contatos é exatamente
o que a Mottivme automatiza. Seria bom ver isso?"

**Se é concorrente direto:**
"Legal que já usa X. Podemos fazer uma comparação rápida? Temos uns diferenciais
interessantes em relatórios e integrações que vale a pena você conhecer."
""",
    'examples': """## Exemplos de Conversas Bem-Sucedidas

### Exemplo 1: Lead Frio → Qualificado
Lead: "Oi, vi seu anúncio"
Isabella: "Oi! Tudo bem? Vi que você trabalha com vendas. Me conta, qual é o principal desafio que seu time enfrenta hoje?"
Lead: "A gente não consegue acompanhar todos os leads"
Isabella: "Que comum! E quantas pessoas trabalham no seu time de vendas? E vocês usam alguma ferramenta atualmente?"
...

### Exemplo 2: Lead Com Objeção de Preço
Lead: "Quanto custa?"
Isabella: "Ótima pergunta! Nossos planos variam bastante. Primeiro, me conta - você é quem decide sobre ferramentas ou precisa de aprovação?"
Lead: "Preciso conversar com meu sócio"
Isabella: "Perfeito. Que tal eu faço uma apresentação rápida para vocês dois? A call leva 20 minutos e vocês veem exatamente como funciona e quanto custa."
...
""",
    'rubric': """## Rubrica Customizada para Isabella

### Completeness (Qualificação BANT)
- 10: BANT completo, todas 4 dimensões identificadas
- 8: 3 dimensões cobertas, 1 parcial
- 6: 2 dimensões cobertas
- 4: Apenas 1 dimensão
- 2: Sem qualificação

### Tone (Tom Consultivo)
- 10: Genuinamente interessado, empático, consultivo
- 8: Profissional, amigável, alguns momentos menos personalizados
- 6: Adequado, mas genérico
- 4: Um pouco vendedor demais
- 2: Agressivo ou inadequado

### Engagement (Engajamento do Lead)
- 10: Lead respondendo ativamente, demonstrando interesse
- 8: Boa participação, respostas substantivas
- 6: Participação mínima, respostas curtas
- 4: Lead pouco engajado
- 2: Lead desengajado ou saiu da conversa

### Compliance (Seguir Instruções)
- 10: Seguiu tudo perfeitamente
- 8: Pequenos desvios não críticos
- 6: Alguns desvios das instruções
- 4: Desvios significativos
- 2: Ignorou instruções

### Conversion (Conversão/Agendamento)
- 10: Agendamento confirmado
- 8: Lead muito qualificado, próximo passo claro
- 6: Lead qualificado, sem conversão
- 4: Inconclusivo
- 2: Lead perdido
"""
}


async def test_agent_simulation():
    """
    Testa a simulação de agente com Claude.
    Mostra como o TestRunner simula respostas de agente.
    """
    logger.info("="*60)
    logger.info("TESTE 1: Simulação de Agente com Claude")
    logger.info("="*60)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set!")
        return False

    # Criar TestRunner
    runner = TestRunner(
        supabase_client=None,
        evaluator=None,
        report_generator=None,
        anthropic_api_key=api_key
    )

    # Testar simulação de resposta
    system_prompt = MOCK_AGENT_COMPLETE['system_prompt']
    test_inputs = [
        "Oi",
        "Quanto custa?",
        "Não tenho tempo agora"
    ]

    logger.info("\nTestando simulação de respostas do agente...\n")

    for i, user_input in enumerate(test_inputs, 1):
        logger.info(f"Input {i}: {user_input}")
        response = await runner._simulate_agent_response(
            system_prompt=system_prompt,
            user_message=user_input
        )
        logger.info(f"Response: {response[:200]}...\n")

    return True


async def test_evaluator():
    """
    Testa o Evaluator (Claude Opus).
    Avalia casos de teste pré-definidos.
    """
    logger.info("="*60)
    logger.info("TESTE 2: Avaliação com Claude Opus")
    logger.info("="*60)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set!")
        return False

    # Dados de teste com respostas simuladas
    test_cases = [
        {
            'name': 'Lead frio - primeira mensagem',
            'input': 'Oi',
            'expected_behavior': 'Cumprimento amigavel + pergunta aberta',
            'agent_response': 'Ola! Tudo bem? Sou a Isabella da Mottivme. Vi que voce demonstrou interesse em nossas solucoes de automacao. Me conta, o que te trouxe ate aqui hoje?',
            'rubric_focus': ['tone', 'engagement']
        },
        {
            'name': 'Lead pergunta preco direto',
            'input': 'Quanto custa?',
            'expected_behavior': 'Ancora valor antes de preco + qualifica necessidade',
            'agent_response': 'Otima pergunta! Nossos planos variam de acordo com a necessidade de cada empresa. Para te dar um valor mais preciso, me conta: qual e o principal desafio que voce quer resolver com automacao? E quantas pessoas trabalham no seu time de vendas hoje?',
            'rubric_focus': ['compliance', 'completeness']
        },
        {
            'name': 'Lead interessado - qualificacao BANT',
            'input': 'Preciso automatizar meu atendimento, temos uma equipe de 5 pessoas.',
            'expected_behavior': 'Qualifica Budget, Authority, Need, Timeline',
            'agent_response': 'Que legal! 5 pessoas e um time de bom tamanho. Automacao de atendimento pode realmente fazer diferenca ai. Me conta mais: qual canal de atendimento e mais movimentado pra voces - WhatsApp, email ou telefone? E voce e quem decide sobre novas ferramentas na empresa?',
            'rubric_focus': ['completeness', 'engagement']
        },
        {
            'name': 'Lead com objecao - nao tenho tempo',
            'input': 'Parece interessante mas agora nao tenho tempo pra ver isso',
            'expected_behavior': 'Trata objecao com empatia + oferece opcao rapida',
            'agent_response': 'Entendo perfeitamente! O dia a dia de quem esta crescendo e sempre corrido. Que tal marcarmos uma call rapida de 15 minutos em um horario que funcione melhor pra voce? Assim consigo te mostrar exatamente como podemos economizar horas do seu time. Qual seria um bom dia essa semana?',
            'rubric_focus': ['tone', 'conversion']
        },
        {
            'name': 'Lead quente - quer agendar',
            'input': 'OK, vamos marcar uma reuniao',
            'expected_behavior': 'Confirma agendamento + coleta informacoes necessarias',
            'agent_response': 'Perfeito! Vou agendar nossa conversa. Tenho disponibilidade amanha as 10h ou quinta as 14h - qual funciona melhor pra voce? E ja me passa seu email e telefone para eu enviar o convite?',
            'rubric_focus': ['conversion', 'completeness']
        }
    ]

    logger.info(f"\nAvaliando {len(test_cases)} casos de teste...\n")

    evaluator = Evaluator(api_key=api_key)
    evaluation = await evaluator.evaluate(
        agent=MOCK_AGENT_COMPLETE,
        skill=MOCK_SKILL,
        test_results=test_cases
    )

    # Mostrar resultados
    logger.info(f"Overall Score: {evaluation['overall_score']:.1f}/10")
    logger.info("\nScore Breakdown:")
    for dim, score in evaluation['scores'].items():
        logger.info(f"  - {dim.capitalize()}: {score:.1f}")

    logger.info("\nStrengths:")
    for s in evaluation.get('strengths', []):
        logger.info(f"  + {s}")

    logger.info("\nWeaknesses:")
    for w in evaluation.get('weaknesses', []):
        logger.info(f"  - {w}")

    return True


async def test_report_generation():
    """
    Testa a geração de relatório HTML.
    """
    logger.info("="*60)
    logger.info("TESTE 3: Geração de Relatório HTML")
    logger.info("="*60)

    # Criar diretório de saída
    output_dir = Path('./test_reports')
    output_dir.mkdir(exist_ok=True)

    # Dados simulados
    test_cases = [
        {
            'name': 'Lead frio',
            'input': 'Oi',
            'expected_behavior': 'Cumprimento amigavel',
            'agent_response': 'Ola! Tudo bem? Sou a Isabella.',
            'score': 8.5,
            'passed': True,
            'feedback': 'Excelente tom e engajamento'
        },
        {
            'name': 'Pergunta preço',
            'input': 'Quanto custa?',
            'expected_behavior': 'Qualifica antes de responder preço',
            'agent_response': 'Otima pergunta! Qual e seu principal desafio?',
            'score': 7.8,
            'passed': True,
            'feedback': 'Bom anchoring, poderia qualificar mais'
        }
    ]

    evaluation = {
        'overall_score': 8.15,
        'scores': {
            'completeness': 8.0,
            'tone': 9.0,
            'engagement': 8.5,
            'compliance': 8.0,
            'conversion': 7.0
        },
        'test_case_evaluations': [
            {'test_name': 'Lead frio', 'score': 8.5, 'passed': True, 'feedback': 'Excelente'},
            {'test_name': 'Pergunta preço', 'score': 7.8, 'passed': True, 'feedback': 'Bom'}
        ],
        'strengths': ['Excelente tom consultivo', 'Bom engajamento do lead'],
        'weaknesses': ['Poderia aprofundar mais a qualificação timeline'],
        'failures': [],
        'warnings': [],
        'recommendations': ['Incluir mais perguntas sobre timeline nas futuras conversas']
    }

    logger.info("\nGerando relatório HTML...\n")

    reporter = ReportGenerator(output_dir=str(output_dir))
    report_path = await reporter.generate_html_report(
        agent=MOCK_AGENT_COMPLETE,
        evaluation=evaluation,
        test_results=test_cases
    )

    logger.info(f"Relatório gerado com sucesso!")
    logger.info(f"Caminho: {report_path}")
    logger.info(f"\nAbra em seu navegador para visualizar o relatório completo")

    return True


async def test_full_pipeline():
    """
    Testa o pipeline completo do TestRunner:
    1. Carregar agente
    2. Executar testes (simulação)
    3. Avaliar com Claude Opus
    4. Gerar relatório
    """
    logger.info("="*60)
    logger.info("TESTE 4: Pipeline Completo (Full Flow)")
    logger.info("="*60)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set!")
        return False

    # Output directory
    output_dir = Path('./test_reports')
    output_dir.mkdir(exist_ok=True)

    logger.info("\n1. Inicializando componentes...")
    evaluator = Evaluator(api_key=api_key)
    reporter = ReportGenerator(output_dir=str(output_dir))
    runner = TestRunner(
        supabase_client=None,
        evaluator=evaluator,
        report_generator=reporter,
        anthropic_api_key=api_key
    )
    logger.info("   ✓ Componentes inicializados")

    # Test cases
    logger.info("\n2. Usando test cases padrão...")
    test_cases_to_use = [
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
        }
    ]
    logger.info(f"   ✓ {len(test_cases_to_use)} test cases carregados")

    # Executar testes
    logger.info("\n3. Executando testes (simulando respostas)...")
    results = []
    for i, test_case in enumerate(test_cases_to_use, 1):
        logger.info(f"   Teste {i}/{len(test_cases_to_use)}: {test_case['name']}")
        result = await runner._run_single_test(
            agent=MOCK_AGENT_COMPLETE,
            skill=MOCK_SKILL,
            test_case=test_case
        )
        results.append(result)
    logger.info(f"   ✓ {len(results)} testes executados")

    # Avaliar
    logger.info("\n4. Avaliando com Claude Opus...")
    evaluation = await evaluator.evaluate(
        agent=MOCK_AGENT_COMPLETE,
        skill=MOCK_SKILL,
        test_results=results
    )
    logger.info(f"   ✓ Avaliação concluída: {evaluation['overall_score']:.1f}/10")

    # Gerar relatório
    logger.info("\n5. Gerando relatório HTML...")
    report_url = await reporter.generate_html_report(
        agent=MOCK_AGENT_COMPLETE,
        evaluation=evaluation,
        test_results=results
    )
    logger.info(f"   ✓ Relatório gerado: {report_url}")

    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("RESULTADO FINAL")
    logger.info("="*60)
    logger.info(f"\nAgente: {MOCK_AGENT_COMPLETE['name']}")
    logger.info(f"Score: {evaluation['overall_score']:.1f}/10")
    logger.info(f"Status: {'✓ APROVADO' if evaluation['overall_score'] >= 8.0 else '⚠ PRECISA MELHORAR'}")
    logger.info(f"\nRelatório disponível em: {report_url}")

    return True


async def main():
    """Main entry point"""

    # Carregar .env
    load_dotenv()

    logger.info("\n")
    logger.info("╔" + "═"*58 + "╗")
    logger.info("║" + " "*58 + "║")
    logger.info("║" + "  AI FACTORY V4 - COMPREHENSIVE TEST SUITE".center(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("╚" + "═"*58 + "╝")
    logger.info("")

    # Verificar API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("\n❌ ANTHROPIC_API_KEY not set!")
        logger.error("   Please set your API key and try again.")
        logger.error("   export ANTHROPIC_API_KEY='sk-ant-...'")
        return 1

    logger.info(f"✓ API Key detected: {api_key[:20]}...\n")

    try:
        # Correr testes
        all_passed = True

        # Teste 1: Simulação de agente
        logger.info("\n\n")
        if not await test_agent_simulation():
            all_passed = False

        # Teste 2: Avaliação
        logger.info("\n\n")
        if not await test_evaluator():
            all_passed = False

        # Teste 3: Relatório
        logger.info("\n\n")
        if not await test_report_generation():
            all_passed = False

        # Teste 4: Pipeline completo
        logger.info("\n\n")
        if not await test_full_pipeline():
            all_passed = False

        if all_passed:
            logger.info("\n\n✓ Todos os testes passaram com sucesso!")
            return 0
        else:
            logger.error("\n\n✗ Alguns testes falharam")
            return 1

    except Exception as e:
        logger.error(f"\n✗ Erro durante execução: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
