from fastapi import APIRouter
from app.api import webhook, worker, metrics, agents, mcp, resources

api_router = APIRouter()

# Include webhook routes
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhooks"])

# Include worker routes (Internal, protected by Cloud Tasks)
api_router.include_router(worker.router, prefix="/worker", tags=["workers"])

# Include metrics routes
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

# Include agent discovery routes
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Include MCP tool handler routes
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# Include MCP resource routes
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
