#!/usr/bin/env python3
"""
Full Flow Example - AI Factory Testing Framework
=================================================
Demonstra o fluxo completo: Test Runner -> Evaluator -> Report Generator
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from evaluator import Evaluator
from report_generator import ReportGenerator


async def main():
    """Demonstra fluxo completo de teste e geração de relatório."""

    print("\n" + "="*60)
    print("  AI FACTORY TESTING FRAMEWORK - FULL FLOW DEMO")
    print("="*60 + "\n")

    # ========================================
    # ETAPA 1: DADOS DO AGENTE
    # ========================================
    print("📋 ETAPA 1: Carregar dados do agente")
    print("-" * 60)

    agent = {
        'id': 'demo-agent-001',
        'name': 'Luna - Customer Success AI',
        'version': 3,
        'description': 'Agente de atendimento ao cliente especializado em onboarding e suporte técnico.',
        'system_prompt': """Você é Luna, uma assistente de Customer Success especializada.

Suas responsabilidades:
1. Fazer onboarding de novos clientes
2. Responder dúvidas técnicas
3. Identificar oportunidades de upsell
4. Coletar feedback e NPS
5. Escalar problemas complexos para humanos

Guardrails:
- Nunca prometer SLA não documentado
- Sempre confirmar entendimento antes de solucionar
- Ser empática mas objetiva
- Documentar todas as interações
"""
    }

    print(f"   Agent: {agent['name']} v{agent['version']}")
    print(f"   ID: {agent['id']}")
    print(f"   ✓ Dados carregados\n")

    # ========================================
    # ETAPA 2: EXECUTAR CASOS DE TESTE
    # ========================================
    print("🧪 ETAPA 2: Executar casos de teste")
    print("-" * 60)

    # Simulando resultados de testes (normalmente viria do TestRunner)
    test_results = [
        {
            'name': 'Onboarding - Primeiro contato',
            'input': 'Oi, acabei de assinar o plano Pro. Como começar?',
            'agent_response': """Olá! Bem-vindo ao plano Pro! 🎉

Vou te ajudar no onboarding. Primeiro, me conta:

1. Qual o principal objetivo que você quer alcançar com nossa plataforma?
2. Você já trabalhou com ferramentas similares antes?
3. Quantas pessoas vão usar a plataforma na sua equipe?

Com essas informações, vou te guiar no setup ideal!""",
            'expected_behavior': 'Iniciar onboarding com perguntas de qualificação',
            'score': 0,
            'passed': False,
            'feedback': ''
        },
        {
            'name': 'Suporte - Problema técnico',
            'input': 'Não consigo fazer upload de arquivos, dá erro.',
            'agent_response': """Entendo sua frustração! Vamos resolver isso.

Primeiro, me ajuda a entender melhor:

1. Qual tipo de arquivo você está tentando fazer upload? (PDF, imagem, etc)
2. Qual o tamanho aproximado do arquivo?
3. O erro aparece logo ao selecionar o arquivo ou durante o upload?

Essas informações vão me ajudar a identificar a causa.""",
            'expected_behavior': 'Coletar informações do problema antes de tentar resolver',
            'score': 0,
            'passed': False,
            'feedback': ''
        },
        {
            'name': 'Upsell - Cliente usando recursos básicos',
            'input': 'Estou gostando bastante, mas sinto falta de mais funcionalidades.',
            'agent_response': """Que bom que está gostando! 😊

Deixa eu te perguntar: quais funcionalidades específicas você sente falta?

Pergunto porque temos recursos avançados no plano Pro que talvez você não esteja usando ainda (ou que fazem mais sentido no seu caso):

- Automações personalizadas
- Integrações com outras ferramentas
- Relatórios avançados
- API de desenvolvimento

Qual desses te interessaria mais?""",
            'expected_behavior': 'Identificar necessidade antes de propor upgrade',
            'score': 0,
            'passed': False,
            'feedback': ''
        }
    ]

    print(f"   Total de testes: {len(test_results)}")
    print(f"   ✓ Casos de teste preparados\n")

    # ========================================
    # ETAPA 3: AVALIAR COM LLM-AS-JUDGE
    # ========================================
    print("🤖 ETAPA 3: Avaliar com Claude Opus (LLM-as-Judge)")
    print("-" * 60)

    # Skill do agente (rubrica de avaliação)
    skill = {
        'rubric': """
## Rubrica de Avaliação - Customer Success Agent

### 1. EMPATHY (25%)
- Demonstra empatia genuína?
- Reconhece frustração/dificuldade do cliente?
- Usa linguagem acolhedora?

Score:
- 10: Empatia excelente, cliente se sente compreendido
- 8: Boa empatia, pequenos ajustes
- 6: Empático mas genérico
- 4: Pouca empatia
- 2: Sem empatia

### 2. DISCOVERY (25%)
- Faz perguntas antes de propor soluções?
- Entende contexto completo?
- Personaliza abordagem?

Score:
- 10: Discovery completo, perguntas relevantes
- 8: Bom discovery, poderia aprofundar
- 6: Discovery básico
- 4: Pouco discovery
- 2: Sem discovery, assume informações

### 3. PROBLEM SOLVING (25%)
- Resolve problema de forma eficaz?
- Explica claramente os passos?
- Documenta para futuro?

