from fastapi import APIRouter
from app.api import webhook, worker

api_router = APIRouter()

# Include webhook routes
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhooks"])

# Include worker routes (Internal, protected by Cloud Tasks)
api_router.include_router(worker.router, prefix="/worker", tags=["workers"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
