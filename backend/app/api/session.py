"""
Session management API endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException

from ..models.schemas import SessionInfo, SessionListResponse
from ..services.agent_service import get_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """
    Get session information.

    Args:
        session_id: Session ID

    Returns:
        SessionInfo: Session information
    """
    agent_service = get_agent_service()

    try:
        session_info = agent_service.get_session_info(session_id)
        return session_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.

    Args:
        session_id: Session ID

    Returns:
        dict: Success message
    """
    agent_service = get_agent_service()

    success = agent_service.delete_session(session_id)

    if success:
        return {"message": f"Session {session_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@router.get("", response_model=SessionListResponse)
async def list_sessions():
    """
    List all active sessions.

    Returns:
        SessionListResponse: List of sessions
    """
    agent_service = get_agent_service()

    sessions = agent_service.list_sessions()

    return {"sessions": sessions, "total": len(sessions)}
