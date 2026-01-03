"""
Standardized response models for AI Factory Backend.

Provides:
- Consistent API response structures
- Success and error response models
- Pagination support
- Response helpers
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response with common fields."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp in UTC",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request identifier for tracing",
    )


class SuccessResponse(BaseResponse, Generic[T]):
    """
    Standard success response.

    Usage:
        return SuccessResponse(
            data={"agent_id": "123", "score": 0.95},
            message="Agent evaluated successfully"
        )
    """

    success: bool = Field(default=True)
    data: Optional[T] = Field(default=None, description="Response payload")
    message: Optional[str] = Field(default=None, description="Human-readable message")


class ErrorResponse(BaseResponse):
    """
    Standard error response.

    Usage:
        return ErrorResponse(
            code="ERR_4001",
            message="Anthropic API rate limit exceeded",
            details={"retry_after": 30}
        )
    """

    error: bool = Field(default=True)
    code: str = Field(description="Error code for client handling")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context (dev mode only)",
    )


class PaginatedResponse(BaseResponse, Generic[T]):
    """
    Paginated list response.

    Usage:
        return PaginatedResponse(
            data=agents,
            total=100,
            page=1,
            page_size=20
        )
    """

    success: bool = Field(default=True)
    data: List[T] = Field(default_factory=list)
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether more pages exist")

    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        page_size: int,
        request_id: Optional[str] = None,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response with calculated has_next."""
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
            request_id=request_id,
        )


class HealthResponse(BaseResponse):
    """Health check response."""

    status: str = Field(description="Overall health status")
    version: str = Field(description="API version")
    checks: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Individual service health checks",
    )


class BatchJobResponse(BaseResponse):
    """Response for batch job initiation."""

    success: bool = Field(default=True)
    job_id: str = Field(description="Unique job identifier")
    status: str = Field(default="queued", description="Current job status")
    status_endpoint: str = Field(description="URL to check job status")
    estimated_duration_seconds: Optional[int] = Field(
        default=None,
        description="Estimated time to complete",
    )


class BatchJobStatusResponse(BaseResponse):
    """Response for batch job status check."""

    job_id: str = Field(description="Job identifier")
    status: str = Field(description="Current status: queued, running, completed, failed")
    progress: Optional[Dict[str, int]] = Field(
        default=None,
        description="Progress information (completed, total, failed)",
    )
    result: Optional[Any] = Field(
        default=None,
        description="Job result when completed",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if failed",
    )
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


# =============================================================================
# Response Helpers
# =============================================================================

def success(
    data: Any = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a success response dict.

    Usage:
        return success(data={"id": "123"}, message="Created successfully")
    """
    return SuccessResponse(
        data=data,
        message=message,
        request_id=request_id,
    ).model_dump(exclude_none=True)


def error(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create an error response dict.

    Usage:
        return error(code="ERR_1002", message="Agent not found")
    """
    return ErrorResponse(
        code=code,
        message=message,
        details=details,
        request_id=request_id,
    ).model_dump(exclude_none=True)


def paginated(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a paginated response dict.

    Usage:
        return paginated(data=agents, total=100, page=1, page_size=20)
    """
    return PaginatedResponse.create(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        request_id=request_id,
    ).model_dump(exclude_none=True)


def health(
    status: str,
    version: str,
    checks: Optional[Dict[str, Dict[str, Any]]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a health check response dict.

    Usage:
        return health(
            status="healthy",
            version="1.0.0",
            checks={"database": {"status": "connected", "latency_ms": 5}}
        )
    """
    return HealthResponse(
        status=status,
        version=version,
        checks=checks or {},
        request_id=request_id,
    ).model_dump(exclude_none=True)


def batch_job(
    job_id: str,
    status_endpoint: str,
    estimated_duration: Optional[int] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a batch job initiation response dict.

    Usage:
        return batch_job(
            job_id="batch_abc123",
            status_endpoint="/api/v1/jobs/batch_abc123"
        )
    """
    return BatchJobResponse(
        job_id=job_id,
        status_endpoint=status_endpoint,
        estimated_duration_seconds=estimated_duration,
        request_id=request_id,
    ).model_dump(exclude_none=True)
