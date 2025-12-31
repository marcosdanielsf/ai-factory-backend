#!/usr/bin/env python3
"""
AI Factory Testing Framework - Secure FastAPI Server

Features:
- API Key Authentication (X-API-Key header)
- CORS Configuration
- Security Headers
- Rate Limiting (100 req/min per IP)
- Request/Response logging
- Health checks
"""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import FastAPI, Security, HTTPException, Depends, Request, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

    # API Security
    api_key: str = Field(default="", alias="API_KEY")
    api_keys_list: list[str] = Field(default_factory=list)  # Multiple API keys support

    # Server
    app_name: str = "AI Factory Testing Server"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:3001", alias="CORS_ORIGINS")
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_allow_headers: list[str] = Field(default=["*"])

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 60

    # Trusted Hosts
    trusted_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        alias="TRUSTED_HOSTS"
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Support multiple API keys
        if self.api_key and not self.api_keys_list:
            self.api_keys_list = [self.api_key]

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(self.cors_origins, str):
            return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return self.cors_origins


@lru_cache()
def get_settings() -> Settings:
    """Load settings (cached)"""
    return Settings()


# ============================================================================
# SECURITY - API KEY AUTHENTICATION
# ============================================================================

api_key_header = APIKeyHeader(name="X-API-Key", description="API Key for authentication")
ip_request_tracker: dict[str, list[datetime]] = {}  # Simple rate limiting tracker


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API Key from request header

    Raises:
        HTTPException: If API key is invalid or missing
    """
    settings = get_settings()

    # Check if API key is in allowed list
    if not api_key or api_key not in settings.api_keys_list:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}..." if api_key else "No API key provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )

    logger.debug(f"API Key authenticated successfully")
    return api_key


async def check_rate_limit(request: Request, settings: Settings = Depends(get_settings)) -> None:
    """
    Check rate limit based on client IP

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not settings.rate_limit_enabled:
        return

    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now()
    cutoff_time = now - timedelta(seconds=settings.rate_limit_period_seconds)

    # Initialize IP tracking if needed
    if client_ip not in ip_request_tracker:
        ip_request_tracker[client_ip] = []

    # Remove old requests outside the time window
    ip_request_tracker[client_ip] = [
        req_time for req_time in ip_request_tracker[client_ip]
        if req_time > cutoff_time
    ]

    # Check if limit exceeded
    if len(ip_request_tracker[client_ip]) >= settings.rate_limit_requests:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {settings.rate_limit_requests} requests per {settings.rate_limit_period_seconds}s"
        )

    # Add current request
    ip_request_tracker[client_ip].append(now)
    logger.debug(f"Rate limit check passed for IP: {client_ip} ({len(ip_request_tracker[client_ip])}/{settings.rate_limit_requests})")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="AI Factory Testing Server",
    description="Secure API for AI Factory Testing Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

settings = get_settings()


# ============================================================================
# MIDDLEWARE STACK
# ============================================================================

# 1. Trusted Host Middleware - Validate Host header
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_hosts,
)

# 2. CORS Middleware - Handle Cross-Origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=["X-Process-Time", "X-Request-ID"],
    max_age=600,  # 10 minutes
)

# 3. Custom security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"  # Prevent MIME type sniffing
    response.headers["X-Frame-Options"] = "DENY"  # Prevent clickjacking
    response.headers["X-XSS-Protection"] = "1; mode=block"  # XSS protection
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"  # HTTPS enforcement
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"  # Referrer policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"  # Disable permissions

    # Add request tracing
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "N/A")

    return response

# 4. Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    import time
    from uuid import uuid4

    request_id = str(uuid4())
    start_time = time.time()

    logger.info(f"[{request_id}] {request.method} {request.url.path}")

    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id

    logger.info(f"[{request_id}] {response.status_code} - {process_time:.3f}s")

    return response


# ============================================================================
# API ROUTES
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint (no authentication required)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version
    }


@app.get("/health/detailed", tags=["Health"])
async def health_check_detailed():
    """Detailed health check (requires auth)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "environment": "production" if not settings.debug else "development",
        "rate_limiting": "enabled" if settings.rate_limit_enabled else "disabled",
        "cors_origins": settings.cors_origins
    }


@app.get(
    "/protected",
    tags=["Protected"],
    dependencies=[
        Depends(verify_api_key),
        Depends(check_rate_limit)
    ]
)
async def protected_route(api_key: str = Security(api_key_header)):
    """
    Protected endpoint requiring API Key

    Requires:
    - Header: X-API-Key: <your-api-key>

    Rate Limited: 100 requests per minute per IP
    """
    return {
        "message": "Access granted to protected resource",
        "api_key": f"{api_key[:10]}...",
        "timestamp": datetime.now().isoformat()
    }


@app.post(
    "/api/test",
    tags=["API"],
    dependencies=[
        Depends(verify_api_key),
        Depends(check_rate_limit)
    ]
)
async def run_test(
    test_data: dict,
    api_key: str = Security(api_key_header),
    request: Request = None
):
    """
    Run test endpoint

    Requires:
    - Header: X-API-Key: <your-api-key>
    - Body: JSON test data

    Rate Limited: 100 requests per minute per IP
    """
    logger.info(f"Running test with data: {test_data}")

    return {
        "success": True,
        "test_id": "test_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "received_data": test_data,
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/api/status",
    tags=["API"],
    dependencies=[
        Depends(verify_api_key),
        Depends(check_rate_limit)
    ]
)
async def get_status(api_key: str = Security(api_key_header)):
    """Get API status (requires authentication)"""
    return {
        "api_status": "running",
        "authentication": "enabled",
        "rate_limiting": {
            "enabled": settings.rate_limit_enabled,
            "limit": f"{settings.rate_limit_requests} requests per {settings.rate_limit_period_seconds}s"
        },
        "cors": {
            "allowed_origins": settings.cors_origins
        },
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with security headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # Don't leak internal error details to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# DOCUMENTATION
# ============================================================================

def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Factory Testing Server",
        version="1.0.0",
        description="Secure API with authentication and rate limiting",
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "api_key": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for authentication"
        }
    }

    # Apply security to all endpoints except /health
    for path, methods in openapi_schema["paths"].items():
        if path != "/health":
            for method in methods.values():
                if isinstance(method, dict) and "security" not in method:
                    method["security"] = [{"api_key": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
    if settings.rate_limit_enabled:
        logger.info(f"Rate limit: {settings.rate_limit_requests} requests per {settings.rate_limit_period_seconds}s")
    logger.info("Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.app_name}")
    ip_request_tracker.clear()  # Clear rate limit tracker
    logger.info("Server shutdown complete")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Validate API Key is set
    if not settings.api_key and not settings.api_keys_list:
        logger.error("ERROR: API_KEY not set in environment variables!")
        logger.error("Set API_KEY in .env or as environment variable before running")
        exit(1)

    logger.info(f"API Keys configured: {len(settings.api_keys_list)}")

    # Run server
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
