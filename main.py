"""
AI Factory Backend API - FastAPI Application
============================================
High-performance API for AI testing framework deployed on Railway.
With structured logging, retry logic, and robust error handling.
"""

import os
import time
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Core modules
from src.core.logging_config import setup_logging, get_logger, LogContext, Timer
from src.core.middleware import setup_middleware, OperationContext
from src.core.exceptions import (
    AIFactoryError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from src.core.responses import (
    success,
    error,
    health,
    batch_job,
    SuccessResponse,
    ErrorResponse,
    HealthResponse,
    BatchJobResponse,
)

# Application modules
from src.supabase_client import SupabaseClient
from src.test_runner import TestRunner
from src.evaluator import Evaluator

# Configure structured logging
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=IS_PRODUCTION,
)

logger = get_logger(__name__)


# =============================================================================
# Application State
# =============================================================================

class AppState:
    """Application state container."""

    def __init__(self):
        self.supabase_client: Optional[SupabaseClient] = None
        self.test_runner: Optional[TestRunner] = None
        self.startup_time: Optional[datetime] = None
        self.version: str = "1.1.0"

    @property
    def is_ready(self) -> bool:
        """Check if all services are initialized."""
        return self.supabase_client is not None and self.test_runner is not None


app_state = AppState()


# =============================================================================
# Application Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Starting AI Factory API...")

    try:
        # Initialize Supabase client
        with Timer() as timer:
            app_state.supabase_client = SupabaseClient()
        logger.info(
            "Supabase client initialized",
            extra_fields={"duration_ms": timer.duration_ms},
        )

        # Initialize Test Runner
        with Timer() as timer:
            app_state.test_runner = TestRunner()
        logger.info(
            "Test runner initialized",
            extra_fields={"duration_ms": timer.duration_ms},
        )

        app_state.startup_time = datetime.now(timezone.utc)
        logger.info(
            "AI Factory API started successfully",
            extra_fields={"version": app_state.version},
        )

    except DatabaseError as e:
        logger.error(
            "Failed to initialize database connection",
            extra_fields={"error_code": e.error_code.value, "error": str(e)},
        )
        raise
    except Exception as e:
        logger.error(
            "Failed to initialize application",
            extra_fields={"error_type": type(e).__name__, "error": str(e)},
        )
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Factory API...")
    app_state.supabase_client = None
    app_state.test_runner = None


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="AI Factory API",
    description="High-performance testing framework for AI agents",
    version=app_state.version,
    lifespan=lifespan,
)

