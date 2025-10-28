"""
Configuration management for Buddy Fox agent.
Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration settings for the web browsing agent."""

    # API Configuration
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-5-20250929"

    # Claude Code Configuration
    claude_code_path: Optional[str] = None

    # Agent Behavior
    max_web_searches: int = 10
    max_context_length: int = 200000

    # Web Search Configuration
    allowed_domains: list[str] | None = None
    blocked_domains: list[str] | None = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    log_file: Optional[str] = None
    log_to_console: bool = True

    # Tool Permissions
    enable_web_search: bool = True
    enable_web_fetch: bool = True
    enable_bash: bool = False  # Disabled by default for security
    enable_file_ops: bool = False  # Disabled by default for security

    # Transcription Configuration
    assemblyai_api_key: Optional[str] = None
    enable_transcription: bool = False
    transcription_chunk_size_ms: int = 1000
    transcription_language: str = "en"
    max_audio_duration_seconds: int = 3600

    # Browser Capture Configuration
    enable_browser_capture: bool = True
    browser_headless: bool = True
    browser_timeout_seconds: int = 30
    browser_max_instances: int = 5

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Create configuration from environment variables.

        Returns:
            AgentConfig: Configuration instance

        Raises:
            ValueError: If required configuration is missing
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )

        # Parse domain lists if provided
        allowed_domains = None
        if allowed_str := os.getenv("ALLOWED_DOMAINS"):
            allowed_domains = [d.strip() for d in allowed_str.split(",") if d.strip()]

        blocked_domains = None
        if blocked_str := os.getenv("BLOCKED_DOMAINS"):
            blocked_domains = [d.strip() for d in blocked_str.split(",") if d.strip()]

        return cls(
            anthropic_api_key=api_key,
            claude_model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
            claude_code_path=os.getenv("CLAUDE_CODE_PATH"),
            max_web_searches=int(os.getenv("MAX_WEB_SEARCHES", "10")),
            allowed_domains=allowed_domains,
            blocked_domains=blocked_domains,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            log_file=os.getenv("LOG_FILE"),
            log_to_console=os.getenv("LOG_TO_CONSOLE", "true").lower() == "true",
            enable_web_search=os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true",
            enable_web_fetch=os.getenv("ENABLE_WEB_FETCH", "true").lower() == "true",
            enable_bash=os.getenv("ENABLE_BASH", "false").lower() == "true",
            enable_file_ops=os.getenv("ENABLE_FILE_OPS", "false").lower() == "true",
            # Transcription settings
            assemblyai_api_key=os.getenv("ASSEMBLYAI_API_KEY"),
            enable_transcription=os.getenv("ENABLE_TRANSCRIPTION", "false").lower() == "true",
            transcription_chunk_size_ms=int(os.getenv("TRANSCRIPTION_CHUNK_SIZE_MS", "1000")),
            transcription_language=os.getenv("TRANSCRIPTION_LANGUAGE", "en"),
            max_audio_duration_seconds=int(os.getenv("MAX_AUDIO_DURATION_SECONDS", "3600")),
            # Browser capture settings
            enable_browser_capture=os.getenv("ENABLE_BROWSER_CAPTURE", "true").lower() == "true",
            browser_headless=os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
            browser_timeout_seconds=int(os.getenv("BROWSER_TIMEOUT_SECONDS", "30")),
            browser_max_instances=int(os.getenv("BROWSER_MAX_INSTANCES", "5")),
        )

    def get_allowed_tools(self) -> list[str]:
        """
        Get list of allowed tools based on configuration.

        Returns:
            list[str]: List of enabled tool names
        """
        tools = []

        if self.enable_web_search:
            tools.append("WebSearch")

        if self.enable_web_fetch:
            tools.append("WebFetch")

        if self.enable_bash:
            tools.append("Bash")

        if self.enable_file_ops:
            tools.extend(["Read", "Write", "Edit", "Glob", "Grep"])

        return tools

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.anthropic_api_key:
            raise ValueError("anthropic_api_key is required")

        if self.max_web_searches < 1:
            raise ValueError("max_web_searches must be at least 1")

        if not self.enable_web_search and not self.enable_web_fetch:
            raise ValueError(
                "At least one web tool (WebSearch or WebFetch) must be enabled"
            )

    def __repr__(self) -> str:
        """Safe string representation that masks sensitive data."""
        masked_key = f"{self.anthropic_api_key[:8]}..." if self.anthropic_api_key else "None"
        return (
            f"AgentConfig("
            f"model={self.claude_model}, "
            f"api_key={masked_key}, "
            f"tools={self.get_allowed_tools()}, "
            f"max_searches={self.max_web_searches})"
        )


# Global configuration instance
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """
    Get or create the global configuration instance.

    Returns:
        AgentConfig: Global configuration instance
    """
    global _config
    if _config is None:
        _config = AgentConfig.from_env()
        _config.validate()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance. Useful for testing."""
    global _config
    _config = None
