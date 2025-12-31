"""
AI Factory Testing Framework
============================

Framework para testar e avaliar agentes de IA usando LLM-as-Judge.

Components:
- SupabaseClient: Cliente para interacao com banco de dados
- Evaluator: Avalia agentes usando Claude Opus como juiz
- ReportGenerator: Gera relatorios HTML
- TestRunner: Orquestra todo o processo de testes

Usage:
    from src import TestRunner, Evaluator, ReportGenerator, SupabaseClient

    # Inicializar componentes
    supabase = SupabaseClient()
    evaluator = Evaluator()
    reporter = ReportGenerator()

    # Criar runner
    runner = TestRunner(
        supabase_client=supabase,
        evaluator=evaluator,
        report_generator=reporter
    )

    # Executar testes
    result = await runner.run_tests("agent-uuid-here")
"""

from .supabase_client import SupabaseClient
from .evaluator import Evaluator
from .report_generator import ReportGenerator
from .test_runner import TestRunner, run_quick_test

__version__ = "1.0.0"
__all__ = [
    "SupabaseClient",
    "Evaluator",
    "ReportGenerator",
    "TestRunner",
    "run_quick_test"
]
