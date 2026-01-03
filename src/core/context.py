"""
AI Factory - Request Context & Tracing
=======================================

Context management para:
- Request ID tracking
- User/Agent identification
- Distributed tracing
- Performance metrics
"""

import uuid
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from contextvars import ContextVar

# Context variable para RequestContext
_request_context: ContextVar[Optional['RequestContext']] = ContextVar(
    'request_context', default=None
)


@dataclass
class RequestContext:
    """
    Contexto da requisição atual.
    Propagado através de toda a stack para logging e tracing.
    """
    request_id: str
    start_time: float = field(default_factory=time.perf_counter)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Identificação
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    client_id: Optional[str] = None

    # Request info
    method: Optional[str] = None
    path: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Tracing
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        request_id: str = None,
        trace_id: str = None,
        **kwargs
    ) -> 'RequestContext':
        """
        Cria novo RequestContext.

        Args:
            request_id: ID único da request (gerado se não fornecido)
            trace_id: Trace ID para distributed tracing
            **kwargs: Campos adicionais
        """
        return cls(
            request_id=request_id or generate_request_id(),
            trace_id=trace_id or generate_trace_id(),
            span_id=generate_span_id(),
            **kwargs
        )

    @property
    def duration_ms(self) -> float:
        """Duração desde o início em milliseconds."""
        return (time.perf_counter() - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict para logging/serialização."""
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "method": self.method,
            "path": self.path,
            "duration_ms": round(self.duration_ms, 2),
            "timestamp": self.timestamp,
        }

    def to_headers(self) -> Dict[str, str]:
        """Gera headers para propagação de contexto."""
        headers = {
            "X-Request-ID": self.request_id,
        }
        if self.trace_id:
            headers["X-Trace-ID"] = self.trace_id
        if self.span_id:
            headers["X-Span-ID"] = self.span_id
        return headers


# =============================================================================
# Context Functions
# =============================================================================

def generate_request_id() -> str:
    """Gera ID único para request."""
    return f"req_{uuid.uuid4().hex[:16]}"


def generate_trace_id() -> str:
    """Gera trace ID para distributed tracing."""
    return f"trace_{uuid.uuid4().hex}"


def generate_span_id() -> str:
    """Gera span ID para tracing."""
    return f"span_{uuid.uuid4().hex[:12]}"


def set_request_context(context: RequestContext) -> None:
    """
    Define o contexto da request atual.
    Deve ser chamado no início do request handler.
    """
    _request_context.set(context)

    # Também atualiza as context vars do módulo de logging
    from .logging import set_request_id, set_user_id
    set_request_id(context.request_id)
    if context.user_id:
        set_user_id(context.user_id)


def get_request_context() -> Optional[RequestContext]:
    """Obtém o contexto da request atual."""
    return _request_context.get()


def get_request_id() -> Optional[str]:
    """Obtém o request_id da request atual."""
    ctx = get_request_context()
    return ctx.request_id if ctx else None


def clear_request_context() -> None:
    """Limpa o contexto da request."""
    _request_context.set(None)


# =============================================================================
# Context Manager
# =============================================================================

class RequestContextManager:
    """
    Context manager para gerenciar RequestContext.

    Usage:
        async with RequestContextManager(request) as ctx:
            # ctx.request_id disponível
            result = await process_request()

        # Ou manualmente:
        with RequestContextManager.create(user_id="123"):
            do_something()
    """

    def __init__(self, context: RequestContext = None, **kwargs):
        if context:
            self.context = context
        else:
            self.context = RequestContext.create(**kwargs)
        self._token = None

    def __enter__(self) -> RequestContext:
        self._token = _request_context.set(self.context)
        # Sync logging context
        from .logging import set_request_id, set_user_id
        set_request_id(self.context.request_id)
        if self.context.user_id:
            set_user_id(self.context.user_id)
        return self.context

    def __exit__(self, *args):
        if self._token:
            _request_context.reset(self._token)

    async def __aenter__(self) -> RequestContext:
        return self.__enter__()

    async def __aexit__(self, *args):
        return self.__exit__(*args)

    @classmethod
    def create(cls, **kwargs) -> 'RequestContextManager':
        """Factory method para criar com RequestContext novo."""
        return cls(context=RequestContext.create(**kwargs))


# =============================================================================
# FastAPI Integration
# =============================================================================

def extract_context_from_request(request) -> RequestContext:
    """
    Extrai contexto de uma FastAPI Request.

    Usage (in middleware or dependency):
        @app.middleware("http")
        async def add_context(request: Request, call_next):
            ctx = extract_context_from_request(request)
            set_request_context(ctx)
            response = await call_next(request)
            return response
    """
    # Extrai headers de tracing
    request_id = request.headers.get("X-Request-ID")
    trace_id = request.headers.get("X-Trace-ID")
    parent_span_id = request.headers.get("X-Span-ID")

    # Extrai client info
    client_ip = None
    if hasattr(request, 'client') and request.client:
        client_ip = request.client.host

    # Cria contexto
    return RequestContext.create(
        request_id=request_id,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        method=request.method,
        path=str(request.url.path),
        client_ip=client_ip,
        user_agent=request.headers.get("User-Agent"),
    )


def add_context_to_response(response, context: RequestContext) -> None:
    """
    Adiciona headers de contexto à response.

    Usage:
        response = JSONResponse(content=data)
        add_context_to_response(response, ctx)
    """
    response.headers["X-Request-ID"] = context.request_id
    if context.trace_id:
        response.headers["X-Trace-ID"] = context.trace_id
