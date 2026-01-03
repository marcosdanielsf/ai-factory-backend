"""
AI Factory Testing Framework - Report Generator
================================================

Gerador de relatórios HTML para testes de agentes IA.
Usa templates Jinja2 para criar relatórios visuais e informativos
com scores, gráficos e detalhes dos testes.

Features:
    - Relatórios HTML responsivos com TailwindCSS
    - Visualização de scores por dimensão
    - Lista de testes com feedback individual
    - Seções de strengths, weaknesses e recommendations
    - Suporte a templates customizados

Example:
    >>> from src import ReportGenerator
    >>> reporter = ReportGenerator(output_dir="./reports")
    >>> url = await reporter.generate_html_report(
    ...     agent=agent_data,
    ...     evaluation=evaluation_result,
    ...     test_results=test_results
    ... )
    >>> print(f"Report: {url}")

Environment Variables:
    REPORTS_OUTPUT_DIR: Diretório para salvar relatórios
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Gerador de relatórios HTML para testes de agentes.

    Usa templates Jinja2 para criar relatórios visuais e informativos.
    Suporta templates customizados e fallback inline.

    Attributes:
        output_dir (str): Diretório para salvar relatórios
        templates_dir (str): Diretório com templates Jinja2
        public_url_base (str): URL base para links públicos
        jinja_env (Environment): Ambiente Jinja2 configurado

    Example:
        >>> reporter = ReportGenerator(
        ...     output_dir="./reports",
        ...     public_url_base="https://reports.example.com"
        ... )
        >>> url = await reporter.generate_html_report(
        ...     agent=agent_data,
        ...     evaluation=evaluation_result,
        ...     test_results=test_results
        ... )
        >>> print(f"Report URL: {url}")
    """

    def __init__(
        self,
        output_dir: str = None,
        templates_dir: str = None,
        public_url_base: str = None
    ):
        """
        Inicializa o ReportGenerator.

        Args:
            output_dir: Diretório para salvar relatórios.
                Default: REPORTS_OUTPUT_DIR ou /mnt/user-data/outputs/test-reports/
            templates_dir: Diretório com templates Jinja2.
                Default: ../templates relativo ao módulo
            public_url_base: URL base para relatórios públicos.
                Se não definido, retorna caminho local.

        Example:
            >>> # Usando defaults
            >>> reporter = ReportGenerator()
            >>>
            >>> # Customizado
            >>> reporter = ReportGenerator(
            ...     output_dir="/var/reports",
            ...     public_url_base="https://cdn.example.com/reports"
            ... )
        """
        # Diretório de saída
        self.output_dir = output_dir or os.getenv(
            'REPORTS_OUTPUT_DIR',
            '/mnt/user-data/outputs/test-reports/'
        )

        # Criar diretório se não existir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Diretório de templates
        if templates_dir:
            self.templates_dir = templates_dir
        else:
            # Default: pasta templates no mesmo nível de src
            self.templates_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'templates'
            )

        # URL base para links públicos
        self.public_url_base = public_url_base

        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Adicionar filtros customizados
        self.jinja_env.filters['format_score'] = self._format_score
        self.jinja_env.filters['score_class'] = self._score_class
        self.jinja_env.filters['format_datetime'] = self._format_datetime
        self.jinja_env.filters['truncate_text'] = self._truncate_text

        logger.info(f"ReportGenerator initialized. Output: {self.output_dir}")

    async def generate_html_report(
        self,
        agent: Dict,
        evaluation: Dict,
        test_results: List[Dict]
    ) -> str:
        """
        Gera relatório HTML completo.

        Args:
            agent: Dados do agente
            evaluation: Resultado da avaliação (do Evaluator)
            test_results: Lista de resultados dos testes

        Returns:
            URL ou caminho do relatório gerado
        """
        logger.info(f"Generating report for agent: {agent.get('id', 'unknown')}")

        # Preparar contexto do template
        context = self._prepare_context(agent, evaluation, test_results)

        # Renderizar template
        try:
            template = self.jinja_env.get_template('report.html')
            html_content = template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            # Usar template inline como fallback
            html_content = self._generate_fallback_html(context)

        # Gerar nome do arquivo
        agent_id = agent.get('id', 'unknown')
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{agent_id[:8]}_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)

        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Report saved to: {filepath}")

        # Retornar URL ou caminho
        if self.public_url_base:
            return f"{self.public_url_base}/{filename}"

        return filepath

    def _prepare_context(
        self,
        agent: Dict,
        evaluation: Dict,
        test_results: List[Dict]
    ) -> Dict:
        """
        Prepara contexto completo para o template Jinja2.

        Combina dados do agente, avaliação e testes em um único
        dicionário pronto para renderização.

        Args:
            agent: Dict com dados do agente.
            evaluation: Dict com resultado da avaliação.
            test_results: Lista de resultados dos testes.

        Returns:
            Dict com todos os dados formatados para o template.
        """
        # Extrair informações do agente
        agent_name = agent.get('name', 'Agente Desconhecido')
        agent_version = agent.get('version', 1)
        agent_id = agent.get('id', 'N/A')

        # Extrair scores
        scores = evaluation.get('scores', {})
        overall_score = evaluation.get('overall_score', 0)

        # Combinar avaliações por teste com resultados originais
        test_evaluations = evaluation.get('test_case_evaluations', [])
        combined_tests = []

        for i, result in enumerate(test_results):
            # Encontrar avaliação correspondente
            eval_data = {}
            for te in test_evaluations:
                if te.get('test_name') == result.get('name'):
                    eval_data = te
                    break

            # Se não encontrou, usar dados do resultado
            if not eval_data and i < len(test_evaluations):
                eval_data = test_evaluations[i]

            combined_tests.append({
                'name': result.get('name', f'Test {i+1}'),
                'input': result.get('input', ''),
                'agent_response': result.get('agent_response', ''),
                'expected_behavior': result.get('expected_behavior', ''),
                'score': eval_data.get('score', result.get('score', 0)),
                'passed': eval_data.get('passed', result.get('passed', False)),
                'feedback': eval_data.get('feedback', result.get('feedback', ''))
            })

        # Estatísticas
        passed_count = sum(1 for t in combined_tests if t.get('passed'))
        failed_count = len(combined_tests) - passed_count

        return {
            # Agente
            'agent_name': agent_name,
            'agent_version': agent_version,
            'agent_id': agent_id,
            'agent_description': agent.get('description', ''),

            # Scores
            'overall_score': overall_score,
            'scores': scores,
            'score_breakdown': [
                {'name': 'Completeness', 'key': 'completeness', 'weight': '25%', 'score': scores.get('completeness', 0)},
                {'name': 'Tone', 'key': 'tone', 'weight': '20%', 'score': scores.get('tone', 0)},
                {'name': 'Engagement', 'key': 'engagement', 'weight': '20%', 'score': scores.get('engagement', 0)},
                {'name': 'Compliance', 'key': 'compliance', 'weight': '20%', 'score': scores.get('compliance', 0)},
                {'name': 'Conversion', 'key': 'conversion', 'weight': '15%', 'score': scores.get('conversion', 0)},
            ],

            # Testes
            'test_results': combined_tests,
            'total_tests': len(combined_tests),
            'passed_tests': passed_count,
            'failed_tests': failed_count,
            'pass_rate': round(passed_count / len(combined_tests) * 100, 1) if combined_tests else 0,

            # Feedback
            'strengths': evaluation.get('strengths', []),
            'weaknesses': evaluation.get('weaknesses', []),
            'failures': evaluation.get('failures', []),
            'warnings': evaluation.get('warnings', []),
            'recommendations': evaluation.get('recommendations', []),

            # Meta
            'generated_at': datetime.utcnow(),
            'evaluator_model': 'Claude Opus',
            'framework_version': '1.0.0',
            'approved': overall_score >= 8.0
        }

    def _generate_fallback_html(self, context: Dict) -> str:
        """
        Gera HTML inline quando template Jinja2 não está disponível.

        Template completo com TailwindCSS incluído via CDN.
        Usado como fallback quando o arquivo template não existe.

        Args:
            context: Dict com dados preparados por _prepare_context.

        Returns:
            String HTML completa pronta para salvar.
        """
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {context['agent_name']} v{context['agent_version']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .score-bar {{ transition: width 0.5s ease-in-out; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-5xl">
        <!-- Header -->
        <header class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div class="flex justify-between items-start">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">{context['agent_name']}</h1>
                    <p class="text-gray-500">Version {context['agent_version']} | ID: {context['agent_id'][:8]}...</p>
                </div>
                <div class="text-right">
                    <div class="text-4xl font-bold {'text-green-600' if context['overall_score'] >= 8 else 'text-yellow-600' if context['overall_score'] >= 6 else 'text-red-600'}">
                        {context['overall_score']:.1f}
                    </div>
                    <div class="text-sm text-gray-500">Overall Score</div>
                    <span class="inline-block mt-2 px-3 py-1 rounded-full text-sm font-medium {'bg-green-100 text-green-800' if context['approved'] else 'bg-red-100 text-red-800'}">
                        {'APPROVED' if context['approved'] else 'NEEDS IMPROVEMENT'}
                    </span>
                </div>
            </div>
        </header>

        <!-- Score Breakdown -->
        <section class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 class="text-lg font-semibold mb-4">Score Breakdown</h2>
            <div class="space-y-4">
                {''.join(self._render_score_bar(s) for s in context['score_breakdown'])}
            </div>
        </section>

        <!-- Test Results Summary -->
        <section class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 class="text-lg font-semibold mb-4">Test Results</h2>
            <div class="grid grid-cols-3 gap-4 mb-6">
                <div class="text-center p-4 bg-gray-50 rounded-lg">
                    <div class="text-2xl font-bold">{context['total_tests']}</div>
                    <div class="text-sm text-gray-500">Total Tests</div>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <div class="text-2xl font-bold text-green-600">{context['passed_tests']}</div>
                    <div class="text-sm text-gray-500">Passed</div>
                </div>
                <div class="text-center p-4 bg-red-50 rounded-lg">
                    <div class="text-2xl font-bold text-red-600">{context['failed_tests']}</div>
                    <div class="text-sm text-gray-500">Failed</div>
                </div>
            </div>

            <!-- Test Cases -->
            <div class="space-y-4">
                {''.join(self._render_test_case(t) for t in context['test_results'])}
            </div>
        </section>

        <!-- Strengths & Weaknesses -->
        <div class="grid grid-cols-2 gap-6 mb-6">
            <section class="bg-white rounded-lg shadow-sm p-6">
                <h2 class="text-lg font-semibold mb-4 text-green-700">Strengths</h2>
                <ul class="space-y-2">
                    {''.join(f'<li class="flex items-start"><span class="text-green-500 mr-2">+</span>{s}</li>' for s in context['strengths']) or '<li class="text-gray-400">No strengths identified</li>'}
                </ul>
            </section>
            <section class="bg-white rounded-lg shadow-sm p-6">
                <h2 class="text-lg font-semibold mb-4 text-red-700">Weaknesses</h2>
                <ul class="space-y-2">
                    {''.join(f'<li class="flex items-start"><span class="text-red-500 mr-2">-</span>{w}</li>' for w in context['weaknesses']) or '<li class="text-gray-400">No weaknesses identified</li>'}
                </ul>
            </section>
        </div>

        <!-- Recommendations -->
        {self._render_recommendations(context)}

        <!-- Footer -->
        <footer class="text-center text-gray-400 text-sm mt-8 pb-8">
            <p>Generated by AI Factory Testing Framework v{context['framework_version']}</p>
            <p>Evaluated by {context['evaluator_model']} | {context['generated_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </footer>
    </div>
</body>
</html>"""

    def _render_score_bar(self, score_item: Dict) -> str:
        """Renderiza barra de score individual"""
        score = score_item['score']
        color = 'bg-green-500' if score >= 8 else 'bg-yellow-500' if score >= 6 else 'bg-red-500'
        width = score * 10

        return f"""
        <div class="flex items-center">
            <div class="w-32 text-sm font-medium">{score_item['name']}</div>
            <div class="flex-1 mx-4">
                <div class="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full score-bar {color}" style="width: {width}%"></div>
                </div>
            </div>
            <div class="w-16 text-right">
                <span class="font-semibold">{score:.1f}</span>
                <span class="text-gray-400 text-sm">({score_item['weight']})</span>
            </div>
        </div>"""

    def _render_test_case(self, test: Dict) -> str:
        """Renderiza caso de teste individual"""
        status_class = 'border-green-200 bg-green-50' if test['passed'] else 'border-red-200 bg-red-50'
        status_badge = '<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">PASSED</span>' if test['passed'] else '<span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">FAILED</span>'

        return f"""
        <div class="border rounded-lg p-4 {status_class}">
            <div class="flex justify-between items-start mb-3">
                <h3 class="font-medium">{test['name']}</h3>
                <div class="flex items-center space-x-2">
                    <span class="text-lg font-semibold">{test['score']:.1f}</span>
                    {status_badge}
                </div>
            </div>
            <div class="space-y-2 text-sm">
                <div>
                    <span class="font-medium text-gray-600">Input:</span>
                    <span class="ml-2">{test['input']}</span>
                </div>
                <div>
                    <span class="font-medium text-gray-600">Agent Response:</span>
                    <p class="ml-2 mt-1 p-2 bg-white rounded border">{test['agent_response'][:500]}{'...' if len(str(test['agent_response'])) > 500 else ''}</p>
                </div>
                <div>
                    <span class="font-medium text-gray-600">Feedback:</span>
                    <span class="ml-2">{test['feedback']}</span>
                </div>
            </div>
        </div>"""

    def _render_recommendations(self, context: Dict) -> str:
        """Renderiza seção de recomendações"""
        if not context['recommendations'] and not context['failures'] and not context['warnings']:
            return ""

        items = []

        for f in context['failures']:
            items.append(f'<li class="flex items-start"><span class="text-red-500 mr-2 font-bold">!</span><span class="text-red-700">{f}</span></li>')

        for w in context['warnings']:
            items.append(f'<li class="flex items-start"><span class="text-yellow-500 mr-2 font-bold">!</span><span class="text-yellow-700">{w}</span></li>')

        for r in context['recommendations']:
            items.append(f'<li class="flex items-start"><span class="text-blue-500 mr-2">></span>{r}</li>')

        return f"""
        <section class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 class="text-lg font-semibold mb-4">Recommendations & Issues</h2>
            <ul class="space-y-2">
                {''.join(items)}
            </ul>
        </section>"""

    # Template filters
    @staticmethod
    def _format_score(score: float) -> str:
        """Formata score para exibição"""
        return f"{score:.1f}"

    @staticmethod
    def _score_class(score: float) -> str:
        """Retorna classe CSS baseada no score"""
        if score >= 8:
            return "text-green-600"
        elif score >= 6:
            return "text-yellow-600"
        else:
            return "text-red-600"

    @staticmethod
    def _format_datetime(dt) -> str:
        """Formata datetime"""
        if isinstance(dt, str):
            return dt
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _truncate_text(text: str, length: int = 200) -> str:
        """Trunca texto"""
        if len(text) <= length:
            return text
        return text[:length] + "..."


# Função helper para uso rápido
async def generate_report(
    agent: Dict,
    evaluation: Dict,
    test_results: List[Dict],
    output_dir: str = None
) -> str:
    """
    Gera relatório HTML de forma simplificada.

    Função wrapper que cria ReportGenerator e gera relatório
    em uma única chamada.

    Args:
        agent: Dict com dados do agente.
        evaluation: Dict com resultado da avaliação.
        test_results: Lista de resultados dos testes.
        output_dir: Diretório para salvar (opcional).

    Returns:
        URL ou caminho do relatório gerado.

    Example:
        >>> url = await generate_report(
        ...     agent={"id": "uuid", "name": "SDR"},
        ...     evaluation={"overall_score": 8.5, ...},
        ...     test_results=[...],
        ...     output_dir="./reports"
        ... )
        >>> print(f"Report: {url}")
    """
    generator = ReportGenerator(output_dir=output_dir)
    return await generator.generate_html_report(agent, evaluation, test_results)
