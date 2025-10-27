"""
Tool definitions and configurations for the web browsing agent.
"""

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class WebSearchParams:
    """Parameters for web search operations."""

    query: str
    allowed_domains: Optional[list[str]] = None
    blocked_domains: Optional[list[str]] = None
    max_results: int = 10

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls."""
        params = {"query": self.query}

        if self.allowed_domains:
            params["allowed_domains"] = self.allowed_domains

        if self.blocked_domains:
            params["blocked_domains"] = self.blocked_domains

        return params


@dataclass
class WebFetchParams:
    """Parameters for web fetch operations."""

    url: str
    prompt: str = "Summarize the main content and key points from this page."

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {"url": self.url, "prompt": self.prompt}


class ToolRegistry:
    """Registry of available tools and their configurations."""

    # Tool names used by Claude Agent SDK
    WEB_SEARCH = "WebSearch"
    WEB_FETCH = "WebFetch"
    BASH = "Bash"
    READ = "Read"
    WRITE = "Write"
    EDIT = "Edit"
    GLOB = "Glob"
    GREP = "Grep"

    @classmethod
    def get_web_tools(cls) -> list[str]:
        """Get list of web-related tools."""
        return [cls.WEB_SEARCH, cls.WEB_FETCH]

    @classmethod
    def get_file_tools(cls) -> list[str]:
        """Get list of file operation tools."""
        return [cls.READ, cls.WRITE, cls.EDIT, cls.GLOB, cls.GREP]

    @classmethod
    def get_all_tools(cls) -> list[str]:
        """Get list of all available tools."""
        return cls.get_web_tools() + cls.get_file_tools() + [cls.BASH]


def create_web_search_tool_config(
    allowed_domains: Optional[list[str]] = None,
    blocked_domains: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Create configuration for WebSearch tool.

    Args:
        allowed_domains: List of domains to restrict searches to
        blocked_domains: List of domains to exclude from searches

    Returns:
        dict: Tool configuration
    """
    config = {"name": ToolRegistry.WEB_SEARCH}

    if allowed_domains:
        config["allowed_domains"] = allowed_domains

    if blocked_domains:
        config["blocked_domains"] = blocked_domains

    return config


def create_web_fetch_tool_config() -> dict[str, Any]:
    """
    Create configuration for WebFetch tool.

    Returns:
        dict: Tool configuration
    """
    return {"name": ToolRegistry.WEB_FETCH}


def build_tool_configs(
    enable_web_search: bool = True,
    enable_web_fetch: bool = True,
    enable_bash: bool = False,
    enable_file_ops: bool = False,
    allowed_domains: Optional[list[str]] = None,
    blocked_domains: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """
    Build list of tool configurations based on enabled features.

    Args:
        enable_web_search: Enable web search capability
        enable_web_fetch: Enable web fetch capability
        enable_bash: Enable bash command execution
        enable_file_ops: Enable file operations
        allowed_domains: Domains to restrict searches to
        blocked_domains: Domains to exclude from searches

    Returns:
        list[dict]: List of tool configurations
    """
    tools = []

    if enable_web_search:
        tools.append(
            create_web_search_tool_config(
                allowed_domains=allowed_domains, blocked_domains=blocked_domains
            )
        )

    if enable_web_fetch:
        tools.append(create_web_fetch_tool_config())

    if enable_bash:
        tools.append({"name": ToolRegistry.BASH})

    if enable_file_ops:
        for tool_name in ToolRegistry.get_file_tools():
            tools.append({"name": tool_name})

    return tools
