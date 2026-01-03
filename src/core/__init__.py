"""
AI Factory Core Infrastructure
==============================

Módulos de infraestrutura para:
- Error handling centralizado
- Retry logic com tenacity
- Logging estruturado (JSON)
- Request context/tracing
"""

from .errors import (
    AIFactoryError,
    DatabaseError,
    ExternalServiceError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    error_handler,
    handle_supabase_error,
    handle_anthropic_error,
)

from .retry import (
    retry_with_backoff,
    retry_database,
    retry_external_api,
    RetryConfig,
)

from .logging import (
    get_logger,
    setup_logging,
    LogContext,
    log_operation,
    log_request,
    log_response,
)

from .context import (
    RequestContext,
    RequestContextManager,
    get_request_id,
    set_request_context,
    get_request_context,
    extract_context_from_request,
    add_context_to_response,
)

__all__ = [
    # Errors
    "AIFactoryError",
    "DatabaseError",
    "ExternalServiceError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "error_handler",
    "handle_supabase_error",
    "handle_anthropic_error",
    # Retry
    "retry_with_backoff",
    "retry_database",
    "retry_external_api",
    "RetryConfig",
    # Logging
    "get_logger",
    "setup_logging",
    "LogContext",
    "log_operation",
    "log_request",
    "log_response",
    # Context
    "RequestContext",
    "RequestContextManager",
    "get_request_id",
    "set_request_context",
    "get_request_context",
    "extract_context_from_request",
    "add_context_to_response",
]
