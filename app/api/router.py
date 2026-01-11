from fastapi import APIRouter
from app.api import webhook, worker, metrics, agents

api_router = APIRouter()

# Include webhook routes
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhooks"])

# Include worker routes (Internal, protected by Cloud Tasks)
api_router.include_router(worker.router, prefix="/worker", tags=["workers"])

# Include metrics routes
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

# Include agent discovery routes
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
