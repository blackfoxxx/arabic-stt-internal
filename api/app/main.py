"""
Arabic STT SaaS - FastAPI Main Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
import time
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import get_settings
from app.core.database import create_tables
from app.core.redis import init_redis, close_redis
from app.core.storage import init_minio
from app.api.v1.router import api_router
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityMiddleware

# Configure structured logging
logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')

settings = get_settings()

# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration(auto_enabling_integrations=False)],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Arabic STT SaaS API", version="1.0.0", environment=settings.ENVIRONMENT)
    
    # Initialize database
    await create_tables()
    logger.info("Database tables created/verified")
    
    # Initialize Redis
    await init_redis()
    logger.info("Redis connection initialized")
    
    # Initialize MinIO
    await init_minio()
    logger.info("MinIO storage initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Arabic STT SaaS API")
    await close_redis()


# Create FastAPI app
app = FastAPI(
    title="Arabic STT SaaS API",
    description="Professional Arabic Speech-to-Text platform with advanced editing capabilities",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "media", 
            "description": "Media file upload and management"
        },
        {
            "name": "jobs",
            "description": "Transcription job management"
        },
        {
            "name": "transcripts",
            "description": "Transcript viewing and editing"
        },
        {
            "name": "exports",
            "description": "Export transcripts to various formats"
        },
        {
            "name": "usage",
            "description": "Usage tracking and billing"
        },
        {
            "name": "webhooks",
            "description": "Webhook management and delivery"
        },
        {
            "name": "admin",
            "description": "Administrative endpoints"
        }
    ]
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    # Add response headers
    response.headers["X-Process-Time"] = str(duration)
    
    return response


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "Arabic STT SaaS API",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/health/detailed", tags=["health"])
async def detailed_health_check():
    """Detailed health check with dependencies"""
    from app.core.database import get_db_health
    from app.core.redis import get_redis_health
    from app.core.storage import get_storage_health
    
    health_status = {
        "status": "healthy",
        "service": "Arabic STT SaaS API",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {}
    }
    
    try:
        # Check database
        db_healthy = await get_db_health()
        health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
        
        # Check Redis
        redis_healthy = await get_redis_health()
        health_status["checks"]["redis"] = "healthy" if redis_healthy else "unhealthy"
        
        # Check storage
        storage_healthy = await get_storage_health()
        health_status["checks"]["storage"] = "healthy" if storage_healthy else "unhealthy"
        
        # Overall status
        all_healthy = all(
            status == "healthy" 
            for status in health_status["checks"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status


@app.get("/metrics", tags=["monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": "The requested resource was not found",
            "path": request.url.path
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error("Internal server error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


# Include API routes
app.include_router(api_router, prefix="/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )