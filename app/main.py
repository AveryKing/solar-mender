from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

from app.api.router import api_router
from app.core.config import settings
from app.db.base import engine, Base
from app.core.logging import configure_logging
from app.core.agents import register_agents

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors and the request body."""
    body = await request.body()
    logger.error(f"Validation error: {exc.errors()}")
    logger.error(f"Request body: {body.decode()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode()},
    )

# Configure logging
configure_logging()

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup.
    """
    try:
        # Register agents
        register_agents()
    except Exception as e:
        logger.error(f"Agent registration failed: {e}", exc_info=True)
        # Don't crash the app if agent registration fails
        # Agents can be registered later if needed
    
    try:
        # Initialize database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        # In production, you might want to exit or retry

@app.get("/")
async def root():
    """Root endpoint redirection or info."""
    return {
        "message": "Welcome to Diviora Systems CI/CD Repair Agent",
        "docs": "/docs"
    }
