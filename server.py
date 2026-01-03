#!/usr/bin/env python3
"""
AI Factory Testing Framework - FastAPI Server
==============================================
REST API para gerenciar testes de agentes IA.
"""

import os
import logging
import asyncio
import time
import platform
import psutil
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import yaml
from dotenv import load_dotenv

from src.supabase_client import SupabaseClient
from src.test_runner import TestRunner
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate Limiter - usa IP do cliente como identificador
limiter = Limiter(key_func=get_remote_address)

# Métricas globais de uptime
START_TIME = datetime.utcnow()

config_path = Path(__file__).parent / 'config.yaml'
try:
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)
except Exception as e:
    logger.warning(f"Could not load config.yaml: {e}")
    yaml_config = {}

API_KEY = os.getenv('API_KEY', 'your-secret-api-key-here-change-me')

try:
    supabase = SupabaseClient()
    evaluator = Evaluator()
    report_generator = ReportGenerator()
    logger.info("All clients initialized")
except Exception as e:
    logger.error(f"Failed to initialize clients: {e}")
    supabase = evaluator = report_generator = None

app = FastAPI(title="AI Factory Testing Framework API", description="REST API para testes automatizados de agentes IA", version="1.0.0")

# Adiciona Rate Limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class TestAgentRequest(BaseModel):
    agent_version_id: str = Field(..., description="UUID do agent_version")
    @validator('agent_version_id')
    def validate_uuid(cls, v):
        if not v or len(v) < 32:
            raise ValueError('agent_version_id must be a valid UUID')
        return v

class TestAgentResponse(BaseModel):
    status: str
    agent_id: str
    message: str

class AgentSummary(BaseModel):
    id: str
    name: str
    mode: str
    version: int
    status: str
    last_test_score: Optional[float] = None
    last_test_at: Optional[str] = None
    framework_approved: Optional[bool] = None

class AgentDetail(BaseModel):
    id: str
    name: str
    mode: str
    version: int
    status: str
    system_prompt: Optional[str] = None
    last_test_score: Optional[float] = None
    last_test_at: Optional[str] = None
    test_report_url: Optional[str] = None
    framework_approved: Optional[bool] = None
    total_tests: int = 0
    latest_test: Optional[Dict] = None

class SkillRequest(BaseModel):
    instructions: str = Field(..., description="INSTRUCTIONS.md")
    examples: Optional[str] = None
    rubric: Optional[str] = None
    test_cases: Optional[List[Dict]] = None
    local_file_path: Optional[str] = None

class SkillResponse(BaseModel):
    skill_id: str
    version: int
    message: str

class TestResultDetail(BaseModel):
    id: str
    agent_version_id: str
    overall_score: float
    test_details: Dict
    report_url: Optional[str] = None
    test_duration_ms: int
    evaluator_model: str
    created_at: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    supabase_connected: bool
    uptime_seconds: float
    environment: str
    memory_usage_mb: Optional[float] = None
    cpu_percent: Optional[float] = None

class HealthDetailedResponse(HealthResponse):
    python_version: str
    platform: str
    host: Optional[str] = None
    dependencies: Dict[str, str] = {}

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedTestResults(BaseModel):
    data: List[TestResultDetail]
    meta: PaginationMeta

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key. Include 'X-API-Key' header.")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key

async def run_agent_test_background(agent_id: str):
    try:
        logger.info(f"Starting background test for agent {agent_id}")
        test_runner = TestRunner(supabase_client=supabase, evaluator=evaluator, report_generator=report_generator)
        result = await test_runner.run_tests(agent_id)
        logger.info(f"Test completed for agent {agent_id}: score={result.get('overall_score')}")
    except Exception as e:
        logger.error(f"Error running test for agent {agent_id}: {e}", exc_info=True)

def get_system_metrics():
    """Coleta métricas do sistema"""
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)
        return memory_mb, cpu_percent
    except Exception:
        return None, None

