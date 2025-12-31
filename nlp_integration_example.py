#!/usr/bin/env python3
"""
NLP Integration Example - Report Generator
==========================================
Demonstra como integrar análise NLP com geração de relatórios.

Este exemplo mostra como avaliar agentes usando técnicas de NLP:
- Sentiment analysis das respostas
- Named Entity Recognition (NER)
- Text quality metrics (coerência, fluência)
- Toxicity detection
- Similarity comparison
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from report_generator import ReportGenerator


class NLPAnalyzer:
    """
    Analisador NLP para avaliar qualidade de respostas de agentes.

    Em produção, usar:
    - transformers (BERT, RoBERTa)
    - spaCy para NER e parsing
    - sentence-transformers para embeddings
    - Detoxify para toxicity
    """

    def analyze_response(self, agent_response: str, input_text: str) -> Dict:
        """
        Analisa resposta do agente usando técnicas de NLP.

        Returns:
            Dict com métricas NLP
        """
        # SIMULAÇÃO - Em produção, usar modelos reais

        analysis = {
            'sentiment': {
                'polarity': 0.8,  # -1 (negativo) a 1 (positivo)
                'label': 'positive',
                'confidence': 0.92
            },
            'entities': [
                {'text': 'BANT', 'label': 'CONCEPT', 'confidence': 0.95},
                {'text': 'reunião', 'label': 'EVENT', 'confidence': 0.88}
            ],
            'quality_metrics': {
                'fluency': 0.87,       # Fluência do texto
                'coherence': 0.91,     # Coerência com input
                'professionalism': 0.89, # Tom profissional
                'empathy': 0.85,       # Empatia detectada
                'toxicity': 0.02       # Toxicidade (0-1, menor é melhor)
            },
            'text_stats': {
                'word_count': len(agent_response.split()),
                'sentence_count': agent_response.count('.') + agent_response.count('!') + agent_response.count('?'),
                'avg_sentence_length': len(agent_response.split()) / max(1, agent_response.count('.')),
                'has_questions': '?' in agent_response,
                'has_emojis': any(char in agent_response for char in '😊🎉😅')
            },
            'semantic_similarity': 0.78  # Similaridade com resposta ideal (0-1)
        }

        return analysis


async def main():
    """Demonstra uso de NLP + Report Generator."""

    print("\n" + "="*70)
    print("  NLP INTEGRATION - AGENT QUALITY ANALYSIS")
    print("="*70 + "\n")

    # ========================================
    # AGENTE A SER ANALISADO
    # ========================================
    agent = {
        'id': 'nlp-agent-001',
        'name': 'Carlos - SDR Tech Sales',
        'version': 1,
        'description': 'Agente SDR especializado em vendas B2B de soluções tecnológicas.',
        'system_prompt': 'Agente de vendas consultivo focado em BANT discovery.'
    }

    # ========================================
    # CASOS DE TESTE COM ANÁLISE NLP
    # ========================================
    print("🔬 Analisando respostas com técnicas de NLP...")
    print("-" * 70)

    nlp_analyzer = NLPAnalyzer()

    test_cases = [
        {
            'name': 'Lead B2B - Descoberta inicial',
            'input': 'Olá, estou interessado em soluções de CRM para minha empresa.',
            'agent_response': """Olá! Ótimo saber do seu interesse em CRM!

Antes de te apresentar nossas soluções, vou te fazer algumas perguntas para entender melhor sua necessidade:

1. Quantos usuários vocês têm na equipe de vendas?
2. Vocês já usam algum CRM hoje? Se sim, qual?
3. Quais os principais desafios que vocês enfrentam atualmente?
4. Você é o decisor dessa compra ou precisa validar com alguém?

Assim consigo te indicar a melhor solução! 😊"""
        },
        {
            'name': 'Lead pergunta sobre preço',
            'input': 'Qual o valor do plano empresarial?',
            'agent_response': """Entendo que preço é importante para você!

O investimento varia de acordo com número de usuários e módulos que você precisa.

Antes de te passar valores, posso te perguntar:

1. Quantos usuários vocês precisam?
2. Vocês têm orçamento já aprovado para CRM esse ano?
3. Quando gostariam de começar a usar?

Com essas informações, consigo te apresentar a opção mais adequada e já com o investimento exato."""
        },
        {
            'name': 'Lead com objeção',
            'input': 'Está muito caro para a gente no momento.',
            'agent_response': """Entendo perfeitamente sua preocupação com investimento.