Score:
- 10: Resolução clara, eficaz e documentada
- 8: Resolve bem, poderia ser mais claro
- 6: Resolve parcialmente
- 4: Não resolve adequadamente
- 2: Não resolve

### 4. PROACTIVITY (15%)
- Antecipa necessidades?
- Sugere melhorias?
- Identifica oportunidades?

Score:
- 10: Muito proativo, agrega valor extra
- 8: Proativo, sugere relevante
- 6: Proativo ocasionalmente
- 4: Pouco proativo
- 2: Apenas reativo

### 5. COMPLIANCE (10%)
- Segue guardrails?
- Escala quando apropriado?
- Não promete o que não pode?

Score:
- 10: 100% compliance
- 8: Pequenos desvios não críticos
- 6: Alguns desvios
- 4: Desvios significativos
- 2: Ignora guardrails
"""
    }

    # NOTA: Em produção, usar Evaluator real com API key
    # evaluator = Evaluator(api_key=os.getenv('ANTHROPIC_API_KEY'))
    # evaluation = await evaluator.evaluate(agent, skill, test_results)

    # Para este demo, simular avaliação
    print("   ⚠️  Demo mode: Usando avaliação simulada")
    print("   💡 Em produção, usar: evaluator.evaluate(agent, skill, test_results)")

    evaluation = {
        'overall_score': 8.3,
        'scores': {
            'empathy': 9.0,
            'discovery': 8.5,
            'problem_solving': 8.0,
            'proactivity': 7.5,
            'compliance': 8.5
        },
        'test_case_evaluations': [
            {
                'test_name': test_results[0]['name'],
                'score': 8.5,
                'passed': True,
                'feedback': 'Excelente onboarding! Fez perguntas relevantes e criou rapport. Tom acolhedor e profissional.'
            },
            {
                'test_name': test_results[1]['name'],
                'score': 8.0,
                'passed': True,
                'feedback': 'Bom troubleshooting. Coletou informações antes de propor solução. Poderia ter demonstrado mais empatia com a frustração.'
            },
            {
                'test_name': test_results[2]['name'],
                'score': 8.5,
                'passed': True,
                'feedback': 'Identificou oportunidade de upsell de forma consultiva. Não foi invasivo. Apresentou opções relevantes.'
            }
        ],
        'strengths': [
            'Empatia genuína - cliente se sente acolhido e compreendido',
            'Discovery estruturado - sempre faz perguntas antes de agir',
            'Tom consultivo - não empurra soluções, sugere baseado em necessidades',
            'Compliance excelente - segue guardrails e não promete o que não pode',
            'Proatividade balanceada - sugere melhorias sem ser invasivo'
        ],
        'weaknesses': [
            'Poderia personalizar mais baseado em contexto do cliente',
            'Falta criar senso de urgência em alguns cenários',
            'Uso de emojis pode ser excessivo para clientes corporativos formais'
        ],
        'failures': [],
        'warnings': [
            'Atenção ao uso de emojis - ajustar conforme perfil do cliente'
        ],
        'recommendations': [
            'Implementar detecção de tom/formalidade do cliente',
            'Adicionar mais casos de sucesso durante conversas',
            'Incluir links para documentação relevante',
            'Testar variações de urgência em diferentes cenários'
        ]
    }

    # Atualizar test_results com scores da avaliação
    for i, test_result in enumerate(test_results):
        if i < len(evaluation['test_case_evaluations']):
            eval_data = evaluation['test_case_evaluations'][i]
            test_result['score'] = eval_data['score']
            test_result['passed'] = eval_data['passed']
            test_result['feedback'] = eval_data['feedback']

    print(f"   Overall Score: {evaluation['overall_score']}/10")
    print(f"   Status: {'✅ APPROVED' if evaluation['overall_score'] >= 8.0 else '⚠️  NEEDS IMPROVEMENT'}")
    print(f"   ✓ Avaliação concluída\n")

    # ========================================
    # ETAPA 4: GERAR RELATÓRIO HTML
    # ========================================
    print("📄 ETAPA 4: Gerar relatório HTML profissional")
    print("-" * 60)

    generator = ReportGenerator(
        output_dir=str(Path(__file__).parent / 'reports')
    )

    report_path = await generator.generate_html_report(
        agent=agent,
        evaluation=evaluation,
        test_results=test_results
    )

    print(f"   ✓ Relatório gerado: {Path(report_path).name}")
    print(f"   📍 Localização: {report_path}\n")

    # ========================================
    # RESUMO FINAL
    # ========================================
    print("="*60)
    print("  RESUMO DO FLUXO")
    print("="*60)
    print(f"✅ Agent: {agent['name']} v{agent['version']}")
    print(f"✅ Testes executados: {len(test_results)}")
    print(f"✅ Score geral: {evaluation['overall_score']}/10")
    print(f"✅ Status: {'APPROVED ✓' if evaluation['overall_score'] >= 8.0 else 'NEEDS IMPROVEMENT ⚠'}")
    print(f"✅ Relatório: {Path(report_path).name}")
    print()
    print("🌐 Abrir relatório no navegador:")
    print(f"   open {report_path}")
    print()
    print("="*60 + "\n")

    return report_path


if __name__ == '__main__':
    asyncio.run(main())
