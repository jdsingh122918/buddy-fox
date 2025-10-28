"""
Pydantic models for API request/response validation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    query: str = Field(..., min_length=1, max_length=10000, description="User query")
    session_id: Optional[str] = Field(
        None, description="Optional session ID to continue conversation"
    )
    stream: bool = Field(True, description="Enable streaming responses")


class SessionInfo(BaseModel):
    """Session information model."""

    session_id: str
    started_at: datetime
    web_searches_used: int
    web_fetches_used: int
    max_searches: int
    duration_seconds: float
    message_count: int


class ToolUsage(BaseModel):
    """Tool usage information."""

    tool_name: str
    status: str  # "started", "completed", "failed"
    timestamp: datetime


class StreamEvent(BaseModel):
    """Server-Sent Event model."""

    type: str  # "text", "tool", "complete", "error"
    content: Optional[str] = None
    tool: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    session_stats: Optional[SessionInfo] = None


class QueryResponse(BaseModel):
    """Response model for non-streaming queries."""

    response: str
    session_id: str
    session_stats: SessionInfo
    duration_ms: float


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""

    sessions: List[SessionInfo]
    total: int


class StatsResponse(BaseModel):
    """Response model for statistics."""

    total_sessions: int
    total_queries: int
    cache_stats: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    agent_ready: bool


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    session_id: Optional[str] = None


# Transcription Models

class WebcastTranscriptionRequest(BaseModel):
    """Request model for webcast transcription."""

    webcast_url: str = Field(..., min_length=1, description="URL of the webcast to transcribe")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    language: Optional[str] = Field("en", description="Language code for transcription")


class TranscriptionChunk(BaseModel):
    """Single transcription chunk."""

    text: str
    confidence: float
    is_final: bool
    timestamp: float
    audio_start: Optional[float] = None
    audio_end: Optional[float] = None


class TranscriptionEvent(BaseModel):
    """Server-Sent Event for transcription."""

    type: str  # "session_started", "browser_ready", "audio_started", "transcription", "error", "complete"
    message: Optional[str] = None
    session_id: Optional[str] = None
    webcast_url: Optional[str] = None
    transcription: Optional[TranscriptionChunk] = None
    error: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None


class TranscriptionSessionInfo(BaseModel):
    """Information about a transcription session."""

    session_id: str
    webcast_url: str
    started_at: datetime
    status: str  # "starting", "active", "stopped", "error"
    total_duration_seconds: float
    chunks_transcribed: int
    language: str
