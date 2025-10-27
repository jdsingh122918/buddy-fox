"""
Agent service for managing Buddy Fox agent instances and sessions.
"""

import sys
from pathlib import Path
from typing import Dict, AsyncIterator
import asyncio
from datetime import datetime
import logging

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src import WebBrowsingAgent, AgentConfig, get_config
from src.agent import AgentSession

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agent instances and sessions."""

    def __init__(self):
        """Initialize the agent service."""
        self.sessions: Dict[str, WebBrowsingAgent] = {}
        self.config: AgentConfig = None
        self._init_config()

    def _init_config(self):
        """Initialize agent configuration."""
        try:
            self.config = get_config()
            logger.info("Agent configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load agent configuration: {e}")
            raise

    async def get_or_create_agent(self, session_id: str = None) -> WebBrowsingAgent:
        """
        Get existing agent or create new one.

        Args:
            session_id: Optional session ID

        Returns:
            WebBrowsingAgent: Agent instance
        """
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        # Create new agent
        try:
            from src import create_agent

            agent = await create_agent(self.config)
            session_id = agent.session.session_id
            self.sessions[session_id] = agent

            logger.info(f"Created new agent with session: {session_id}")
            return agent

        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise

    async def stream_query(
        self, query: str, session_id: str = None
    ) -> AsyncIterator[Dict]:
        """
        Stream query to agent and yield response chunks.

        Args:
            query: User query
            session_id: Optional session ID

        Yields:
            Dict: Stream events
        """
        agent = await self.get_or_create_agent(session_id)
        session_id = agent.session.session_id

        try:
            # Yield session start event
            yield {
                "type": "session",
                "session_id": session_id,
                "status": "started",
            }

            # Track tool usage and accumulate response
            accumulated_response = ""

            async for text_chunk in agent.query(query):
                # The agent.query() now yields clean text content strings
                # Detect tool usage from accumulated text (tools are tracked in agent logs)
                # We rely on agent's internal tool tracking rather than parsing output

                # Yield text chunk
                if text_chunk:
                    yield {
                        "type": "text",
                        "content": text_chunk,
                    }
                    accumulated_response += text_chunk

            # Yield completion event with stats
            stats = agent.get_session_info()
            yield {
                "type": "complete",
                "session_stats": {
                    "session_id": stats["session_id"],
                    "started_at": agent.session.started_at.isoformat(),
                    "web_searches_used": stats["web_searches"],
                    "web_fetches_used": stats["web_fetches"],
                    "max_searches": self.config.max_web_searches,
                    "duration_seconds": stats["duration_seconds"],
                    "message_count": stats["messages"],
                },
            }

        except Exception as e:
            logger.error(f"Error during query stream: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id,
            }

    def get_session_info(self, session_id: str) -> Dict:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            Dict: Session info
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        agent = self.sessions[session_id]
        stats = agent.get_session_info()

        return {
            "session_id": stats["session_id"],
            "started_at": agent.session.started_at.isoformat(),
            "web_searches_used": stats["web_searches"],
            "web_fetches_used": stats["web_fetches"],
            "max_searches": self.config.max_web_searches,
            "duration_seconds": stats["duration_seconds"],
            "message_count": stats["messages"],
        }

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID

        Returns:
            bool: True if deleted
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def list_sessions(self) -> list:
        """
        List all active sessions.

        Returns:
            list: List of session info dicts
        """
        sessions = []
        for session_id, agent in self.sessions.items():
            stats = agent.get_session_info()
            sessions.append(
                {
                    "session_id": stats["session_id"],
                    "started_at": agent.session.started_at.isoformat(),
                    "web_searches_used": stats["web_searches"],
                    "web_fetches_used": stats["web_fetches"],
                    "max_searches": self.config.max_web_searches,
                    "duration_seconds": stats["duration_seconds"],
                    "message_count": stats["messages"],
                }
            )
        return sessions

    def get_stats(self) -> Dict:
        """
        Get overall statistics.

        Returns:
            Dict: Statistics
        """
        total_queries = sum(
            agent.session.web_searches_used + agent.session.web_fetches_used
            for agent in self.sessions.values()
        )

        return {
            "total_sessions": len(self.sessions),
            "total_queries": total_queries,
            "active_sessions": len(self.sessions),
        }


# Global agent service instance
_agent_service: AgentService = None


def get_agent_service() -> AgentService:
    """
    Get or create the global agent service instance.

    Returns:
        AgentService: Global agent service
    """
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