# Setup custom middleware (request ID, logging, error handlers)
setup_middleware(
    app,
    include_error_details=not IS_PRODUCTION,
    enable_request_logging=True,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# =============================================================================
# Pydantic Models
# =============================================================================

class TestCaseInput(BaseModel):
    """Test case input model."""
    agent_id: str = Field(..., description="Unique agent identifier")
    test_name: str = Field(..., description="Name of the test")
    input_text: str = Field(..., description="Input to test agent")
    expected_behavior: str = Field(..., description="Expected behavior")
    rubric_focus: list = Field(default_factory=list, description="Focus areas for evaluation")


class TestResult(BaseModel):
    """Test result model."""
    test_id: str
    agent_id: str
    test_name: str
    status: str
    score: float
    feedback: str
    execution_time_ms: float
    timestamp: datetime


class BatchTestInput(BaseModel):
    """Batch test input model."""
    agent_id: str
    test_cases: list[TestCaseInput]
    run_name: Optional[str] = None


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """
    Health check endpoint with detailed service status.

    Returns:
        Health status with database connectivity info
    """
    request_id = getattr(request.state, "request_id", None)

    checks = {}

    # Check Supabase
    if app_state.supabase_client:
        db_health = app_state.supabase_client.health_check()
        checks["database"] = db_health
    else:
        checks["database"] = {"status": "not_initialized", "connected": False}

    # Check Test Runner
    checks["test_runner"] = {
        "status": "ready" if app_state.test_runner else "not_initialized",
        "initialized": app_state.test_runner is not None,
    }

    # Determine overall status
    all_healthy = all(
        check.get("status") in ("healthy", "ready")
        for check in checks.values()
    )

    return health(
        status="healthy" if all_healthy else "degraded",
        version=app_state.version,
        checks=checks,
        request_id=request_id,
    )


@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint for load balancers."""
    return {"message": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}


# =============================================================================
# Testing Endpoints
# =============================================================================

@app.post("/api/v1/test/run", tags=["Testing"])
async def run_test(
    test_input: TestCaseInput,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """
    Run a single test case against an agent.

    Args:
        test_input: Test case configuration

    Returns:
        Test result with score and feedback
    """
    request_id = getattr(request.state, "request_id", None)

    if not app_state.is_ready:
        raise AIFactoryError(
            message="Service not ready",
            status_code=503,
        )

    async with OperationContext(
        "run_single_test",
        agent_id=test_input.agent_id,
        test_name=test_input.test_name,
    ) as ctx:
        with Timer() as timer:
            # Run test
            result = app_state.test_runner.run_single_test(
                agent_id=test_input.agent_id,
                test_case={
                    'name': test_input.test_name,
                    'input': test_input.input_text,
                    'expected_behavior': test_input.expected_behavior,
                    'rubric_focus': test_input.rubric_focus
                }
            )

        ctx.add_metric("score", result.get('score', 0.0))
        ctx.add_metric("execution_ms", timer.duration_ms)

        # Save result to Supabase in background
        if app_state.supabase_client:
            background_tasks.add_task(
                app_state.supabase_client.save_test_result,
                agent_version_id=test_input.agent_id,
                overall_score=result.get('score', 0.0),
                test_details=result,
                report_url="",
                test_duration_ms=int(timer.duration_ms),
            )

        return success(
            data=TestResult(
                test_id=result.get('test_id', f"test_{int(time.time() * 1000)}"),
                agent_id=test_input.agent_id,
                test_name=test_input.test_name,
                status="completed",
                score=result.get('score', 0.0),
                feedback=result.get('feedback', ''),
                execution_time_ms=timer.duration_ms,
                timestamp=datetime.now(timezone.utc),
            ).model_dump(),
            message="Test completed successfully",
            request_id=request_id,
        )


@app.post("/api/v1/test/batch", tags=["Testing"])
async def run_batch_tests(
    batch_input: BatchTestInput,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """
    Run multiple test cases in batch.

    Args:
        batch_input: Batch test configuration

    Returns:
        Batch job info with status endpoint
    """
    request_id = getattr(request.state, "request_id", None)

    if not app_state.is_ready:
        raise AIFactoryError(
            message="Service not ready",
            status_code=503,
        )

    run_id = f"batch_{int(time.time() * 1000)}"

    logger.info(
        "Batch test submitted",
        extra_fields={
            "run_id": run_id,
            "agent_id": batch_input.agent_id,
            "test_count": len(batch_input.test_cases),
        },
    )

    # Run tests asynchronously
    background_tasks.add_task(
        _execute_batch,
        run_id=run_id,
        agent_id=batch_input.agent_id,
        test_cases=batch_input.test_cases,
        run_name=batch_input.run_name,
    )

    return batch_job(
        job_id=run_id,
        status_endpoint=f"/api/v1/test/status/{run_id}",
        estimated_duration=len(batch_input.test_cases) * 5,
        request_id=request_id,
    )


@app.get("/api/v1/test/status/{run_id}", tags=["Testing"])
async def get_test_status(run_id: str, request: Request):
    """
    Get status of a batch test run.

    Args:
        run_id: Batch run identifier

    Returns:
        Status information and results
    """
    request_id = getattr(request.state, "request_id", None)

    if not app_state.supabase_client:
        raise AIFactoryError(
            message="Database not available",
            status_code=503,
        )

    # Note: You'll need to implement get_batch_status in supabase_client
    # For now, return a placeholder
    return success(
        data={
            "run_id": run_id,
            "status": "processing",
            "message": "Batch status endpoint - implement get_batch_status method",
        },
        request_id=request_id,
    )


# =============================================================================
# Agent Endpoints
# =============================================================================

@app.get("/api/v1/agents/{agent_id}/results", tags=["Agents"])
async def get_agent_results(
    agent_id: str,
    limit: int = 10,
    offset: int = 0,
    request: Request = None,
):
    """
    Get test results for an agent.

    Args:
        agent_id: Agent identifier
        limit: Number of results to return
        offset: Number of results to skip

    Returns:
        List of test results
    """
    request_id = getattr(request.state, "request_id", None) if request else None

    if not app_state.supabase_client:
        raise AIFactoryError(
            message="Database not available",
            status_code=503,
        )

    with LogContext(operation="get_agent_results", agent_id=agent_id):
        results = app_state.supabase_client.get_test_results_history(
            agent_version_id=agent_id,
            limit=limit,
        )

        return success(
            data={
                "agent_id": agent_id,
                "count": len(results),
                "results": results,
            },
            request_id=request_id,
        )


@app.get("/api/v1/metrics", tags=["Metrics"])
async def get_metrics(request: Request):
    """
    Get system metrics and performance stats.

    Returns:
        Performance and usage metrics
    """
    request_id = getattr(request.state, "request_id", None)

    uptime_seconds = None
    if app_state.startup_time:
        uptime_seconds = (datetime.now(timezone.utc) - app_state.startup_time).total_seconds()

    return success(
        data={
            "version": app_state.version,
            "uptime_seconds": uptime_seconds,
            "services": {
                "database": "connected" if app_state.supabase_client else "disconnected",
                "test_runner": "ready" if app_state.test_runner else "not_initialized",
            },
        },
        request_id=request_id,
    )


# =============================================================================
# Background Tasks
# =============================================================================

async def _execute_batch(
    run_id: str,
    agent_id: str,
    test_cases: list,
    run_name: Optional[str],
):
    """Execute batch tests in background with proper error handling."""
    with LogContext(operation="execute_batch", run_id=run_id, agent_id=agent_id):
        with Timer() as batch_timer:
            logger.info(
                "Starting batch execution",
                extra_fields={
                    "run_id": run_id,
                    "test_count": len(test_cases),
                },
            )

            results = []
            failed_count = 0

            for i, test_case in enumerate(test_cases):
                try:
                    with Timer() as test_timer:
                        result = app_state.test_runner.run_single_test(
                            agent_id=agent_id,
                            test_case={
                                'name': test_case.test_name,
                                'input': test_case.input_text,
                                'expected_behavior': test_case.expected_behavior,
                                'rubric_focus': test_case.rubric_focus
                            }
                        )
                        result['execution_time_ms'] = test_timer.duration_ms
                        results.append(result)

                    logger.debug(
                        f"Test {i+1}/{len(test_cases)} completed",
                        extra_fields={
                            "test_name": test_case.test_name,
                            "score": result.get('score', 0),
                            "duration_ms": test_timer.duration_ms,
                        },
                    )

                except Exception as e:
                    failed_count += 1
                    logger.error(
                        f"Test {i+1}/{len(test_cases)} failed",
                        extra_fields={
                            "test_name": test_case.test_name,
                            "error": str(e),
                        },
                    )
                    results.append({
                        'test_id': f"test_{i}",
                        'test_name': test_case.test_name,
                        'status': 'failed',
                        'error': str(e),
                    })

            # Calculate summary
            completed_count = len(test_cases) - failed_count
            avg_score = 0.0
            if completed_count > 0:
                scores = [r.get('score', 0) for r in results if 'score' in r]
                avg_score = sum(scores) / len(scores) if scores else 0.0

            logger.info(
                "Batch execution completed",
                extra_fields={
                    "run_id": run_id,
                    "total_tests": len(test_cases),
                    "completed": completed_count,
                    "failed": failed_count,
                    "avg_score": round(avg_score, 2),
                    "duration_ms": batch_timer.duration_ms,
                },
            )


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))

    logger.info(
        "Starting server",
        extra_fields={"host": host, "port": port},
    )

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
