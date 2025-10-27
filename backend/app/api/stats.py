"""
Statistics and health check API endpoints.
"""

import logging
from fastapi import APIRouter

from ..models.schemas import StatsResponse, HealthResponse
from ..services.agent_service import get_agent_service
from .. import __version__

logger = logging.getLogger(__name__)

router = APIRouter(tags=["stats"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse: Health status
    """
    agent_service = get_agent_service()

    try:
        # Check if agent service is ready
        agent_ready = agent_service.config is not None

        return {
            "status": "healthy" if agent_ready else "degraded",
            "version": __version__,
            "agent_ready": agent_ready,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "version": __version__, "agent_ready": False}


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get overall statistics.

    Returns:
        StatsResponse: Statistics
    """
    agent_service = get_agent_service()

    try:
        stats = agent_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return {"total_sessions": 0, "total_queries": 0}
