"""
FastAPI middleware for AI Factory Backend.

Provides:
- Request ID generation and propagation
- Global exception handling
- Request/Response logging
- Performance timing
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_config import get_logger, set_request_id, LogContext, Timer
from .exceptions import AIFactoryError, ErrorCode
from .responses import ErrorResponse


logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and propagate request IDs.

    - Generates a unique request ID for each request
    - Uses X-Request-ID header if provided
    - Adds request ID to response headers
    - Sets request ID in logging context
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]

        # Set in logging context
        set_request_id(request_id)

        # Store in request state for access in endpoints
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request/response details.

    Logs:
    - Request method, path, and query params
    - Response status code
    - Request duration
    """

    # Paths to skip logging (health checks, etc.)
    SKIP_PATHS = {"/health", "/ping", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        with Timer() as timer:
            # Log request
            logger.info(
                f"Request started: {request.method} {request.url.path}",
                extra_fields={
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.query_params) if request.query_params else None,
                    "client_ip": request.client.host if request.client else None,
                },
            )

            try:
                response = await call_next(request)

                # Log response
                log_method = logger.info if response.status_code < 400 else logger.warning
                log_method(
                    f"Request completed: {request.method} {request.url.path}",
                    extra_fields={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": timer.duration_ms,
                    },
                )

                return response

            except Exception as e:
                logger.error(
                    f"Request failed: {request.method} {request.url.path}",
                    extra_fields={
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": timer.duration_ms,
                        "error": str(e),
                    },
                    exc_info=True,
                )
                raise


def create_exception_handlers(app: FastAPI, include_details: bool = False) -> None:
    """
    Register global exception handlers on the FastAPI app.

    Args:
        app: FastAPI application instance
        include_details: Whether to include error details in responses (dev only)
    """

    @app.exception_handler(AIFactoryError)
    async def ai_factory_error_handler(
        request: Request, exc: AIFactoryError
    ) -> JSONResponse:
        """Handle all AIFactoryError exceptions."""
        logger.error(
            f"AIFactoryError: {exc.message}",
            extra_fields={
                "error_code": exc.error_code.value,
                "status_code": exc.status_code,
                "details": exc.details if include_details else None,
            },
            exc_info=exc.original_error is not None,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=True,
                code=exc.error_code.value,
                message=exc.message,
                details=exc.details if include_details else None,
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(exclude_none=True),
            headers={"X-Error-Code": exc.error_code.value},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=True,
                code=ErrorCode.INTERNAL_ERROR.value,
                message="An unexpected error occurred",
                details={"exception": str(exc)} if include_details else None,
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(exclude_none=True),
        )


def setup_middleware(
    app: FastAPI,
    include_error_details: bool = False,
    enable_request_logging: bool = True,
) -> None:
    """
    Set up all middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
        include_error_details: Include error details in responses (dev only)
        enable_request_logging: Enable request/response logging
    """
    # Add middleware in order (executed in reverse order)
    if enable_request_logging:
        app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(RequestIDMiddleware)

    # Register exception handlers
    create_exception_handlers(app, include_details=include_error_details)


class OperationContext:
    """
    Context manager for tracking operations within endpoints.

    Usage:
        async with OperationContext("evaluate_agent", agent_id=agent_id) as ctx:
            result = await evaluate(agent_id)
            ctx.add_metric("tokens_used", result.tokens)
            return result
    """

    def __init__(self, operation: str, **context_data):
        self.operation = operation
        self.context_data = context_data
        self.metrics = {}
        self.timer = Timer()

    async def __aenter__(self) -> "OperationContext":
        self.timer.__enter__()
        logger.info(
            f"Operation started: {self.operation}",
            extra_fields=self.context_data,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.timer.__exit__(exc_type, exc_val, exc_tb)

        if exc_type is None:
            logger.info(
                f"Operation completed: {self.operation}",
                extra_fields={
                    **self.context_data,
                    **self.metrics,
                    "duration_ms": self.timer.duration_ms,
                },
            )
        else:
            logger.error(
                f"Operation failed: {self.operation}",
                extra_fields={
                    **self.context_data,
                    **self.metrics,
                    "duration_ms": self.timer.duration_ms,
                    "error": str(exc_val),
                },
            )

        return False  # Don't suppress exceptions

    def add_metric(self, name: str, value) -> None:
        """Add a metric to be logged on completion."""
        self.metrics[name] = value
