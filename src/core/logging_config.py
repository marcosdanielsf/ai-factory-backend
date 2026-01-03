"""
Structured logging configuration for AI Factory Backend.

Features:
- Correlation IDs for request tracing
- JSON structured logs for production
- Human-readable logs for development
- Context managers for operation tracking
- Performance timing utilities
"""

import logging
import sys
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from contextvars import ContextVar
from functools import wraps


# Context variable for request-scoped data
request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


class LogContext:
    """
    Context manager for adding contextual information to logs.

    Usage:
        with LogContext(operation="evaluate_agent", agent_id="123"):
            logger.info("Starting evaluation")
            # All logs within this block include operation and agent_id
    """

    def __init__(self, **kwargs):
        self.context = kwargs
        self.token = None

    def __enter__(self):
        current = request_context.get().copy()
        current.update(self.context)
        self.token = request_context.set(current)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            request_context.reset(self.token)
        return False


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set or generate a request ID for the current context."""
    rid = request_id or str(uuid.uuid4())[:8]
    current = request_context.get().copy()
    current["request_id"] = rid
    request_context.set(current)
    return rid


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return request_context.get().get("request_id")


class StructuredFormatter(logging.Formatter):
    """
    JSON structured log formatter for production.

    Output format:
    {
        "timestamp": "2024-01-15T10:30:00.000Z",
        "level": "INFO",
        "logger": "src.evaluator",
        "message": "Agent evaluation completed",
        "request_id": "abc12345",
        "operation": "evaluate_agent",
        "duration_ms": 1234,
        ...
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context variables
        ctx = request_context.get()
        if ctx:
            log_entry.update(ctx)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add source location for errors
        if record.levelno >= logging.ERROR:
            log_entry["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        return json.dumps(log_entry, default=str)


class DevelopmentFormatter(logging.Formatter):
    """
    Human-readable formatter for development.

    Output format:
    2024-01-15 10:30:00 | INFO     | src.evaluator | [abc12345] Agent evaluation completed
    """

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Get context
        ctx = request_context.get()
        request_id = ctx.get("request_id", "-")

        # Color for level
        color = self.COLORS.get(record.levelname, "")

        # Build message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = f"{color}{record.levelname:8}{self.RESET}"
        logger_name = record.name[-30:] if len(record.name) > 30 else record.name

        parts = [f"{timestamp} | {level} | {logger_name:30} | [{request_id}]"]

        # Add context info if present
        if ctx.get("operation"):
            parts.append(f"op={ctx['operation']}")

        parts.append(record.getMessage())

        message = " ".join(parts)

        # Add extra fields
        if hasattr(record, "extra_fields") and record.extra_fields:
            extras = " | ".join(f"{k}={v}" for k, v in record.extra_fields.items())
            message += f" | {extras}"

        # Add exception
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes context and extra fields.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing request", extra_fields={"user_id": "123", "action": "create"})
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        # Extract extra_fields from kwargs
        extra_fields = kwargs.pop("extra_fields", {})

        # Merge with any existing extra
        extra = kwargs.get("extra", {})
        extra["extra_fields"] = extra_fields

        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    level: str = "INFO",
    json_logs: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON structured logs (for production)
        log_file: Optional file path to write logs to
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if json_logs:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(DevelopmentFormatter())

    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())  # Always JSON for files
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def get_logger(name: str) -> ContextLogger:
    """
    Get a logger with context support.

    Args:
        name: Logger name (typically __name__)

    Returns:
        ContextLogger instance
    """
    return ContextLogger(logging.getLogger(name), {})


def log_duration(
    logger: ContextLogger,
    operation: str,
    level: int = logging.INFO,
) -> Callable:
    """
    Decorator to log operation duration.

    Usage:
        @log_duration(logger, "evaluate_agent")
        async def evaluate(agent_id: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.log(
                    level,
                    f"{operation} completed",
                    extra_fields={"duration_ms": round(duration_ms, 2)},
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"{operation} failed: {type(e).__name__}",
                    extra_fields={"duration_ms": round(duration_ms, 2)},
                    exc_info=True,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.log(
                    level,
                    f"{operation} completed",
                    extra_fields={"duration_ms": round(duration_ms, 2)},
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"{operation} failed: {type(e).__name__}",
                    extra_fields={"duration_ms": round(duration_ms, 2)},
                    exc_info=True,
                )
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class Timer:
    """
    Context manager for timing operations.

    Usage:
        with Timer() as timer:
            do_something()
        logger.info("Operation completed", extra_fields={"duration_ms": timer.duration_ms})
    """

    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0

    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        self.end_time = time.perf_counter()

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        end = self.end_time or time.perf_counter()
        return round((end - self.start_time) * 1000, 2)

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        end = self.end_time or time.perf_counter()
        return round(end - self.start_time, 3)
