"""
Simple example: Perform a web search and display results.

Usage:
    python examples/simple_search.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_agent


async def main():
    """Run a simple web search example."""
    print("=" * 60)
    print("Buddy Fox - Simple Web Search Example")
    print("=" * 60)
    print()

    # Create the agent
    print("Initializing agent...")
    agent = await create_agent()
    print(f"✓ Agent ready: {agent}")
    print()

    # Perform a search
    query = "What are the latest developments in AI agents in 2025?"
    print(f"Query: {query}")
    print("-" * 60)
    print()

    try:
        # Stream the response
        async for chunk in agent.search_web(query, max_results=3):
            print(chunk, end="", flush=True)

        print()
        print()
        print("-" * 60)

        # Display session info
        stats = agent.get_session_info()
        print(f"\n📊 Session Statistics:")
        print(f"   • Web searches: {stats['web_searches']}")
        print(f"   • Web fetches: {stats['web_fetches']}")
        print(f"   • Duration: {stats['duration_seconds']:.2f}s")
        print(f"   • Messages: {stats['messages']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
