"""
Buddy Fox - AI Web Browsing Agent
Built with Claude Agent SDK
"""

__version__ = "0.1.0"

# Import main components
from .agent import (
    WebBrowsingAgent,
    AgentSession,
    create_agent,
    quick_query,
)
from .config import (
    AgentConfig,
    get_config,
    reset_config,
)
from .tools import (
    ToolRegistry,
    WebSearchParams,
    WebFetchParams,
    build_tool_configs,
)
from .cache import (
    ResultCache,
    SearchCache,
    FetchCache,
    get_global_cache,
    clear_global_cache,
)
from .persistence import (
    SessionPersistence,
    get_persistence,
)
from .retry import (
    RetryError,
    exponential_backoff_async,
    exponential_backoff_sync,
    retry_async,
    retry_sync,
)
from .logging_config import (
    setup_logging,
    get_logger,
    StructuredLogger,
    create_correlation_id,
)
from . import utils

__all__ = [
    # Version
    "__version__",
    # Agent
    "WebBrowsingAgent",
    "AgentSession",
    "create_agent",
    "quick_query",
    # Config
    "AgentConfig",
    "get_config",
    "reset_config",
    # Tools
    "ToolRegistry",
    "WebSearchParams",
    "WebFetchParams",
    "build_tool_configs",
    # Cache
    "ResultCache",
    "SearchCache",
    "FetchCache",
    "get_global_cache",
    "clear_global_cache",
    # Persistence
    "SessionPersistence",
    "get_persistence",
    # Retry
    "RetryError",
    "exponential_backoff_async",
    "exponential_backoff_sync",
    "retry_async",
    "retry_sync",
    # Logging
    "setup_logging",
    "get_logger",
    "StructuredLogger",
    "create_correlation_id",
    # Utils
    "utils",
]
