"""
Core module for AI Factory Backend.

Provides centralized error handling, logging, retry logic, and middleware.
"""

from .exceptions import (
    AIFactoryError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    ExternalAPIError,
    AnthropicAPIError,
    AnthropicRateLimitError,
    ValidationError,
    AuthenticationError,
    InvalidAPIKeyError,
    RateLimitError,
    TimeoutError,
    NotFoundError,
    ErrorCode,
)
from .logging_config import setup_logging, get_logger, LogContext, Timer
from .retry import (
    with_retry,
    RetryConfig,
    ANTHROPIC_RETRY_CONFIG,
    SUPABASE_RETRY_CONFIG,
    HTTP_RETRY_CONFIG,
    retry_anthropic,
    retry_supabase,
    retry_http,
)
from .responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    HealthResponse,
    BatchJobResponse,
    success,
    error,
    health,
    batch_job,
    paginated,
)

__all__ = [
    # Exceptions
    "AIFactoryError",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "ExternalAPIError",
    "AnthropicAPIError",
    "AnthropicRateLimitError",
    "ValidationError",
    "AuthenticationError",
    "InvalidAPIKeyError",
    "RateLimitError",
    "TimeoutError",
    "NotFoundError",
    "ErrorCode",
    # Logging
    "setup_logging",
    "get_logger",
    "LogContext",
    "Timer",
    # Retry
    "with_retry",
    "RetryConfig",
    "ANTHROPIC_RETRY_CONFIG",
    "SUPABASE_RETRY_CONFIG",
    "HTTP_RETRY_CONFIG",
    "retry_anthropic",
    "retry_supabase",
    "retry_http",
    # Responses
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "HealthResponse",
    "BatchJobResponse",
    "success",
    "error",
    "health",
    "batch_job",
    "paginated",
]