@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check básico - não requer autenticação"""
    supabase_ok = False
    try:
        if supabase:
            test_query = supabase.client.table('agent_versions').select('id').limit(1).execute()
            supabase_ok = True
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")

    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    memory_mb, cpu_percent = get_system_metrics()
    env = os.getenv('ENVIRONMENT', os.getenv('RAILWAY_ENVIRONMENT', 'development'))

    return HealthResponse(
        status="healthy" if supabase_ok else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        supabase_connected=supabase_ok,
        uptime_seconds=uptime,
        environment=env,
        memory_usage_mb=round(memory_mb, 2) if memory_mb else None,
        cpu_percent=round(cpu_percent, 2) if cpu_percent else None
    )

@app.get("/health/detailed", response_model=HealthDetailedResponse, tags=["Health"])
@limiter.limit("10/minute")
async def health_check_detailed(request: Request, x_api_key: str = Header(..., alias="X-API-Key")):
    """Health check detalhado - requer autenticação"""
    await verify_api_key(x_api_key)

    supabase_ok = False
    try:
        if supabase:
            test_query = supabase.client.table('agent_versions').select('id').limit(1).execute()
            supabase_ok = True
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")

    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    memory_mb, cpu_percent = get_system_metrics()
    env = os.getenv('ENVIRONMENT', os.getenv('RAILWAY_ENVIRONMENT', 'development'))

    # Versões das dependências principais
    import fastapi
    import anthropic
    deps = {
        "fastapi": fastapi.__version__,
        "anthropic": anthropic.__version__,
        "python": platform.python_version()
    }

    return HealthDetailedResponse(
        status="healthy" if supabase_ok else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        supabase_connected=supabase_ok,
        uptime_seconds=uptime,
        environment=env,
        memory_usage_mb=round(memory_mb, 2) if memory_mb else None,
        cpu_percent=round(cpu_percent, 2) if cpu_percent else None,
        python_version=platform.python_version(),
        platform=platform.platform(),
        host=os.getenv('RAILWAY_PUBLIC_DOMAIN', os.getenv('HOST', 'localhost')),
        dependencies=deps
    )

@app.get("/ping", tags=["Health"])
@limiter.limit("120/minute")
async def ping(request: Request):
    """Ping simples para load balancers - sem autenticação"""
    return {"pong": True, "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/test-agent", response_model=TestAgentResponse, tags=["Testing"])
@limiter.limit("10/minute")
async def test_agent(request: Request, body: TestAgentRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")
    agent = supabase.get_agent_version(body.agent_version_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {body.agent_version_id} not found")
    background_tasks.add_task(run_agent_test_background, body.agent_version_id)
    return TestAgentResponse(status="queued", agent_id=body.agent_version_id, message=f"Test queued for agent '{agent.get('name')}'")

@app.get("/api/test-results/{test_id}", response_model=TestResultDetail, tags=["Testing"])
@limiter.limit("60/minute")
async def get_test_result(request: Request, test_id: str, x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")
    try:
        result = supabase.client.table('agenttest_test_results').select('*').eq('id', test_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Test result {test_id} not found")
        return TestResultDetail(**result.data)
    except Exception as e:
        logger.error(f"Error fetching test result {test_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents", response_model=List[AgentSummary], tags=["Agents"])
@limiter.limit("30/minute")
async def list_agents(request: Request, limit: int = 100, status_filter: Optional[str] = None, x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")
    try:
        query = supabase.client.table('agent_versions').select('id, name, mode, version, status, last_test_score, last_test_at, framework_approved').order('last_test_at', desc=True).limit(limit)
        if status_filter:
            query = query.eq('status', status_filter)
        response = query.execute()
        agents = [AgentSummary(**agent) for agent in response.data]
        return agents
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/{agent_id}", response_model=AgentDetail, tags=["Agents"])
@limiter.limit("60/minute")
async def get_agent_details(request: Request, agent_id: str, x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")
    agent = supabase.get_agent_version(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    tests = supabase.get_test_results_history(agent_id, limit=1)
    latest_test = tests[0] if tests else None
    total_tests_response = supabase.client.table('agenttest_test_results').select('id', count='exact').eq('agent_version_id', agent_id).execute()
    total_tests = total_tests_response.count or 0
    return AgentDetail(id=agent['id'], name=agent['name'], mode=agent['mode'], version=agent['version'], status=agent['status'], system_prompt=agent.get('system_prompt'), last_test_score=agent.get('last_test_score'), last_test_at=agent.get('last_test_at'), test_report_url=agent.get('test_report_url'), framework_approved=agent.get('framework_approved'), total_tests=total_tests, latest_test=latest_test)

@app.get("/api/agent/{agent_id}/tests", response_model=PaginatedTestResults, tags=["Agents"])
@limiter.limit("30/minute")
async def get_agent_test_history(
    request: Request,
    agent_id: str,
    page: int = 1,
    per_page: int = 20,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """Retorna histórico de testes com paginação completa"""
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")

    # Validação de parâmetros
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    if per_page > 100:
        per_page = 100  # Limite máximo

    agent = supabase.get_agent_version(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    # Conta total de registros
    count_response = supabase.client.table('agenttest_test_results')\
        .select('id', count='exact')\
        .eq('agent_version_id', agent_id)\
        .execute()
    total = count_response.count or 0

    # Calcula offset
    offset = (page - 1) * per_page

    # Busca resultados paginados
    tests = supabase.get_test_results_history_paginated(agent_id, limit=per_page, offset=offset)

    # Calcula metadados de paginação
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return PaginatedTestResults(
        data=[TestResultDetail(**test) for test in tests],
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )

@app.get("/api/agent/{agent_id}/skill", tags=["Skills"])
@limiter.limit("60/minute")
async def get_agent_skill(request: Request, agent_id: str, x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")
    agent = supabase.get_agent_version(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    skill = supabase.get_skill(agent_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"No skill found for agent {agent_id}")
    return skill

@app.post("/api/agent/{agent_id}/skill", response_model=SkillResponse, tags=["Skills"])
@limiter.limit("20/minute")
async def create_or_update_skill(request: Request, agent_id: str, body: SkillRequest, x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not initialized")
    agent = supabase.get_agent_version(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    try:
        skill_id = supabase.save_skill(agent_version_id=agent_id, instructions=body.instructions, examples=body.examples, rubric=body.rubric, test_cases=body.test_cases, local_file_path=body.local_file_path)
        skill = supabase.get_skill(agent_id)
        return SkillResponse(skill_id=skill_id, version=skill['version'], message=f"Skill v{skill['version']} created successfully")
    except Exception as e:
        logger.error(f"Error creating skill for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": True, "detail": exc.detail, "timestamp": datetime.utcnow().isoformat()})

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": True, "detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()})

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("AI Factory Testing Framework API")
    logger.info("=" * 50)
    logger.info(f"Supabase: {'Connected' if supabase else 'Disconnected'}")
    logger.info(f"Config: {config_path}")
    logger.info("API Key: ENABLED")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API...")

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get('HOST', yaml_config.get('server', {}).get('host', '0.0.0.0'))
    port = int(os.environ.get('PORT', yaml_config.get('server', {}).get('port', 8000)))
    reload = yaml_config.get('server', {}).get('reload', False)  # Disable reload in production
    logger.info(f"Starting server at {host}:{port} (ENV PORT: {os.environ.get('PORT', 'not set')})")
    uvicorn.run("server:app", host=host, port=port, reload=reload, log_level="info")
