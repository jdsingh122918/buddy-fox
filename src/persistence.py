"""
Session persistence for saving and loading agent state.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from .agent import AgentSession
from .utils import save_json, load_json

logger = logging.getLogger(__name__)


class SessionPersistence:
    """
    Handles saving and loading agent sessions to/from disk.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize session persistence.

        Args:
            storage_dir: Directory to store session files (None = use default)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".cache" / "buddy-fox" / "sessions"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.storage_dir / f"{session_id}.json"

    def save_session(self, session: AgentSession) -> bool:
        """
        Save session to disk.

        Args:
            session: Session to save

        Returns:
            bool: True if successful
        """
        try:
            session_data = {
                "session_id": session.session_id,
                "started_at": session.started_at.isoformat(),
                "web_searches_used": session.web_searches_used,
                "web_fetches_used": session.web_fetches_used,
                "total_tokens": session.total_tokens,
                "conversation_history": session.conversation_history,
            }

            file_path = self._get_session_path(session.session_id)
            save_json(session_data, file_path)

            logger.info(f"Session {session.session_id} saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def load_session(self, session_id: str) -> Optional[AgentSession]:
        """
        Load session from disk.

        Args:
            session_id: Session ID to load

        Returns:
            AgentSession or None if not found
        """
        try:
            file_path = self._get_session_path(session_id)

            if not file_path.exists():
                logger.warning(f"Session {session_id} not found")
                return None

            session_data = load_json(file_path)

            # Reconstruct session
            session = AgentSession(
                session_id=session_data["session_id"],
                started_at=datetime.fromisoformat(session_data["started_at"]),
            )
            session.web_searches_used = session_data["web_searches_used"]
            session.web_fetches_used = session_data["web_fetches_used"]
            session.total_tokens = session_data["total_tokens"]
            session.conversation_history = session_data["conversation_history"]

            logger.info(f"Session {session_id} loaded from {file_path}")
            return session

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None

    def list_sessions(self) -> list[dict]:
        """
        List all saved sessions.

        Returns:
            list[dict]: List of session metadata
        """
        sessions = []

        for file_path in self.storage_dir.glob("*.json"):
            try:
                session_data = load_json(file_path)
                sessions.append(
                    {
                        "session_id": session_data["session_id"],
                        "started_at": session_data["started_at"],
                        "web_searches": session_data["web_searches_used"],
                        "web_fetches": session_data["web_fetches_used"],
                        "messages": len(session_data["conversation_history"]),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to load session from {file_path}: {e}")

        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x["started_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a saved session.

        Args:
            session_id: Session ID to delete

        Returns:
            bool: True if successful
        """
        try:
            file_path = self._get_session_path(session_id)

            if file_path.exists():
                file_path.unlink()
                logger.info(f"Session {session_id} deleted")
                return True
            else:
                logger.warning(f"Session {session_id} not found")
                return False

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def clear_all_sessions(self) -> int:
        """
        Delete all saved sessions.

        Returns:
            int: Number of sessions deleted
        """
        count = 0
        for file_path in self.storage_dir.glob("*.json"):
            try:
                file_path.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {e}")

        logger.info(f"Cleared {count} sessions")
        return count

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            int: Number of sessions deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        count = 0

        for file_path in self.storage_dir.glob("*.json"):
            try:
                session_data = load_json(file_path)
                started_at = datetime.fromisoformat(session_data["started_at"])

                if started_at < cutoff_date:
                    file_path.unlink()
                    count += 1
                    logger.debug(f"Deleted old session: {session_data['session_id']}")

            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

        logger.info(f"Cleaned up {count} old sessions")
        return count

    def export_session(self, session_id: str, output_path: Path) -> bool:
        """
        Export session to a specified file.

        Args:
            session_id: Session to export
            output_path: Path to export to

        Returns:
            bool: True if successful
        """
        try:
            source_path = self._get_session_path(session_id)

            if not source_path.exists():
                logger.error(f"Session {session_id} not found")
                return False

            session_data = load_json(source_path)

            # Add export metadata
            session_data["exported_at"] = datetime.now().isoformat()

            save_json(session_data, output_path)
            logger.info(f"Session {session_id} exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return False

    def import_session(self, import_path: Path) -> Optional[str]:
        """
        Import session from a file.

        Args:
            import_path: Path to import from

        Returns:
            str or None: Session ID if successful
        """
        try:
            if not import_path.exists():
                logger.error(f"Import file not found: {import_path}")
                return None

            session_data = load_json(import_path)
            session_id = session_data["session_id"]

            # Save to storage directory
            destination_path = self._get_session_path(session_id)
            save_json(session_data, destination_path)

            logger.info(f"Session {session_id} imported from {import_path}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return None


# Global persistence instance
_global_persistence: Optional[SessionPersistence] = None


def get_persistence(storage_dir: Optional[Path] = None) -> SessionPersistence:
    """
    Get or create global persistence instance.

    Args:
        storage_dir: Optional storage directory

    Returns:
        SessionPersistence: Global persistence instance
    """
    global _global_persistence

    if _global_persistence is None:
        _global_persistence = SessionPersistence(storage_dir)

    return _global_persistence
