"""
AI Factory Backend API - FastAPI Application
============================================
High-performance API for AI testing framework deployed on Railway.

Features:
- Connection pooling with asyncpg
- In-memory caching with TTL
- Soft delete support
- Background task processing
"""

import os
import json
import logging
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from src.supabase_client import SupabaseClient
from src.test_runner import TestRunner
from src.evaluator import Evaluator
from src.database import DatabaseManager, get_database_manager, close_database_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global instances
supabase_client: Optional[SupabaseClient] = None
test_runner: Optional[TestRunner] = None
db_manager: Optional[DatabaseManager] = None
cache_cleanup_task: Optional[asyncio.Task] = None


async def periodic_cache_cleanup():
    """Tarefa de limpeza periódica do cache."""
    while True:
        try:
            await asyncio.sleep(300)  # A cada 5 minutos
            if db_manager:
                count = await db_manager.cleanup_expired_cache()
                if count > 0:
                    logger.info(f"Cache cleanup: removed {count} expired entries")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    global supabase_client, test_runner, db_manager, cache_cleanup_task

    # Startup
    logger.info("Starting AI Factory API...")
    try:
        # Initialize DatabaseManager (connection pool + cache)
        db_manager = await get_database_manager()
        logger.info("DatabaseManager initialized (pool + cache)")

        # Initialize Supabase client (fallback)
        supabase_client = SupabaseClient()
        logger.info("Supabase client initialized")

        # Initialize test runner
        test_runner = TestRunner()
        logger.info("Test runner initialized")

        # Start periodic cache cleanup
        cache_cleanup_task = asyncio.create_task(periodic_cache_cleanup())
        logger.info("Cache cleanup task started")

    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Factory API...")

    # Cancel cache cleanup task
    if cache_cleanup_task:
        cache_cleanup_task.cancel()
        try:
            await cache_cleanup_task
        except asyncio.CancelledError:
            pass

    # Close database connections
    await close_database_manager()
    logger.info("Database connections closed")


# Initialize FastAPI app
app = FastAPI(
    title="AI Factory API",
    description="High-performance testing framework for AI agents",
    version="1.0.0",
    lifespan=lifespan
)


# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Pydantic models
class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    database: str
    pool: Optional[Dict[str, Any]] = None
    cache: Optional[Dict[str, Any]] = None


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
    execution_time: float
    timestamp: datetime


class BatchTestInput(BaseModel):
    """Batch test input model."""
    agent_id: str
    test_cases: list[TestCaseInput]
    run_name: Optional[str] = None


# API Routes

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint with pool and cache stats.

    Returns:
        HealthCheckResponse with status, version, pool and cache info
    """
    try:
        pool_stats = None
        cache_stats = None

        # Check DatabaseManager health
        if db_manager:
            health = await db_manager.healthcheck()
            db_status = health.get("status", "unknown")
            pool_stats = health.get("pool")
            cache_stats = health.get("cache")
        elif supabase_client:
            supabase_client.ping()
            db_status = "connected"
        else:
            db_status = "not_initialized"

        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database=db_status,
            pool=pool_stats,
            cache=cache_stats
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint for load balancers."""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/v1/test/run", response_model=TestResult, tags=["Testing"])
async def run_test(
    test_input: TestCaseInput,
    background_tasks: BackgroundTasks
):
    """
    Run a single test case against an agent.

    Args:
        test_input: Test case configuration
        background_tasks: Background task runner

    Returns:
        TestResult with score and feedback
    """
    if not test_runner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Test runner not initialized"
        )

    try:
        start_time = time.time()

        # Run test
        result = test_runner.run_single_test(
            agent_id=test_input.agent_id,
            test_case={
                'name': test_input.test_name,
                'input': test_input.input_text,
                'expected_behavior': test_input.expected_behavior,
                'rubric_focus': test_input.rubric_focus
            }
        )

        execution_time = time.time() - start_time

        # Save result to Supabase
        if supabase_client:
            background_tasks.add_task(
                supabase_client.save_test_result,
                agent_id=test_input.agent_id,
                result=result,
                execution_time=execution_time
            )

        return TestResult(
            test_id=result.get('test_id', 'unknown'),
            agent_id=test_input.agent_id,
            test_name=test_input.test_name,
            status="completed",
            score=result.get('score', 0.0),
            feedback=result.get('feedback', ''),
            execution_time=execution_time,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution failed: {str(e)}"
        )


