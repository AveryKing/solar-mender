from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.db.base import engine, Base
from app.core.logging import configure_logging

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure logging
configure_logging()

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # In a real app, we might want to exit or log this properly

@app.get("/")
async def root():
    """Root endpoint redirection or info."""
    return {
        "message": "Welcome to Diviora Systems CI/CD Repair Agent",
        "docs": "/docs"
    }
