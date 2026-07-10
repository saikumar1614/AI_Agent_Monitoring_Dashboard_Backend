import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.auth.auth_routes import router as auth_router
from api.agents.agent_routes import router as agent_router
from api.executions.execution_routes import router as execution_router
from api.langfuse.langfuse_routes import router as langfuse_router
from api.dashboard.dashboard_routes import router as dashboard_router
from api.live.live_routes import router as live_router
from api.tool_usage.tool_usage_routes import router as tool_usage_router
from api.failures.failure_routes import router as failure_router
from api.analytics.analytics_routes import router as analytics_router
from core.config import settings
from database.base import Base
from database.connection import engine
from models.user import User  # noqa: F401
from models.agent import Agent  # noqa: F401
from models.execution import Execution  # noqa: F401
from models.tool_usage import ToolUsage  # noqa: F401
from models.failure import Failure  # noqa: F401
from telemetry.opentelemetry_config import configure_telemetry

# Create tables on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME}")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

configure_telemetry(app, db_engine=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(execution_router)
app.include_router(langfuse_router)
app.include_router(dashboard_router)
app.include_router(live_router)
app.include_router(tool_usage_router)
app.include_router(failure_router)
app.include_router(analytics_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
