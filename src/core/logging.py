"""
AI Factory - Structured Logging
================================

Logging estruturado com:
- Output JSON para produção
- Contexto de request (request_id, user_id, etc)
- Métricas de performance
- Suporte a diferentes níveis por ambiente
"""

import os
import sys
import json
import time
import logging
import functools
from typing import Optional, Dict, Any, Callable, TypeVar
from datetime import datetime
from contextvars import ContextVar
from dataclasses import dataclass, field, asdict

T = TypeVar('T')

# Context variables para request tracking
_request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
_user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
_operation: ContextVar[Optional[str]] = ContextVar('operation', default=None)


@dataclass
class LogContext:
    """Contexto para logs estruturados"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    operation: Optional[str] = None
    agent_id: Optional[str] = None
    duration_ms: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class StructuredFormatter(logging.Formatter):
    """
    Formatter que produz logs em JSON.
    Ideal para produção com log aggregators (Datadog, CloudWatch, etc).
    """

    def __init__(self, include_timestamp: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_timestamp:
            log_data["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Adiciona contexto de request
        request_id = _request_id.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = _user_id.get()
        if user_id:
            log_data["user_id"] = user_id

        operation = _operation.get()
        if operation:
            log_data["operation"] = operation

        # Adiciona campos extras
        if hasattr(record, '__dict__'):
            extra_fields = [
                'function', 'error_code', 'error_category', 'error_severity',
                'attempt', 'max_attempts', 'wait_seconds', 'duration_ms',
                'agent_id', 'test_id', 'score', 'status_code', 'method', 'path',
                'error_type', 'error_message', 'will_retry', 'total_attempts',
            ]
            for field_name in extra_fields:
                if hasattr(record, field_name):
                    value = getattr(record, field_name)
                    if value is not None:
                        log_data[field_name] = value

        # Adiciona exception info se presente
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Adiciona localização do código
        log_data["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        return json.dumps(log_data, default=str, ensure_ascii=False)


class PrettyFormatter(logging.Formatter):
    """
    Formatter legível para desenvolvimento local.
    """

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Cor baseada no level
        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET if color else ''

        # Timestamp
        timestamp = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]

        # Request ID (se presente)
        request_id = _request_id.get()
        req_str = f"[{request_id[:8]}] " if request_id else ""

        # Monta linha principal
        main_line = (
            f"{timestamp} {color}{record.levelname:8}{reset} "
            f"{req_str}{record.name}: {record.getMessage()}"
        )

        # Adiciona campos extras importantes
        extras = []
        extra_fields = ['duration_ms', 'attempt', 'error_code', 'score']
        for field_name in extra_fields:
            if hasattr(record, field_name):
                value = getattr(record, field_name)
                if value is not None:
                    extras.append(f"{field_name}={value}")

        if extras:
            main_line += f" ({', '.join(extras)})"

        # Adiciona exception se presente
        if record.exc_info:
            main_line += f"\n{self.formatException(record.exc_info)}"

        return main_line


def setup_logging(
    level: str = None,
    json_output: bool = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configura logging para a aplicação.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        json_output: Se True, usa JSON. Se None, detecta do ambiente.
        log_file: Arquivo para logs (opcional)
    """
    # Detecta ambiente
    env = os.getenv('ENVIRONMENT', 'development').lower()
    is_production = env in ('production', 'prod', 'staging')

    # Defaults baseados no ambiente
    if level is None:
        level = os.getenv('LOG_LEVEL', 'DEBUG' if not is_production else 'INFO')

    if json_output is None:
        # JSON em produção, pretty em dev
        json_output = is_production or os.getenv('LOG_FORMAT') == 'json'

    # Configura root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove handlers existentes
    root_logger.handlers = []

    # Escolhe formatter
    if json_output:
        formatter = StructuredFormatter()
    else:
        formatter = PrettyFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (se especificado)
    if log_file:
        # Cria diretório se necessário
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(StructuredFormatter())  # Sempre JSON em arquivo
        root_logger.addHandler(file_handler)

    # Reduz verbosidade de bibliotecas
    for lib in ['httpx', 'httpcore', 'urllib3', 'asyncio']:
        logging.getLogger(lib).setLevel(logging.WARNING)

    root_logger.info(
        "Logging initialized",
        extra={
            'level': level,
            'format': 'json' if json_output else 'pretty',
            'environment': env,
        }
    )


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtém um logger com nome do módulo.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing request", extra={"user_id": "123"})
    """
    return logging.getLogger(name or __name__)


# =============================================================================
# Decorators para logging
# =============================================================================

def log_operation(
    operation_name: str = None,
    log_args: bool = False,
    log_result: bool = False,
    log_errors: bool = True,
) -> Callable:
    """
    Decorator que loga entrada, saída e tempo de execução.

    Usage:
        @log_operation("fetch_user")
        async def fetch_user(user_id: str):
            ...

        @log_operation(log_args=True, log_result=True)
        def process_data(data):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = operation_name or func.__name__
        logger = get_logger(func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            start_time = time.perf_counter()

            # Log entrada
            extra = {"function": name}
            if log_args:
                extra["args"] = str(args)[:200]
                extra["kwargs"] = str(kwargs)[:200]

            logger.debug(f"Starting {name}", extra=extra)

            # Define operation no contexto
            token = _operation.set(name)

            try:
                result = await func(*args, **kwargs)

                duration_ms = (time.perf_counter() - start_time) * 1000

                # Log sucesso
                extra = {"function": name, "duration_ms": round(duration_ms, 2)}
                if log_result:
                    extra["result"] = str(result)[:200]

                logger.info(f"Completed {name}", extra=extra)

                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000

                if log_errors:
                    logger.error(
                        f"Failed {name}: {str(e)}",
                        extra={
                            "function": name,
                            "duration_ms": round(duration_ms, 2),
                            "error_type": type(e).__name__,
                            "error_message": str(e)[:500],
                        },
                        exc_info=True,
                    )
                raise
            finally:
                _operation.reset(token)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            start_time = time.perf_counter()

            extra = {"function": name}
            if log_args:
                extra["args"] = str(args)[:200]
                extra["kwargs"] = str(kwargs)[:200]

            logger.debug(f"Starting {name}", extra=extra)

            token = _operation.set(name)

            try:
                result = func(*args, **kwargs)

                duration_ms = (time.perf_counter() - start_time) * 1000

                extra = {"function": name, "duration_ms": round(duration_ms, 2)}
                if log_result:
                    extra["result"] = str(result)[:200]

                logger.info(f"Completed {name}", extra=extra)

                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000

                if log_errors:
                    logger.error(
                        f"Failed {name}: {str(e)}",
                        extra={
                            "function": name,
                            "duration_ms": round(duration_ms, 2),
                            "error_type": type(e).__name__,
                            "error_message": str(e)[:500],
                        },
                        exc_info=True,
                    )
                raise
            finally:
                _operation.reset(token)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def log_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """
    Log de request HTTP estruturado.

    Usage:
        log_request("GET", "/api/v1/users", 200, 45.2)
    """
    logger = get_logger("http.request")

    level = logging.INFO
    if status_code >= 500:
        level = logging.ERROR
    elif status_code >= 400:
        level = logging.WARNING

    logger.log(
        level,
        f"{method} {path} {status_code}",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
    )


def log_response(
    status_code: int,
    body_size: int = 0,
    headers: Dict[str, str] = None,
) -> None:
    """Log de response HTTP estruturado."""
    logger = get_logger("http.response")
    logger.debug(
        f"Response {status_code}",
        extra={
            "status_code": status_code,
            "body_size": body_size,
        }
    )


# =============================================================================
# Context Management
# =============================================================================

def set_request_id(request_id: str) -> None:
    """Define request_id no contexto."""
    _request_id.set(request_id)


def get_request_id() -> Optional[str]:
    """Obtém request_id do contexto."""
    return _request_id.get()


def set_user_id(user_id: str) -> None:
    """Define user_id no contexto."""
    _user_id.set(user_id)


def get_user_id() -> Optional[str]:
    """Obtém user_id do contexto."""
    return _user_id.get()


class LogContextManager:
    """
    Context manager para definir contexto de logging.

    Usage:
        with LogContextManager(request_id="abc123", user_id="user1"):
            logger.info("Processing")  # Inclui request_id e user_id
    """

    def __init__(
        self,
        request_id: str = None,
        user_id: str = None,
        operation: str = None,
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.operation = operation
        self._tokens = []

    def __enter__(self):
        if self.request_id:
            self._tokens.append(('request_id', _request_id.set(self.request_id)))
        if self.user_id:
            self._tokens.append(('user_id', _user_id.set(self.user_id)))
        if self.operation:
            self._tokens.append(('operation', _operation.set(self.operation)))
        return self

    def __exit__(self, *args):
        for var_name, token in self._tokens:
            if var_name == 'request_id':
                _request_id.reset(token)
            elif var_name == 'user_id':
                _user_id.reset(token)
            elif var_name == 'operation':
                _operation.reset(token)
