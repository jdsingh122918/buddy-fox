"""
Buddy Fox Backend API - FastAPI Application
Main application entry point.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .api import query, session, stats, webcast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Buddy Fox API",
    description="AI Web Browsing Agent API with real-time streaming",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Primary frontend port
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default (backup)
        "http://localhost:5174",  # Alternative Vite port (backup)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(query.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(webcast.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Buddy Fox API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/health",
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("=" * 60)
    logger.info(f"🦊 Buddy Fox API v{__version__} starting...")
    logger.info("=" * 60)

    try:
        # Initialize agent service
        from .services.agent_service import get_agent_service

        agent_service = get_agent_service()
        logger.info("✓ Agent service initialized")
        logger.info(f"✓ Model: {agent_service.config.claude_model}")
        logger.info(f"✓ Max searches: {agent_service.config.max_web_searches}")
        logger.info(f"✓ Tools: {', '.join(agent_service.config.get_allowed_tools())}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize agent service: {e}")
        logger.error(
            "Please ensure ANTHROPIC_API_KEY is set in your environment or .env file"
        )
        raise

    logger.info("=" * 60)
    logger.info("🚀 API is ready!")
    logger.info("   Docs: http://localhost:8000/docs")
    logger.info("   Health: http://localhost:8000/api/health")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("🦊 Buddy Fox API shutting down...")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
