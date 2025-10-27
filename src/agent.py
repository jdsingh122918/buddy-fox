"""
Core web browsing agent implementation using Claude Agent SDK.
"""

import time
from typing import AsyncIterator, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock

from .config import AgentConfig, get_config
from .tools import build_tool_configs, ToolRegistry
from .logging_config import get_logger, setup_logging, create_correlation_id


@dataclass
class AgentSession:
    """Session information for tracking agent state."""

    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    web_searches_used: int = 0
    web_fetches_used: int = 0
    total_tokens: int = 0
    conversation_history: list[dict] = field(default_factory=list)

    def record_search(self) -> None:
        """Record a web search usage."""
        self.web_searches_used += 1

    def record_fetch(self) -> None:
        """Record a web fetch usage."""
        self.web_fetches_used += 1

    def can_search(self, max_searches: int) -> bool:
        """Check if more searches are allowed."""
        return self.web_searches_used < max_searches

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

    def get_stats(self) -> dict:
        """Get session statistics."""
        duration = datetime.now() - self.started_at
        return {
            "session_id": self.session_id,
            "duration_seconds": duration.total_seconds(),
            "web_searches": self.web_searches_used,
            "web_fetches": self.web_fetches_used,
            "total_tokens": self.total_tokens,
            "messages": len(self.conversation_history),
        }