Deixa eu te fazer uma pergunta: quando você diz "muito caro", você está comparando com:
a) Outros CRMs que pesquisou?
b) O orçamento que vocês têm disponível?
c) O retorno que esperam ter?

Pergunto porque muitos clientes inicialmente acham caro, mas quando calculam o ROI (redução de tempo, aumento de conversão, etc), veem que se paga em poucos meses.

Podemos fazer esse cálculo junto? Posso te mostrar casos de empresas similares à sua."""
        }
    ]

    # Analisar cada resposta
    test_results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 Caso {i}/{len(test_cases)}: {test['name']}")

        # Análise NLP
        nlp_analysis = nlp_analyzer.analyze_response(
            agent_response=test['agent_response'],
            input_text=test['input']
        )

        # Calcular score baseado em métricas NLP
        quality = nlp_analysis['quality_metrics']
        score = (
            quality['fluency'] * 0.20 +
            quality['coherence'] * 0.25 +
            quality['professionalism'] * 0.20 +
            quality['empathy'] * 0.20 +
            (1 - quality['toxicity']) * 0.15
        ) * 10

        # Determinar se passou
        passed = score >= 7.0 and quality['toxicity'] < 0.1

        # Gerar feedback baseado em NLP
        feedback_parts = []

        if nlp_analysis['sentiment']['label'] == 'positive':
            feedback_parts.append(f"✓ Tom positivo detectado (confiança: {nlp_analysis['sentiment']['confidence']:.0%})")

        if quality['empathy'] >= 0.80:
            feedback_parts.append(f"✓ Alta empatia detectada ({quality['empathy']:.0%})")
        elif quality['empathy'] < 0.60:
            feedback_parts.append(f"⚠ Baixa empatia detectada ({quality['empathy']:.0%})")

        if quality['coherence'] >= 0.85:
            feedback_parts.append(f"✓ Excelente coerência com input ({quality['coherence']:.0%})")

        if nlp_analysis['text_stats']['has_questions']:
            feedback_parts.append("✓ Faz perguntas de discovery")
        else:
            feedback_parts.append("⚠ Não fez perguntas de qualificação")

        if quality['toxicity'] > 0.05:
            feedback_parts.append(f"⚠ Toxicidade detectada ({quality['toxicity']:.0%})")

        # Entidades encontradas
        if nlp_analysis['entities']:
            entities_str = ', '.join([e['text'] for e in nlp_analysis['entities']])
            feedback_parts.append(f"ℹ️ Entidades: {entities_str}")

        feedback = ' | '.join(feedback_parts)

        test_result = {
            'name': test['name'],
            'input': test['input'],
            'agent_response': test['agent_response'],
            'expected_behavior': 'Resposta consultiva com discovery e empatia',
            'score': round(score, 1),
            'passed': passed,
            'feedback': feedback,
            'nlp_analysis': nlp_analysis  # Manter para referência
        }

        test_results.append(test_result)

        # Log análise
        print(f"   Sentiment: {nlp_analysis['sentiment']['label']} ({nlp_analysis['sentiment']['confidence']:.0%})")
        print(f"   Fluency: {quality['fluency']:.0%} | Coherence: {quality['coherence']:.0%}")
        print(f"   Empathy: {quality['empathy']:.0%} | Professionalism: {quality['professionalism']:.0%}")
        print(f"   Score: {score:.1f}/10 | Status: {'✅ PASS' if passed else '❌ FAIL'}")

    # ========================================
    # AVALIAÇÃO CONSOLIDADA
    # ========================================
    print("\n" + "-" * 70)
    print("📈 Consolidando avaliação NLP...\n")

    # Calcular scores agregados
    avg_fluency = sum(t['nlp_analysis']['quality_metrics']['fluency'] for t in test_results) / len(test_results)
    avg_coherence = sum(t['nlp_analysis']['quality_metrics']['coherence'] for t in test_results) / len(test_results)
    avg_professionalism = sum(t['nlp_analysis']['quality_metrics']['professionalism'] for t in test_results) / len(test_results)
    avg_empathy = sum(t['nlp_analysis']['quality_metrics']['empathy'] for t in test_results) / len(test_results)
    avg_toxicity = sum(t['nlp_analysis']['quality_metrics']['toxicity'] for t in test_results) / len(test_results)

    overall_score = (
        avg_fluency * 0.20 +
        avg_coherence * 0.25 +
        avg_professionalism * 0.20 +
        avg_empathy * 0.20 +
        (1 - avg_toxicity) * 0.15
    ) * 10

    evaluation = {
        'overall_score': round(overall_score, 1),
        'scores': {
            'fluency': round(avg_fluency * 10, 1),
            'coherence': round(avg_coherence * 10, 1),
            'professionalism': round(avg_professionalism * 10, 1),
            'empathy': round(avg_empathy * 10, 1),
            'safety': round((1 - avg_toxicity) * 10, 1)
        },
        'test_case_evaluations': [
            {
                'test_name': t['name'],
                'score': t['score'],
                'passed': t['passed'],
                'feedback': t['feedback']
            }
            for t in test_results
        ],
        'strengths': [
            'Tom consistentemente positivo e consultivo',
            'Alta coerência nas respostas (média: {:.0%})'.format(avg_coherence),
            'Profissionalismo mantido em todos os casos',
            'Zero toxicidade detectada' if avg_toxicity < 0.05 else 'Baixa toxicidade',
            'Sempre faz perguntas de discovery'
        ],
        'weaknesses': [
            'Uso de emojis pode ser excessivo para clientes formais',
            'Respostas um pouco longas (média: {:.0f} palavras)'.format(
                sum(t['nlp_analysis']['text_stats']['word_count'] for t in test_results) / len(test_results)
            )
        ] if avg_professionalism < 0.90 else [],
        'failures': [],
        'warnings': [
            'Monitorar uso de emojis conforme perfil do lead'
        ] if any(t['nlp_analysis']['text_stats']['has_emojis'] for t in test_results) else [],
        'recommendations': [
            'Implementar detecção de tom do lead para ajustar formalidade',
            'Variar comprimento de resposta baseado em contexto',
            'A/B test respostas com e sem emojis',
            'Adicionar mais exemplos concretos e cases de sucesso'
        ]
    }

    print(f"Overall Score (NLP): {evaluation['overall_score']}/10")
    print(f"Status: {'✅ APPROVED' if evaluation['overall_score'] >= 8.0 else '⚠️ NEEDS IMPROVEMENT'}")

    # ========================================
    # GERAR RELATÓRIO
    # ========================================
    print("\n" + "-" * 70)
    print("📄 Gerando relatório HTML com análise NLP...\n")

    generator = ReportGenerator(
        output_dir=str(Path(__file__).parent / 'reports')
    )

    report_path = await generator.generate_html_report(
        agent=agent,
        evaluation=evaluation,
        test_results=test_results
    )

    print(f"✅ Relatório gerado: {Path(report_path).name}")
    print(f"📍 {report_path}")

    # ========================================
    # SUMÁRIO
    # ========================================
    print("\n" + "="*70)
    print("  SUMÁRIO DA ANÁLISE NLP")
    print("="*70)
    print(f"Agent: {agent['name']}")
    print(f"Casos testados: {len(test_results)}")
    print(f"Aprovados: {sum(1 for t in test_results if t['passed'])}/{len(test_results)}")
    print()
    print("Métricas NLP (médias):")
    print(f"  - Fluency: {avg_fluency:.0%}")
    print(f"  - Coherence: {avg_coherence:.0%}")
    print(f"  - Professionalism: {avg_professionalism:.0%}")
    print(f"  - Empathy: {avg_empathy:.0%}")
    print(f"  - Toxicity: {avg_toxicity:.2%}")
    print()
    print(f"Overall Score: {evaluation['overall_score']}/10")
    print(f"Status: {'APPROVED ✓' if evaluation['overall_score'] >= 8.0 else 'NEEDS IMPROVEMENT ⚠'}")
    print()
    print(f"🌐 Abrir relatório:")
    print(f"   open {report_path}")
    print("="*70 + "\n")

    return report_path


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   NLP INTEGRATION EXAMPLE                                        ║
║   AI Factory Testing Framework                                   ║
║                                                                  ║
║   Este exemplo demonstra como integrar análise NLP avançada     ║
║   com o Report Generator.                                        ║
║                                                                  ║
║   Técnicas demonstradas:                                         ║
║   • Sentiment Analysis                                           ║
║   • Named Entity Recognition (NER)                               ║
║   • Text Quality Metrics (fluency, coherence)                    ║
║   • Toxicity Detection                                           ║
║   • Semantic Similarity                                          ║
║                                                                  ║
║   NOTA: Exemplo usa valores simulados.                           ║
║   Em produção, usar transformers/spaCy reais.                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

    asyncio.run(main())
