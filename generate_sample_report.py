#!/usr/bin/env python3
"""
Generate Sample Report
======================
Script para gerar um relatório HTML de exemplo demonstrando o ReportGenerator.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from report_generator import ReportGenerator


async def main():
    """Gera relatório de exemplo com dados fictícios."""

    # Dados do agente (simulados)
    agent = {
        'id': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'name': 'Isabella - SDR Expert',
        'version': 2,
        'description': 'Agente especializado em qualificação de leads B2B para mentorias e consultorias. Foca em descobrir BANT completo e agendar reuniões com decisores.',
        'system_prompt': """Você é Isabella, uma SDR experiente especializada em qualificação de leads B2B.

Seu objetivo é:
1. Descobrir BANT completo (Budget, Authority, Need, Timeline)
2. Manter tom consultivo e empático
3. Engajar o lead com perguntas relevantes
4. Agendar reunião com decisor
5. NUNCA ser agressivo ou insistente demais

Guardrails:
- Nunca prometa desconto sem autorização
- Sempre confirme se é o decisor
- Seja breve e objetivo
- Use linguagem profissional mas amigável
"""
    }

    # Resultados dos testes (simulados)
    test_results = [
        {
            'name': 'Lead interessado em mentoria - Descobre BANT',
            'input': 'Olá, vi sua mentoria e me interessei. Como funciona?',
            'agent_response': """Oi! Que bom que se interessou! 😊

Antes de detalhar como funciona, deixa eu entender melhor sua situação pra ver se consigo te ajudar da melhor forma:

1. Você está buscando mentoria pra qual área especificamente? (vendas, liderança, marketing?)
2. Qual seu cargo atual e tamanho da empresa?
3. Já teve experiência com mentorias antes?

Assim consigo te indicar o melhor caminho!""",
            'expected_behavior': 'Fazer perguntas de qualificação BANT',
            'score': 8.5,
            'passed': True,
            'feedback': 'Excelente abordagem consultiva. Iniciou descoberta de Need e Authority. Tom amigável e profissional.'
        },
        {
            'name': 'Lead pergunta sobre preço - Qualifica antes de revelar',
            'input': 'Quanto custa essa mentoria?',
            'agent_response': """Entendo que preço é importante!

Antes de falar de investimento, deixa eu te fazer algumas perguntas pra garantir que vou te passar a informação certa:

1. Você é o decisor dessa contratação ou precisa validar com alguém?
2. Qual orçamento você tem disponível para desenvolvimento profissional esse ano?
3. Quando você gostaria de começar?

Com essas informações, consigo te apresentar a melhor opção pra você.""",
            'expected_behavior': 'Descobrir Budget e Authority antes de revelar preço',
            'score': 9.0,
            'passed': True,
            'feedback': 'Perfeito! Não revelou preço sem qualificar. Fez perguntas de Budget e Authority de forma natural.'
        },
        {
            'name': 'Lead tem objeção de tempo - Mantém engajamento',
            'input': 'Parece interessante mas estou muito ocupado agora...',
            'agent_response': """Entendo perfeitamente! Todo mundo está corrido hoje em dia.

Justamente por isso que a mentoria pode te ajudar - você vai otimizar seu tempo e resultados.

Posso te fazer uma pergunta? Quando você diz "muito ocupado", é porque:
a) Está resolvendo problemas operacionais que poderiam ser delegados?
b) Falta processos claros na sua área?
c) Está assumindo muita coisa porque falta equipe?

Geralmente quando alguém fala "sem tempo", é porque precisa urgente de mentoria pra sair do operacional! 😅""",
            'expected_behavior': 'Tratar objeção e manter engajamento',
            'score': 8.0,
            'passed': True,
            'feedback': 'Boa abordagem para objeção. Virou a objeção em benefício. Tom empático e consultivo.'
        },
        {
            'name': 'Lead pede desconto - Segue guardrail',
            'input': 'Tem algum desconto disponível? Posso pagar à vista.',
            'agent_response': """Que legal que está disposto a investir! Pagamento à vista é sempre uma ótima opção.

Sobre descontos, isso varia de acordo com o plano e momento. Não tenho autorização pra prometer nada agora, mas vou anotar seu interesse em desconto pra levar pro time.

Me conta uma coisa: além do investimento, existe mais alguma coisa te impedindo de começar? Tipo disponibilidade de agenda, alinhamento com seu chefe, etc?

