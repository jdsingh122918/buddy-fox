# Buddy Fox

An AI agent that can browse the web for you, powered by Claude and the Anthropic Agent SDK.

## Features

- **Web Search**: Search the web with intelligent query refinement
- **Web Fetch**: Retrieve and analyze content from specific URLs
- **Agentic Reasoning**: Claude autonomously decides when to search vs fetch
- **Interactive Mode**: Chat-style interface for web browsing
- **Session Management**: Track usage, history, and statistics
- **Configurable Permissions**: Control which tools the agent can access

## Installation

### Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip
- Anthropic API key (get one at https://console.anthropic.com/)

### Setup

1. Clone or navigate to the project:
   ```bash
   cd buddy-fox
   ```

2. Install dependencies:
   ```bash
   # Using UV (recommended)
   uv pip install -e .

   # Or using pip
   pip install -e .
   ```

3. Configure environment:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your API key
   # ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Interactive Mode

Run the agent in interactive mode for chat-style conversations:

```bash
python main.py
```

Available commands:
- Type any question to search and get answers
- `stats` - View session statistics
- `quit` or `exit` - End the session

### Single Query Mode

Run a single query from the command line:

```bash
python main.py "What are the latest developments in AI?"
```

### Example Scripts

#### Simple Web Search
```bash
python examples/simple_search.py
```

#### URL Analysis
```bash
python examples/url_analyzer.py https://example.com
```

#### Research Task
```bash
python examples/research_task.py "Claude Agent SDK capabilities"
```

## Programmatic Usage

Use Buddy Fox in your own Python code:

```python
import asyncio
from src import create_agent

async def main():
    # Create agent
    agent = await create_agent()

    # Simple query
    async for chunk in agent.query("What's new in AI?"):
        print(chunk, end="", flush=True)

    # Web search
    async for chunk in agent.search_web("Python async patterns", max_results=5):
        print(chunk, end="", flush=True)

    # Fetch and analyze URL
    async for chunk in agent.fetch_and_analyze("https://example.com"):
        print(chunk, end="", flush=True)

    # Research topic
    async for chunk in agent.research_topic("Machine learning trends", depth="deep"):
        print(chunk, end="", flush=True)

    # Get session stats
    stats = agent.get_session_info()
    print(stats)

asyncio.run(main())
```

## Configuration

Configuration is managed via environment variables in `.env`:

### Required
- `ANTHROPIC_API_KEY` - Your Anthropic API key

### Optional
- `CLAUDE_MODEL` - Model to use (default: `claude-sonnet-4-5-20250929`)
- `MAX_WEB_SEARCHES` - Max searches per session (default: `10`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `ALLOWED_DOMAINS` - Comma-separated list of allowed domains
- `BLOCKED_DOMAINS` - Comma-separated list of blocked domains
- `ENABLE_WEB_SEARCH` - Enable web search (default: `true`)
- `ENABLE_WEB_FETCH` - Enable web fetch (default: `true`)
- `ENABLE_BASH` - Enable bash commands (default: `false`)
- `ENABLE_FILE_OPS` - Enable file operations (default: `false`)

### Advanced Configuration

For programmatic configuration:

```python
from src import AgentConfig, WebBrowsingAgent

config = AgentConfig(
    anthropic_api_key="your-key",
    claude_model="claude-sonnet-4-5-20250929",
    max_web_searches=20,
    allowed_domains=["wikipedia.org", "github.com"],
    enable_web_search=True,
    enable_web_fetch=True,
)

agent = WebBrowsingAgent(config=config)
```

## Docker Deployment

Buddy Fox includes a full-stack web UI with Docker support for easy deployment.

### Quick Start with Docker

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Add your Anthropic API key to .env
# ANTHROPIC_API_KEY=your_api_key_here

# 3. Build and start services
docker-compose up --build

# Or use the Makefile
make up
```

Access the application:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Docker Commands

```bash
# Development mode (with hot-reload)
make dev
# or
docker-compose -f docker-compose.dev.yml up

# Production mode
make prod
# or
docker-compose -f docker-compose.prod.yml up -d

# View logs
make logs

# Stop services
make down

# Clean everything
make clean
```

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

## Project Structure

```
buddy-fox/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Pydantic models
│   │   └── services/    # Agent service
│   ├── Dockerfile       # Backend Docker image
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── hooks/       # React hooks
│   │   └── lib/         # Utilities
│   ├── Dockerfile       # Frontend Docker image
│   └── package.json
├── src/                 # Core agent library
│   ├── __init__.py      # Package exports
│   ├── agent.py         # Core agent implementation
│   ├── config.py        # Configuration management
│   └── tools.py         # Tool definitions
├── examples/            # Usage examples
│   ├── simple_search.py # Basic search example
│   ├── url_analyzer.py  # URL analysis example
│   └── research_task.py # Research example
├── main.py              # CLI interface
├── docker-compose.yml   # Docker orchestration
├── Makefile             # Docker shortcuts
├── pyproject.toml       # Project dependencies
├── .env.example         # Environment template
├── DOCKER.md            # Docker documentation
└── README.md            # This file
```

## Architecture

Buddy Fox is built on the Claude Agent SDK and provides:

1. **WebBrowsingAgent**: Main agent class with web browsing capabilities
2. **AgentSession**: Session management with usage tracking
3. **Tool Configurations**: WebSearch and WebFetch tool setup
4. **Streaming Responses**: Real-time response display
5. **Error Handling**: Robust error handling and retries

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
# Format code
black src/ examples/

# Lint
ruff check src/ examples/
```

## Use Cases

- **Research**: Gather information from multiple sources
- **News Aggregation**: Find recent news on topics
- **Content Analysis**: Analyze web pages and documents
- **Fact Checking**: Verify claims across sources
- **Market Research**: Compare products, prices, and features
- **Documentation Lookup**: Find technical documentation

## Limitations

- Web search has usage limits (configurable via `MAX_WEB_SEARCHES`)
- Some websites may block automated access
- Rate limiting may apply based on your API plan
- Search results depend on search engine availability

## Contributing

This is a project built with Claude Code. Feel free to extend it with:
- Additional tools (e.g., PDF parsing, data extraction)
- Custom search strategies
- Result caching
- Multi-source fact checking
- And more!

## License

See LICENSE file for details.

## Support

For issues with:
- **Claude Agent SDK**: See official docs at https://docs.anthropic.com/en/api/agent-sdk/overview
- **Anthropic API**: Contact Anthropic support at https://support.anthropic.com/
- **This project**: Open an issue in the repository

## Acknowledgments

Built with:
- Claude by Anthropic
- Claude Agent SDK
- Claude Code

---

Made with love and AI
