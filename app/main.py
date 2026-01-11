from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.db.base import engine, Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on startup (for local development).
    In production, migrations should be handled by Alembic.
    """
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    """Root endpoint redirection or info."""
    return {
        "message": "Welcome to Diviora Systems CI/CD Repair Agent",
        "docs": "/docs"
    }