class WebBrowsingAgent:
    """
    AI agent capable of browsing the web using Claude Agent SDK.

    This agent can:
    - Search the web for information
    - Fetch and analyze web pages
    - Synthesize information from multiple sources
    - Maintain conversation context
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the web browsing agent.

        Args:
            config: Agent configuration. If None, loads from environment.
        """
        self.config = config or get_config()

        # Set up logging
        setup_logging(
            log_level=self.config.log_level,
            json_format=(self.config.log_format == "json"),
            log_file=Path(self.config.log_file) if self.config.log_file else None,
            include_console=self.config.log_to_console,
        )

        # Create correlation ID for this agent instance
        self.correlation_id = create_correlation_id()

        # Get structured logger
        self.logger = get_logger(__name__, self.correlation_id)

        # Initialize session
        self.session = AgentSession(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Build tool configurations
        self.tool_configs = build_tool_configs(
            enable_web_search=self.config.enable_web_search,
            enable_web_fetch=self.config.enable_web_fetch,
            enable_bash=self.config.enable_bash,
            enable_file_ops=self.config.enable_file_ops,
            allowed_domains=self.config.allowed_domains,
            blocked_domains=self.config.blocked_domains,
        )

        # Log agent initialization
        tools = [t["name"] for t in self.tool_configs]
        self.logger.log_agent_init(
            session_id=self.session.session_id,
            model=self.config.claude_model,
            tools=tools,
            max_web_searches=self.config.max_web_searches,
        )

    def __repr__(self) -> str:
        """String representation of the agent."""
        tools = [t["name"] for t in self.tool_configs]
        return f"WebBrowsingAgent(session={self.session.session_id}, tools={tools})"

    def _extract_text_from_message(self, message) -> str:
        """
        Extract text content from Claude SDK message objects.

        Args:
            message: Message object from Claude SDK

        Returns:
            str: Extracted text content, or empty string if no text content
        """
        # Handle AssistantMessage which contains content blocks
        if isinstance(message, AssistantMessage):
            text_parts = []
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
            return "".join(text_parts)

        # For other message types, return empty string
        return ""

    def _build_system_prompt(self, custom_instructions: Optional[str] = None) -> str:
        """
        Build the system prompt for the agent.

        Args:
            custom_instructions: Optional custom instructions to add

        Returns:
            str: Complete system prompt
        """
        base_prompt = """You are an AI web browsing agent powered by Claude. Your capabilities include:

- Searching the web for current information
- Fetching and analyzing web page content
- Synthesizing information from multiple sources
- Providing well-researched, accurate responses

Guidelines:
1. Use web search when you need current information or to find relevant sources
2. Use web fetch to get detailed content from specific URLs
3. Always cite your sources by including URLs
4. If information conflicts across sources, mention this
5. Be transparent about limitations and uncertainty
6. Provide concise, well-organized responses

When searching or fetching web content:
- Be strategic about your queries
- Refine searches based on initial results
- Cross-reference information when possible
- Summarize key findings clearly
"""

        if custom_instructions:
            base_prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"

        # Add domain restrictions if configured
        if self.config.allowed_domains:
            base_prompt += f"\n\nRestricted to domains: {', '.join(self.config.allowed_domains)}"

        if self.config.blocked_domains:
            base_prompt += f"\n\nBlocked domains: {', '.join(self.config.blocked_domains)}"

        base_prompt += f"\n\nYou have {self.config.max_web_searches} web searches available for this session."

        return base_prompt

    async def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = True,
    ) -> AsyncIterator[str]:
        """
        Query the agent with a prompt.

        Args:
            prompt: User's query or task
            system_prompt: Optional custom system prompt
            stream: Whether to stream responses (default: True)

        Yields:
            str: Response chunks from the agent

        Raises:
            ValueError: If search limit exceeded or invalid parameters
            Exception: For API or network errors
        """
        # Validate search limit
        if not self.session.can_search(self.config.max_web_searches):
            raise ValueError(
                f"Maximum web searches ({self.config.max_web_searches}) exceeded for this session"
            )

        # Record the query
        self.session.add_message("user", prompt)

        # Log query start
        self.logger.log_query_start(
            query=prompt,
            session_id=self.session.session_id,
        )

        start_time = time.time()

        # Build options for Claude Agent SDK
        # Note: API key is picked up from ANTHROPIC_API_KEY environment variable
        options = ClaudeAgentOptions(
            model=self.config.claude_model,
            system_prompt=system_prompt or self._build_system_prompt(),
            allowed_tools=self.config.get_allowed_tools(),
        )

        try:
            # Use Claude Agent SDK's query function
            response_text = ""
            tool_uses = {"WebSearch": 0, "WebFetch": 0}

            async for message in query(prompt=prompt, options=options):
                # Extract text content from the message
                text_content = self._extract_text_from_message(message)

                # Track tool usage by checking the raw message for tool blocks
                message_str = str(message)
                if "WebSearch" in message_str and "WebSearch" not in response_text:
                    self.session.record_search()
                    tool_uses["WebSearch"] += 1
                    self.logger.log_tool_use(
                        tool_name="WebSearch",
                        tool_input={},
                        session_id=self.session.session_id,
                    )

                if "WebFetch" in message_str and "WebFetch" not in response_text:
                    self.session.record_fetch()
                    tool_uses["WebFetch"] += 1
                    self.logger.log_tool_use(
                        tool_name="WebFetch",
                        tool_input={},
                        session_id=self.session.session_id,
                    )

                # Only yield and accumulate if there's actual text content
                if text_content:
                    response_text += text_content
                    yield text_content

            # Record the complete response
            self.session.add_message("assistant", response_text)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log query completion
            self.logger.log_query_complete(
                duration_ms=duration_ms,
                session_id=self.session.session_id,
                web_searches_used=tool_uses["WebSearch"],
                web_fetches_used=tool_uses["WebFetch"],
                response_length=len(response_text),
            )

            # Log metrics
            self.logger.log_metric(
                metric_name="query_duration_ms",
                metric_value=duration_ms,
                metric_unit="milliseconds",
                session_id=self.session.session_id,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Query failed",
                error=e,
                session_id=self.session.session_id,
                duration_ms=duration_ms,
            )
            raise

    async def search_web(
        self, query: str, max_results: int = 5
    ) -> AsyncIterator[str]:
        """
        Perform a web search with a specific query.

        Args:
            query: Search query
            max_results: Maximum number of results to consider

        Yields:
            str: Search results and analysis
        """
        prompt = f"""Search the web for: "{query}"

Provide a summary of the top {max_results} most relevant results. Include:
1. Key findings
2. Source URLs
3. Any notable patterns or themes across results
"""
        async for chunk in self.query(prompt):
            yield chunk

    async def fetch_and_analyze(
        self, url: str, analysis_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Fetch a URL and analyze its content.

        Args:
            url: URL to fetch
            analysis_prompt: Optional specific analysis instructions

        Yields:
            str: Analysis of the fetched content
        """
        if analysis_prompt:
            prompt = f"Fetch and analyze this URL: {url}\n\n{analysis_prompt}"
        else:
            prompt = f"Fetch and analyze this URL: {url}\n\nProvide a comprehensive summary including main topics, key points, and notable details."

        async for chunk in self.query(prompt):
            yield chunk

    async def research_topic(
        self, topic: str, depth: str = "medium"
    ) -> AsyncIterator[str]:
        """
        Conduct comprehensive research on a topic.

        Args:
            topic: Topic to research
            depth: Research depth - "quick", "medium", or "deep"

        Yields:
            str: Research findings
        """
        depth_instructions = {
            "quick": "Provide a quick overview from 1-2 sources.",
            "medium": "Research from multiple sources and provide a balanced summary.",
            "deep": "Conduct thorough research across multiple sources, cross-reference information, and provide detailed analysis.",
        }

        instruction = depth_instructions.get(depth, depth_instructions["medium"])

        prompt = f"""Research the following topic: "{topic}"

{instruction}

Include:
1. Overview of the topic
2. Key facts and details
3. Different perspectives or viewpoints (if applicable)
4. Recent developments or current state
5. Citations with URLs
"""

        async for chunk in self.query(prompt):
            yield chunk

    def get_session_info(self) -> dict:
        """Get current session information."""
        return self.session.get_stats()

    def reset_session(self) -> None:
        """Reset the session, clearing history and counters."""
        old_session_id = self.session.session_id
        self.session = AgentSession(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Log session reset
        self.logger.log_session_event(
            event="reset",
            session_id=self.session.session_id,
            previous_session_id=old_session_id,
        )


async def create_agent(config: Optional[AgentConfig] = None) -> WebBrowsingAgent:
    """
    Factory function to create a web browsing agent.

    Args:
        config: Optional configuration. If None, loads from environment.

    Returns:
        WebBrowsingAgent: Initialized agent instance
    """
    return WebBrowsingAgent(config=config)


async def quick_query(prompt: str, **kwargs) -> str:
    """
    Convenience function for one-off queries.

    Args:
        prompt: Query prompt
        **kwargs: Additional arguments passed to agent.query()

    Returns:
        str: Complete response
    """
    agent = await create_agent()
    response = ""
    async for chunk in agent.query(prompt, **kwargs):
        response += chunk
    return response
