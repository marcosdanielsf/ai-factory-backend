"""
AI Factory Testing Framework
============================

Framework para testar e avaliar agentes de IA usando LLM-as-Judge.
Inclui retry logic, logging estruturado e error handling robusto.

Components:
- SupabaseClient: Cliente para interacao com banco de dados (com retry)
- Evaluator: Avalia agentes usando Claude Opus como juiz (com retry)
- ReportGenerator: Gera relatorios HTML
- TestRunner: Orquestra todo o processo de testes

Core:
- exceptions: Custom exception hierarchy
- logging_config: Structured logging with correlation IDs
- retry: Retry decorators for external APIs
- middleware: FastAPI middleware for request tracking
- responses: Standardized API response models

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

# Core modules
from .core.exceptions import (
    AIFactoryError,
    DatabaseError,
    ExternalAPIError,
    AnthropicAPIError,
    ValidationError,
    NotFoundError,
)
from .core.logging_config import setup_logging, get_logger, LogContext
from .core.retry import with_retry, ANTHROPIC_RETRY_CONFIG, SUPABASE_RETRY_CONFIG

__version__ = "1.1.0"
__all__ = [
    # Main components
    "SupabaseClient",
    "Evaluator",
    "ReportGenerator",
    "TestRunner",
    "run_quick_test",
    # Core - Exceptions
    "AIFactoryError",
    "DatabaseError",
    "ExternalAPIError",
    "AnthropicAPIError",
    "ValidationError",
    "NotFoundError",
    # Core - Logging
    "setup_logging",
    "get_logger",
    "LogContext",
    # Core - Retry
    "with_retry",
    "ANTHROPIC_RETRY_CONFIG",
    "SUPABASE_RETRY_CONFIG",
]
