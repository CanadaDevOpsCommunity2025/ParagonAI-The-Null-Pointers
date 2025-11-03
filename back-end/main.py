# back-end/main.py
from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.routers import grok, agents, deployments, metrics, generate, health, auth
from app.database import init_db, close_db
from app.tasks.metrics_collector import start_metrics_collector, stop_metrics_collector
from app.services.grok_service import GroqService
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    print("🚀 Starting ParagonAI Backend...")
    await init_db()
    print("✅ Database initialized")
    await start_metrics_collector()
    print("✅ Background tasks started")
    
    try:
        async with GroqService() as service:
            print("Groq service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Groq service: {str(e)}")
        if not settings.DEBUG:
            raise RuntimeError("Failed to initialize Groq service") from e
    yield
    
    print("Stopping background tasks...")
    await stop_metrics_collector()
    print("Shutting down ParagonAI Backend...")
    await close_db()

app = FastAPI(
    title="ParagonAI API",
    description="Backend API for AI agent deployment and management",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com"]  # Update in production
)

if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
app.include_router(generate.router, prefix="/api/v1", tags=["Generation"])
app.include_router(deployments.router, prefix="/api/v1", tags=["Deployments"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])
app.include_router(grok.router, prefix="/api/v1", tags=["Groq"])

@app.get("/")
async def root():
    return {
        "message": "ParagonAI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )