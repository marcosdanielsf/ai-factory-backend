"""
AI Factory - Centralized Error Handling
=======================================

Hierarquia de exceções customizadas e handlers para:
- Erros de banco de dados (Supabase)
- Erros de APIs externas (Anthropic, etc)
- Validação
- Rate limiting
- Timeouts
"""

import functools
import traceback
from typing import Optional, Dict, Any, Callable, TypeVar, Type
from enum import Enum
from datetime import datetime

# Type var para decorators
T = TypeVar('T')


class ErrorSeverity(Enum):
    """Severidade do erro para logging/alertas"""
    LOW = "low"           # Não impacta operação
    MEDIUM = "medium"     # Impacta parcialmente
    HIGH = "high"         # Impacta funcionalidade
    CRITICAL = "critical" # Sistema instável


class ErrorCategory(Enum):
    """Categoria do erro para métricas"""
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    INTERNAL = "internal"
    NETWORK = "network"


class AIFactoryError(Exception):
    """
    Base exception para todos os erros do AI Factory.

    Attributes:
        message: Mensagem de erro
        code: Código de erro único (ex: "DB001", "API002")
        category: Categoria do erro
        severity: Severidade do erro
        details: Dict com detalhes adicionais
        original_error: Exceção original (se houver)
        request_id: ID da requisição (para tracing)
        timestamp: Momento do erro
    """

    def __init__(
        self,
        message: str,
        code: str = "ERR000",
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.original_error = original_error
        self.request_id = request_id
        self.timestamp = datetime.utcnow().isoformat()

        # Captura stack trace se houver erro original
        if original_error:
            self.details['original_traceback'] = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict para logging/resposta"""
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "category": self.category.value,
                "severity": self.severity.value,
                "timestamp": self.timestamp,
                "request_id": self.request_id,
                "details": self.details,
            }
        }

    def to_response(self, include_details: bool = False) -> Dict[str, Any]:
        """Converte para resposta HTTP (sem info sensível)"""
        response = {
            "error": {
                "message": self.message,
                "code": self.code,
                "timestamp": self.timestamp,
            }
        }
        if self.request_id:
            response["error"]["request_id"] = self.request_id
        if include_details and self.details:
            # Remove info sensível
            safe_details = {
                k: v for k, v in self.details.items()
                if k not in ['original_traceback', 'credentials', 'api_key']
            }
            if safe_details:
                response["error"]["details"] = safe_details
        return response

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class DatabaseError(AIFactoryError):
    """Erros relacionados ao banco de dados (Supabase)"""

    def __init__(
        self,
        message: str,
        code: str = "DB001",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table

        super().__init__(
            message=message,
            code=code,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )


class ExternalServiceError(AIFactoryError):
    """Erros de APIs externas (Anthropic, etc)"""

    def __init__(
        self,
        message: str,
        code: str = "EXT001",
        service: str = "unknown",
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        details['service'] = service
        if status_code:
            details['status_code'] = status_code

        super().__init__(
            message=message,
            code=code,
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )


class ValidationError(AIFactoryError):
    """Erros de validação de dados"""

    def __init__(
        self,
        message: str,
        code: str = "VAL001",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['received_value'] = str(value)[:100]  # Truncate for safety

        super().__init__(
            message=message,
            code=code,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            **kwargs
        )


class AuthenticationError(AIFactoryError):
    """Erros de autenticação/autorização"""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH001",
        **kwargs
    ):
        super().__init__(
            message=message,
            code=code,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class RateLimitError(AIFactoryError):
    """Erros de rate limiting"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE001",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if retry_after:
            details['retry_after_seconds'] = retry_after

        super().__init__(
            message=message,
            code=code,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )


class TimeoutError(AIFactoryError):
    """Erros de timeout"""

    def __init__(
        self,
        message: str = "Operation timed out",
        code: str = "TIME001",
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        if operation:
            details['operation'] = operation

        super().__init__(
            message=message,
            code=code,
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )


# =============================================================================
# Error Handlers
# =============================================================================

def error_handler(
    error_class: Type[AIFactoryError] = AIFactoryError,
    default_message: str = "An error occurred",
    default_code: str = "ERR000",
    reraise: bool = True,
    log_error: bool = True,
) -> Callable:
    """
    Decorator para capturar e transformar exceções em AIFactoryError.

    Usage:
        @error_handler(DatabaseError, "Failed to fetch data", "DB002")
        async def fetch_data():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except AIFactoryError:
                # Já é um erro nosso, propaga
                raise
            except Exception as e:
                from .logging import get_logger
                logger = get_logger(func.__module__)

                error = error_class(
                    message=f"{default_message}: {str(e)}",
                    code=default_code,
                    original_error=e,
                )

                if log_error:
                    logger.error(
                        f"{error.code} - {error.message}",
                        extra={
                            "error_code": error.code,
                            "error_category": error.category.value,
                            "error_severity": error.severity.value,
                            "function": func.__name__,
                            "original_error": str(e),
                        }
                    )

                if reraise:
                    raise error from e
                return None

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except AIFactoryError:
                raise
            except Exception as e:
                from .logging import get_logger
                logger = get_logger(func.__module__)

                error = error_class(
                    message=f"{default_message}: {str(e)}",
                    code=default_code,
                    original_error=e,
                )

                if log_error:
                    logger.error(
                        f"{error.code} - {error.message}",
                        extra={
                            "error_code": error.code,
                            "error_category": error.category.value,
                            "error_severity": error.severity.value,
                            "function": func.__name__,
                            "original_error": str(e),
                        }
                    )

                if reraise:
                    raise error from e
                return None

        # Detectar se é async ou sync
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def handle_supabase_error(error: Exception, operation: str, table: str = None) -> DatabaseError:
    """
    Converte erros do Supabase em DatabaseError.

    Args:
        error: Exceção original
        operation: Operação que falhou (select, insert, update, delete)
        table: Nome da tabela (opcional)
    """
    error_str = str(error).lower()

    # Mapear erros comuns do Supabase
    if "connection" in error_str or "network" in error_str:
        code = "DB002"
        message = f"Database connection failed during {operation}"
    elif "timeout" in error_str:
        code = "DB003"
        message = f"Database operation timed out during {operation}"
    elif "duplicate" in error_str or "unique" in error_str:
        code = "DB004"
        message = f"Duplicate entry violation during {operation}"
    elif "foreign key" in error_str:
        code = "DB005"
        message = f"Foreign key constraint violation during {operation}"
    elif "not found" in error_str or "no rows" in error_str:
        code = "DB006"
        message = f"Record not found during {operation}"
    elif "permission" in error_str or "denied" in error_str:
        code = "DB007"
        message = f"Permission denied for {operation}"
    else:
        code = "DB001"
        message = f"Database error during {operation}: {str(error)}"

    return DatabaseError(
        message=message,
        code=code,
        operation=operation,
        table=table,
        original_error=error,
    )


def handle_anthropic_error(error: Exception, model: str = None) -> ExternalServiceError:
    """
    Converte erros do Anthropic em ExternalServiceError.

    Args:
        error: Exceção original
        model: Modelo sendo usado
    """
    error_str = str(error).lower()

    details = {}
    if model:
        details['model'] = model

    # Mapear erros comuns do Anthropic
    if "rate limit" in error_str or "429" in error_str:
        return RateLimitError(
            message="Anthropic API rate limit exceeded",
            code="ANT001",
            retry_after=60,  # Default retry
            original_error=error,
            details=details,
        )
    elif "authentication" in error_str or "401" in error_str or "api_key" in error_str:
        return AuthenticationError(
            message="Anthropic API authentication failed",
            code="ANT002",
            original_error=error,
            details=details,
        )
    elif "timeout" in error_str:
        return TimeoutError(
            message="Anthropic API request timed out",
            code="ANT003",
            operation="claude_completion",
            original_error=error,
            details=details,
        )
    elif "overloaded" in error_str or "503" in error_str:
        return ExternalServiceError(
            message="Anthropic API is overloaded",
            code="ANT004",
            service="anthropic",
            status_code=503,
            original_error=error,
            details=details,
        )
    elif "invalid" in error_str or "400" in error_str:
        return ValidationError(
            message=f"Invalid request to Anthropic API: {str(error)}",
            code="ANT005",
            original_error=error,
            details=details,
        )
    else:
        return ExternalServiceError(
            message=f"Anthropic API error: {str(error)}",
            code="ANT000",
            service="anthropic",
            original_error=error,
            details=details,
        )
