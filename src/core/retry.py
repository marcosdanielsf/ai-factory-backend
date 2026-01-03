"""
AI Factory - Retry Logic with Tenacity
=======================================

Retry strategies para diferentes tipos de operações:
- Database (Supabase)
- External APIs (Anthropic, etc)
- Network requests

Usa tenacity para exponential backoff com jitter.
"""

import functools
from typing import Callable, TypeVar, Optional, Tuple, Type
from dataclasses import dataclass
import random

from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    wait_random_exponential,
    retry_if_exception_type,
    retry_if_exception,
    before_sleep_log,
    after_log,
    RetryError,
)

from .errors import (
    AIFactoryError,
    DatabaseError,
    ExternalServiceError,
    RateLimitError,
    TimeoutError,
)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuração para retry logic"""
    max_attempts: int = 3
    max_delay_seconds: float = 60.0
    initial_wait_seconds: float = 1.0
    max_wait_seconds: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_timeout: bool = True
    retry_on_rate_limit: bool = True
    retry_on_server_error: bool = True

    # Códigos HTTP que devem triggear retry
    retryable_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504)


# Configs padrão para diferentes cenários
DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_wait_seconds=0.5,
    max_wait_seconds=15.0,
    exponential_base=2.0,
    jitter=True,
)

ANTHROPIC_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_wait_seconds=2.0,
    max_wait_seconds=60.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_rate_limit=True,
)

EXTERNAL_API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_wait_seconds=1.0,
    max_wait_seconds=30.0,
    exponential_base=2.0,
    jitter=True,
)


def _should_retry_exception(exception: Exception) -> bool:
    """
    Determina se uma exceção deve triggear retry.

    Returns:
        True se deve tentar novamente
    """
    # Nunca retry em erros de validação
    from .errors import ValidationError, AuthenticationError
    if isinstance(exception, (ValidationError, AuthenticationError)):
        return False

    # Retry em rate limit
    if isinstance(exception, RateLimitError):
        return True

    # Retry em timeout
    if isinstance(exception, TimeoutError):
        return True

    # Retry em erros de database temporários
    if isinstance(exception, DatabaseError):
        # Não retry em erros de constraint/validação
        if exception.code in ("DB004", "DB005", "DB006", "DB007"):
            return False
        return True

    # Retry em erros de serviço externo
    if isinstance(exception, ExternalServiceError):
        # Verifica status code se disponível
        status_code = exception.details.get('status_code')
        if status_code in (429, 500, 502, 503, 504):
            return True
        return False

    # Erros genéricos - retry em erros de rede
    error_str = str(exception).lower()
    network_errors = ['connection', 'timeout', 'network', 'socket', 'reset']
    return any(err in error_str for err in network_errors)


def _get_wait_time(attempt: int, config: RetryConfig) -> float:
    """
    Calcula tempo de espera com exponential backoff + jitter.

    Args:
        attempt: Número da tentativa (1-indexed)
        config: Configuração de retry

    Returns:
        Tempo de espera em segundos
    """
    # Exponential backoff
    wait = config.initial_wait_seconds * (config.exponential_base ** (attempt - 1))

    # Cap no máximo
    wait = min(wait, config.max_wait_seconds)

    # Adiciona jitter (±25%)
    if config.jitter:
        jitter = wait * 0.25
        wait = wait + random.uniform(-jitter, jitter)

    return max(0.1, wait)  # Mínimo 100ms


def retry_with_backoff(
    config: RetryConfig = None,
    on_retry: Optional[Callable] = None,
) -> Callable:
    """
    Decorator genérico para retry com exponential backoff.

    Usage:
        @retry_with_backoff(config=DATABASE_RETRY_CONFIG)
        async def fetch_data():
            ...

        @retry_with_backoff()
        def sync_operation():
            ...
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            from .logging import get_logger
            logger = get_logger(func.__module__)

            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Verifica se deve retry
                    if not _should_retry_exception(e):
                        logger.warning(
                            f"Not retrying {func.__name__}: {type(e).__name__}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "error_type": type(e).__name__,
                                "will_retry": False,
                            }
                        )
                        raise

                    # Última tentativa - não espera
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"Max retries ({config.max_attempts}) exceeded for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "total_attempts": attempt,
                                "error_type": type(e).__name__,
                            }
                        )
                        raise

                    # Calcula tempo de espera
                    wait_time = _get_wait_time(attempt, config)

                    logger.warning(
                        f"Retry {attempt}/{config.max_attempts} for {func.__name__} "
                        f"in {wait_time:.2f}s",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": config.max_attempts,
                            "wait_seconds": wait_time,
                            "error_type": type(e).__name__,
                            "error_message": str(e)[:200],
                        }
                    )

                    # Callback opcional
                    if on_retry:
                        on_retry(attempt, e, wait_time)

                    # Espera antes do próximo retry
                    import asyncio
                    await asyncio.sleep(wait_time)

            # Não deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            from .logging import get_logger
            import time

            logger = get_logger(func.__module__)
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if not _should_retry_exception(e):
                        logger.warning(
                            f"Not retrying {func.__name__}: {type(e).__name__}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "error_type": type(e).__name__,
                                "will_retry": False,
                            }
                        )
                        raise

                    if attempt >= config.max_attempts:
                        logger.error(
                            f"Max retries ({config.max_attempts}) exceeded for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "total_attempts": attempt,
                                "error_type": type(e).__name__,
                            }
                        )
                        raise

                    wait_time = _get_wait_time(attempt, config)

                    logger.warning(
                        f"Retry {attempt}/{config.max_attempts} for {func.__name__} "
                        f"in {wait_time:.2f}s",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": config.max_attempts,
                            "wait_seconds": wait_time,
                            "error_type": type(e).__name__,
                            "error_message": str(e)[:200],
                        }
                    )

                    if on_retry:
                        on_retry(attempt, e, wait_time)

                    time.sleep(wait_time)

            if last_exception:
                raise last_exception

        # Detectar se é async ou sync
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Decorators de conveniência
def retry_database(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry otimizado para operações de banco de dados.

    Usage:
        @retry_database
        def query_users():
            ...
    """
    return retry_with_backoff(config=DATABASE_RETRY_CONFIG)(func)


def retry_external_api(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry otimizado para APIs externas.

    Usage:
        @retry_external_api
        async def call_anthropic():
            ...
    """
    return retry_with_backoff(config=EXTERNAL_API_RETRY_CONFIG)(func)


def retry_anthropic(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry otimizado para Anthropic API.

    Usage:
        @retry_anthropic
        async def generate_response():
            ...
    """
    return retry_with_backoff(config=ANTHROPIC_RETRY_CONFIG)(func)


# =============================================================================
# Utility para retry manual
# =============================================================================

async def execute_with_retry(
    operation: Callable[..., T],
    *args,
    config: RetryConfig = None,
    operation_name: str = "operation",
    **kwargs
) -> T:
    """
    Executa uma operação com retry.
    Útil quando não se pode usar decorator.

    Usage:
        result = await execute_with_retry(
            client.fetch_data,
            user_id,
            config=DATABASE_RETRY_CONFIG,
            operation_name="fetch_user"
        )
    """
    if config is None:
        config = RetryConfig()

    @retry_with_backoff(config=config)
    async def _execute():
        return await operation(*args, **kwargs)

    return await _execute()


def execute_with_retry_sync(
    operation: Callable[..., T],
    *args,
    config: RetryConfig = None,
    operation_name: str = "operation",
    **kwargs
) -> T:
    """
    Versão síncrona de execute_with_retry.
    """
    if config is None:
        config = RetryConfig()

    @retry_with_backoff(config=config)
    def _execute():
        return operation(*args, **kwargs)

    return _execute()