@app.post("/api/v1/test/batch", tags=["Testing"])
async def run_batch_tests(
    batch_input: BatchTestInput,
    background_tasks: BackgroundTasks
):
    """
    Run multiple test cases in batch.

    Args:
        batch_input: Batch test configuration
        background_tasks: Background task runner

    Returns:
        Batch job info with status endpoint
    """
    if not test_runner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Test runner not initialized"
        )

    try:
        run_id = f"batch_{int(time.time() * 1000)}"

        # Store batch info in Supabase
        if supabase_client:
            background_tasks.add_task(
                supabase_client.save_batch_job,
                run_id=run_id,
                agent_id=batch_input.agent_id,
                test_count=len(batch_input.test_cases),
                status="processing"
            )

        # Run tests asynchronously
        background_tasks.add_task(
            _execute_batch,
            run_id=run_id,
            agent_id=batch_input.agent_id,
            test_cases=batch_input.test_cases,
            run_name=batch_input.run_name
        )

        return {
            "run_id": run_id,
            "agent_id": batch_input.agent_id,
            "test_count": len(batch_input.test_cases),
            "status": "queued",
            "status_endpoint": f"/api/v1/test/status/{run_id}",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Batch test submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch test submission failed: {str(e)}"
        )


@app.get("/api/v1/test/status/{run_id}", tags=["Testing"])
async def get_test_status(run_id: str):
    """
    Get status of a batch test run.

    Args:
        run_id: Batch run identifier

    Returns:
        Status information and results
    """
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    try:
        status_info = supabase_client.get_batch_status(run_id)
        return status_info
    except Exception as e:
        logger.error(f"Failed to retrieve status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}"
        )


@app.get("/api/v1/agents/{agent_id}/results", tags=["Agents"])
async def get_agent_results(
    agent_id: str,
    limit: int = 10,
    offset: int = 0
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
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    try:
        results = supabase_client.get_agent_results(
            agent_id=agent_id,
            limit=limit,
            offset=offset
        )
        return {
            "agent_id": agent_id,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to retrieve results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve results: {str(e)}"
        )


@app.get("/api/v1/metrics", tags=["Metrics"])
async def get_metrics():
    """
    Get system metrics and performance stats.

    Returns:
        Performance and usage metrics
    """
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    try:
        metrics = supabase_client.get_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Failed to retrieve metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


# ============================================
# ADMIN ENDPOINTS (Cache & Pool Management)
# ============================================

@app.get("/api/v1/admin/stats", tags=["Admin"])
async def get_admin_stats():
    """
    Get detailed database pool and cache statistics.

    Returns:
        Pool and cache stats for monitoring
    """
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DatabaseManager not available"
        )

    try:
        health = await db_manager.healthcheck()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": health,
            "pool": db_manager.pool.get_stats(),
            "cache": db_manager._cache.get_stats()
        }
    except Exception as e:
        logger.error(f"Failed to get admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/admin/cache/clear", tags=["Admin"])
async def clear_cache(namespace: Optional[str] = None):
    """
    Clear cache entries.

    Args:
        namespace: Optional namespace to clear (all if not specified)

    Returns:
        Number of entries cleared
    """
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DatabaseManager not available"
        )

    try:
        count = await db_manager.clear_cache(namespace)
        return {
            "success": True,
            "cleared": count,
            "namespace": namespace or "all",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/admin/cache/namespaces", tags=["Admin"])
async def get_cache_namespaces():
    """
    List all cache namespaces and their entry counts.

    Returns:
        Dict of namespace -> count
    """
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DatabaseManager not available"
        )

    try:
        # Get all cache keys and group by namespace
        namespaces: Dict[str, int] = {}
        for key in db_manager._cache._cache.keys():
            ns = key.split(":")[0] if ":" in key else "default"
            namespaces[ns] = namespaces.get(ns, 0) + 1

        return {
            "namespaces": namespaces,
            "total_entries": sum(namespaces.values()),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache namespaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Background task helper
async def _execute_batch(
    run_id: str,
    agent_id: str,
    test_cases: list,
    run_name: Optional[str]
):
    """Execute batch tests in background."""
    try:
        logger.info(f"Starting batch execution: {run_id}")

        results = []
        for i, test_case in enumerate(test_cases):
            try:
                result = test_runner.run_single_test(
                    agent_id=agent_id,
                    test_case={
                        'name': test_case.test_name,
                        'input': test_case.input_text,
                        'expected_behavior': test_case.expected_behavior,
                        'rubric_focus': test_case.rubric_focus
                    }
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Test {i} failed: {e}")
                results.append({'test_id': f"test_{i}", 'error': str(e)})

        # Update batch status
        if supabase_client:
            supabase_client.save_batch_results(
                run_id=run_id,
                results=results,
                status="completed"
            )

        logger.info(f"Batch execution completed: {run_id}")

    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        if supabase_client:
            supabase_client.save_batch_results(
                run_id=run_id,
                results=[],
                status="failed",
                error=str(e)
            )


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    workers = int(os.getenv("GUNICORN_WORKERS", 4))

    logger.info(f"Starting server on {host}:{port} with {workers} workers")

    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )
