"""
Query API endpoints with Server-Sent Events streaming.
"""

import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncIterator

from ..models.schemas import QueryRequest, QueryResponse, StreamEvent
from ..services.agent_service import get_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


async def event_generator(query: str, session_id: str = None) -> AsyncIterator[str]:
    """
    Generate Server-Sent Events for streaming responses.

    Args:
        query: User query
        session_id: Optional session ID

    Yields:
        str: SSE formatted events
    """
    agent_service = get_agent_service()

    try:
        async for event in agent_service.stream_query(query, session_id):
            # Format as SSE
            event_data = json.dumps(event)
            yield f"data: {event_data}\n\n"

    except Exception as e:
        logger.error(f"Error in event generator: {e}", exc_info=True)
        error_event = {"type": "error", "error": str(e)}
        yield f"data: {json.dumps(error_event)}\n\n"


@router.post("")
async def query_agent(request: QueryRequest):
    """
    Query the agent with streaming response.

    Args:
        request: Query request with query text and optional session ID

    Returns:
        StreamingResponse: Server-Sent Events stream
    """
    logger.info(f"Received query: {request.query[:100]}...")

    if request.stream:
        # Return SSE stream
        return StreamingResponse(
            event_generator(request.query, request.session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable proxy buffering
            },
        )
    else:
        # Return single response (not implemented for MVP)
        raise HTTPException(
            status_code=400, detail="Non-streaming mode not implemented yet"
        )
