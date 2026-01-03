"""
Retry logic utilities using tenacity.

Provides:
- Configurable retry decorators for different scenarios
- Specific retry configs for Anthropic API, Supabase, etc.
- Exponential backoff with jitter
- Custom retry conditions
"""

import random
from typing import Callable, Optional, Type, Tuple, Union
from dataclasses import dataclass, field
from functools import wraps

from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    wait_random_exponential,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log,
    after_log,
    RetryError,
)

from .logging_config import get_logger
from .exceptions import (
    AIFactoryError,
    DatabaseError,
    ExternalAPIError,
    AnthropicAPIError,
    AnthropicRateLimitError,
    RateLimitError,
    TimeoutError,
)

logger = get_logger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    max_delay_seconds: float = 60.0
    initial_delay_seconds: float = 1.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,)

    def __post_init__(self):
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


# Pre-configured retry configs for common scenarios
ANTHROPIC_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay_seconds=2.0,
    max_delay_seconds=120.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=(
        AnthropicAPIError,
        AnthropicRateLimitError,
        ConnectionError,
        TimeoutError,
    ),
)

SUPABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=4,
    initial_delay_seconds=1.0,
    max_delay_seconds=30.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=(
        DatabaseError,
        ConnectionError,
        TimeoutError,
    ),
)

HTTP_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay_seconds=0.5,
    max_delay_seconds=15.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=(
        ConnectionError,
        TimeoutError,
        ExternalAPIError,
    ),
)


def is_retryable_status_code(status_code: int) -> bool:
    """Check if an HTTP status code should trigger a retry."""
    # 429: Rate limited
    # 500+: Server errors (except 501 Not Implemented)
    return status_code == 429 or (status_code >= 500 and status_code != 501)


def calculate_backoff(
    attempt: int,
    initial_delay: float,
    exponential_base: float,
    max_delay: float,
    jitter: bool = True,
) -> float:
    """
    Calculate backoff delay with optional jitter.

    Uses exponential backoff: delay = initial * (base ** attempt)
    With jitter: adds random factor to prevent thundering herd
    """
    delay = min(initial_delay * (exponential_base ** attempt), max_delay)

    if jitter:
        # Full jitter: random value between 0 and calculated delay
        delay = random.uniform(0, delay)

    return delay


def with_retry(
    config: Optional[RetryConfig] = None,
    max_attempts: Optional[int] = None,
    initial_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable] = None,
) -> Callable:
    """
    Decorator to add retry logic to a function.

    Args:
        config: RetryConfig to use (or individual params below)
        max_attempts: Maximum retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        retry_on: Tuple of exception types to retry on
        on_retry: Callback function called on each retry

    Usage:
        @with_retry(config=ANTHROPIC_RETRY_CONFIG)
        async def call_anthropic(prompt: str):
            ...

        @with_retry(max_attempts=3, retry_on=(ConnectionError,))
        def fetch_data():
            ...
    """
    # Build config from individual params or use provided config
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts or 3,
            initial_delay_seconds=initial_delay or 1.0,
            max_delay_seconds=max_delay or 60.0,
            retry_on_exceptions=retry_on or (Exception,),
        )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = calculate_backoff(
                            attempt=attempt,
                            initial_delay=config.initial_delay_seconds,
                            exponential_base=config.exponential_base,
                            max_delay=config.max_delay_seconds,
                            jitter=config.jitter,
                        )

                        logger.warning(
                            f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__}",
                            extra_fields={
                                "exception": type(e).__name__,
                                "delay_seconds": round(delay, 2),
                            },
                        )

                        if on_retry:
                            on_retry(attempt, e)

                        import asyncio
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}",
                            extra_fields={"exception": type(e).__name__},
                        )
                except Exception as e:
                    # Non-retryable exception
                    raise

            # All retries exhausted
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retry_on_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = calculate_backoff(
                            attempt=attempt,
                            initial_delay=config.initial_delay_seconds,
                            exponential_base=config.exponential_base,
                            max_delay=config.max_delay_seconds,
                            jitter=config.jitter,
                        )

                        logger.warning(
                            f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__}",
                            extra_fields={
                                "exception": type(e).__name__,
                                "delay_seconds": round(delay, 2),
                            },
                        )

                        if on_retry:
                            on_retry(attempt, e)

                        import time
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}",
                            extra_fields={"exception": type(e).__name__},
                        )
                except Exception as e:
                    # Non-retryable exception
                    raise

            # All retries exhausted
            raise last_exception

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def retry_anthropic(func: Callable) -> Callable:
    """
    Shorthand decorator for Anthropic API calls.

    Usage:
        @retry_anthropic
        async def evaluate_with_claude(prompt: str):
            return await client.messages.create(...)
    """
    return with_retry(config=ANTHROPIC_RETRY_CONFIG)(func)


def retry_supabase(func: Callable) -> Callable:
    """
    Shorthand decorator for Supabase calls.

    Usage:
        @retry_supabase
        def get_agent(agent_id: str):
            return client.table('agents').select('*').eq('id', agent_id).execute()
    """
    return with_retry(config=SUPABASE_RETRY_CONFIG)(func)


def retry_http(func: Callable) -> Callable:
    """
    Shorthand decorator for HTTP calls.

    Usage:
        @retry_http
        async def fetch_external_api(url: str):
            return await httpx.get(url)
    """
    return with_retry(config=HTTP_RETRY_CONFIG)(func)


class RetryContext:
    """
    Context manager for manual retry control.

    Usage:
        async with RetryContext(max_attempts=3) as ctx:
            while ctx.should_retry:
                try:
                    result = await some_operation()
                    break
                except RetryableError as e:
                    await ctx.handle_retry(e)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.attempt = 0
        self.last_exception: Optional[Exception] = None

    async def __aenter__(self) -> "RetryContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    @property
    def should_retry(self) -> bool:
        """Check if more retry attempts are available."""
        return self.attempt < self.max_attempts

    async def handle_retry(self, exception: Exception) -> None:
        """Handle a retry attempt."""
        self.last_exception = exception
        self.attempt += 1

        if self.attempt >= self.max_attempts:
            raise exception

        delay = calculate_backoff(
            attempt=self.attempt - 1,
            initial_delay=self.initial_delay,
            exponential_base=2.0,
            max_delay=self.max_delay,
            jitter=self.jitter,
        )

        logger.warning(
            f"Retry attempt {self.attempt}/{self.max_attempts}",
            extra_fields={
                "exception": type(exception).__name__,
                "delay_seconds": round(delay, 2),
            },
        )

        import asyncio
        await asyncio.sleep(delay)