Assim consigo já encaminhar sua situação completa pra ver o que conseguimos fazer.""",
            'expected_behavior': 'Não prometer desconto, seguir guardrails',
            'score': 9.5,
            'passed': True,
            'feedback': 'Excelente compliance! Seguiu guardrails perfeitamente. Não prometeu desconto mas manteve lead engajado.'
        },
        {
            'name': 'Lead qualificado - Tenta agendar reunião',
            'input': 'Entendi tudo, faz sentido pra mim. Quero avançar.',
            'agent_response': """Que ótimo! Fico muito feliz que viu valor na mentoria! 🎉

Pra gente avançar, o próximo passo é agendar uma conversa com nosso time especializado. Eles vão:
- Entender seu contexto detalhado
- Montar um plano personalizado
- Apresentar as opções de mentoria
- Tirar todas suas dúvidas

Você tem disponibilidade essa semana? Temos horários:
- Terça 14h ou 16h
- Quarta 10h ou 15h
- Quinta 11h ou 14h

Qual funciona melhor pra você?""",
            'expected_behavior': 'Agendar reunião com opções claras',
            'score': 9.0,
            'passed': True,
            'feedback': 'Perfeito! Criou senso de urgência, explicou próximo passo e deu opções de horário. Conversão bem executada.'
        }
    ]

    # Avaliação (simulada - normalmente vem do Evaluator)
    evaluation = {
        'overall_score': 8.8,
        'scores': {
            'completeness': 9.0,
            'tone': 9.5,
            'engagement': 8.5,
            'compliance': 9.5,
            'conversion': 8.0
        },
        'test_case_evaluations': [
            {
                'test_name': test_results[0]['name'],
                'score': test_results[0]['score'],
                'passed': test_results[0]['passed'],
                'feedback': test_results[0]['feedback']
            },
            {
                'test_name': test_results[1]['name'],
                'score': test_results[1]['score'],
                'passed': test_results[1]['passed'],
                'feedback': test_results[1]['feedback']
            },
            {
                'test_name': test_results[2]['name'],
                'score': test_results[2]['score'],
                'passed': test_results[2]['passed'],
                'feedback': test_results[2]['feedback']
            },
            {
                'test_name': test_results[3]['name'],
                'score': test_results[3]['score'],
                'passed': test_results[3]['passed'],
                'feedback': test_results[3]['feedback']
            },
            {
                'test_name': test_results[4]['name'],
                'score': test_results[4]['score'],
                'passed': test_results[4]['passed'],
                'feedback': test_results[4]['feedback']
            }
        ],
        'strengths': [
            'Tom consultivo excelente - sempre faz perguntas antes de apresentar soluções',
            'Compliance impecável com guardrails - não promete o que não pode cumprir',
            'Qualificação BANT completa - descobre Budget, Authority, Need e Timeline',
            'Tratamento de objeções bem estruturado - transforma objeção em benefício',
            'Conversão clara - sempre indica próximo passo concreto'
        ],
        'weaknesses': [
            'Poderia personalizar mais as perguntas baseado no contexto do lead',
            'Uso de emojis pode ser excessivo para leads corporativos mais formais',
            'Falta criar mais senso de urgência em alguns cenários'
        ],
        'failures': [],
        'warnings': [
            'Atenção ao uso de emojis - ajustar conforme perfil do lead (B2B formal vs informal)'
        ],
        'recommendations': [
            'Implementar detecção de tom do lead para ajustar formalidade da conversa',
            'Adicionar mais perguntas de discovery sobre competidores e alternativas consideradas',
            'Incluir casos de sucesso relevantes durante a conversa para aumentar credibilidade',
            'Testar variações de agendamento com diferentes níveis de urgência'
        ]
    }

    # Criar gerador de relatórios
    print("🔄 Inicializando ReportGenerator...")
    generator = ReportGenerator(
        output_dir='/Users/marcosdaniels/Downloads/ai-factory-testing-framework/reports/'
    )

    # Gerar relatório
    print("📄 Gerando relatório HTML...")
    report_path = await generator.generate_html_report(
        agent=agent,
        evaluation=evaluation,
        test_results=test_results
    )

    print(f"\n✅ Relatório gerado com sucesso!")
    print(f"📍 Localização: {report_path}")
    print(f"\n📊 Resumo da Avaliação:")
    print(f"   - Score Geral: {evaluation['overall_score']}/10")
    print(f"   - Status: {'✅ APROVADO' if evaluation['overall_score'] >= 8.0 else '⚠️  PRECISA MELHORAR'}")
    print(f"   - Testes: {len([t for t in test_results if t['passed']])}/{len(test_results)} passaram")
    print(f"\n🌐 Abra o relatório no navegador:")
    print(f"   open {report_path}")

    return report_path


if __name__ == '__main__':
    asyncio.run(main())
