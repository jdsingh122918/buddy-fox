"""
Example: Fetch and analyze a specific URL.

Usage:
    python examples/url_analyzer.py [URL]
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_agent


async def main():
    """Fetch and analyze a URL."""
    print("=" * 60)
    print("Buddy Fox - URL Analyzer Example")
    print("=" * 60)
    print()

    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.anthropic.com/news/agent-capabilities-api"
        print(f"No URL provided. Using default: {url}")

    print(f"Analyzing: {url}")
    print("-" * 60)
    print()

    # Create the agent
    agent = await create_agent()

    try:
        # Fetch and analyze the URL
        analysis_prompt = """
        Analyze this page and provide:
        1. Main topic and purpose
        2. Key points and takeaways
        3. Target audience
        4. Notable details or features
        """

        async for chunk in agent.fetch_and_analyze(url, analysis_prompt):
            print(chunk, end="", flush=True)

        print()
        print()
        print("-" * 60)

        # Display session info
        stats = agent.get_session_info()
        print(f"\n📊 Session Statistics:")
        print(f"   • Web fetches: {stats['web_fetches']}")
        print(f"   • Duration: {stats['duration_seconds']:.2f}s")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
