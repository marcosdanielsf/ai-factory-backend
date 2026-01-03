"""
Custom exception hierarchy for AI Factory Backend.

Provides structured error handling with:
- Hierarchical exception types for different error categories
- HTTP status code mapping
- Error codes for client identification
- Contextual details without exposing internals
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes for API responses."""

    # General errors (1xxx)
    INTERNAL_ERROR = "ERR_1000"
    VALIDATION_ERROR = "ERR_1001"
    NOT_FOUND = "ERR_1002"

    # Authentication/Authorization (2xxx)
    AUTHENTICATION_FAILED = "ERR_2000"
    INVALID_API_KEY = "ERR_2001"
    PERMISSION_DENIED = "ERR_2002"

    # Database errors (3xxx)
    DATABASE_ERROR = "ERR_3000"
    DATABASE_CONNECTION = "ERR_3001"
    DATABASE_QUERY = "ERR_3002"
    DATABASE_TIMEOUT = "ERR_3003"

    # External API errors (4xxx)
    EXTERNAL_API_ERROR = "ERR_4000"
    ANTHROPIC_API_ERROR = "ERR_4001"
    ANTHROPIC_RATE_LIMIT = "ERR_4002"
    ANTHROPIC_TIMEOUT = "ERR_4003"
    SUPABASE_ERROR = "ERR_4010"

    # Rate limiting (5xxx)
    RATE_LIMIT_EXCEEDED = "ERR_5000"

    # Timeout errors (6xxx)
    TIMEOUT_ERROR = "ERR_6000"
    REQUEST_TIMEOUT = "ERR_6001"
    OPERATION_TIMEOUT = "ERR_6002"


class AIFactoryError(Exception):
    """
    Base exception for all AI Factory errors.

    Attributes:
        message: Human-readable error message
        error_code: Standardized error code for client handling
        status_code: HTTP status code to return
        details: Additional context (not exposed to client in production)
        original_error: The underlying exception, if any
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            "error": True,
            "code": self.error_code.value,
            "message": self.message,
        }
        if include_details and self.details:
            result["details"] = self.details
        return result

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"


# =============================================================================
# Database Errors
# =============================================================================

class DatabaseError(AIFactoryError):
    """Base exception for database-related errors."""

    def __init__(
        self,
        message: str = "Database operation failed",
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=503,
            details=details,
            original_error=original_error,
        )


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to database."""

    def __init__(
        self,
        message: str = "Failed to connect to database",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_CONNECTION,
            details=details,
            original_error=original_error,
        )


class DatabaseQueryError(DatabaseError):
    """Database query failed."""

    def __init__(
        self,
        message: str = "Database query failed",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_QUERY,
            details=details,
            original_error=original_error,
        )


# =============================================================================
# External API Errors
# =============================================================================

class ExternalAPIError(AIFactoryError):
    """Base exception for external API errors."""

    def __init__(
        self,
        message: str = "External API request failed",
        error_code: ErrorCode = ErrorCode.EXTERNAL_API_ERROR,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details,
            original_error=original_error,
        )


class AnthropicAPIError(ExternalAPIError):
    """Error from Anthropic Claude API."""

    def __init__(
        self,
        message: str = "Anthropic API request failed",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.ANTHROPIC_API_ERROR,
            status_code=502,
            details=details,
            original_error=original_error,
        )


class AnthropicRateLimitError(AnthropicAPIError):
    """Rate limited by Anthropic API."""

    def __init__(
        self,
        message: str = "Anthropic API rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        details = details or {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            details=details,
            original_error=original_error,
        )
        self.error_code = ErrorCode.ANTHROPIC_RATE_LIMIT
        self.status_code = 429
        self.retry_after = retry_after


# =============================================================================
# Validation Errors
# =============================================================================

class ValidationError(AIFactoryError):
    """Request validation failed."""

    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details,
            original_error=original_error,
        )


# =============================================================================
# Authentication Errors
# =============================================================================

class AuthenticationError(AIFactoryError):
    """Authentication failed."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: ErrorCode = ErrorCode.AUTHENTICATION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401,
            details=details,
            original_error=original_error,
        )


class InvalidAPIKeyError(AuthenticationError):
    """Invalid or missing API key."""

    def __init__(
        self,
        message: str = "Invalid or missing API key",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_API_KEY,
            details=details,
            original_error=original_error,
        )


# =============================================================================
# Rate Limiting
# =============================================================================

class RateLimitError(AIFactoryError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        details = details or {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details=details,
            original_error=original_error,
        )
        self.retry_after = retry_after


# =============================================================================
# Timeout Errors
# =============================================================================

class TimeoutError(AIFactoryError):
    """Operation timed out."""

    def __init__(
        self,
        message: str = "Operation timed out",
        error_code: ErrorCode = ErrorCode.TIMEOUT_ERROR,
        timeout_seconds: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        details = details or {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=504,
            details=details,
            original_error=original_error,
        )


# =============================================================================
# Not Found Errors
# =============================================================================

class NotFoundError(AIFactoryError):
    """Resource not found."""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        details = details or {}
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details,
            original_error=original_error,
        )
