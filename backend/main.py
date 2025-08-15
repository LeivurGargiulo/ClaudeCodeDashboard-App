"""
Claude Code Dashboard - FastAPI Backend

A web dashboard for managing and interacting with multiple Claude Code instances,
both local and containerized, with support for remote access via Tailscale.
"""

import os
import logging
import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

from models.instance import Instance, InstanceCreate, InstanceUpdate
from models.chat import ChatMessage, ChatResponse
from auth import verify_token
from services.instance_service import InstanceService
from logging_config import setup_default_logging, get_loggers, LoggerMixin
import structlog

# Setup comprehensive logging
setup_default_logging()
logger = structlog.get_logger(__name__)
loggers = get_loggers()

# Security
security = HTTPBearer(auto_error=False)

# Global services
instance_service = InstanceService()

# Import and create global Docker manager
from docker_manager import DockerManager
docker_manager = DockerManager()

# Import routers after creating docker_manager
from routers import instances, chat, docker, usage

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting Claude Code Dashboard...")
    
    # Load existing instances from config if available
    await instance_service.load_instances()
    
    # Auto-discover Docker containers running Claude Code
    await instance_service.discover_docker_instances()
    
    yield
    
    logger.info("Shutting down Claude Code Dashboard...")
    # Save instance configurations
    await instance_service.save_instances()

# Create FastAPI application
app = FastAPI(
    title="Claude Code Dashboard",
    description="A web dashboard for managing multiple Claude Code instances",
    version="1.1.0",
    lifespan=lifespan
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing and error handling."""
    return await loggers['request'].log_request(request, call_next)

# CORS middleware for frontend access
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set Docker manager in the router to avoid circular imports
docker.set_docker_manager(docker_manager)

# Include routers
app.include_router(instances.router, prefix="/api/instances", tags=["instances"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(docker.router, prefix="/api/docker", tags=["docker"])
app.include_router(usage.router, prefix="/api", tags=["usage"])

@app.get("/")
async def root():
    """Root endpoint with basic application info."""
    return {
        "name": "Claude Code Dashboard",
        "version": "1.1.0",
        "description": "Web dashboard for managing Claude Code instances"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    import datetime
    try:
        instances_count = len(await instance_service.get_all_instances())
    except Exception:
        instances_count = 0
    
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "instances_count": instances_count
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")  # Bind to all interfaces for Tailscale
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )