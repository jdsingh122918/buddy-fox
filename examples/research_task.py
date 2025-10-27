"""
Example: Conduct comprehensive research on a topic.

Usage:
    python examples/research_task.py "Your research topic"
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_agent


async def main():
    """Conduct research on a topic."""
    print("=" * 60)
    print("Buddy Fox - Research Task Example")
    print("=" * 60)
    print()

    # Get topic from command line or use default
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Claude Agent SDK capabilities and use cases"
        print(f"No topic provided. Using default: {topic}")

    print(f"Researching: {topic}")
    print()

    # Get research depth
    depth = "medium"  # Options: "quick", "medium", "deep"
    print(f"Research depth: {depth}")
    print("-" * 60)
    print()

    # Create the agent
    agent = await create_agent()

    try:
        # Conduct research
        async for chunk in agent.research_topic(topic, depth=depth):
            print(chunk, end="", flush=True)

        print()
        print()
        print("-" * 60)

        # Display session info
        stats = agent.get_session_info()
        print(f"\n📊 Session Statistics:")
        print(f"   • Web searches: {stats['web_searches']}")
        print(f"   • Web fetches: {stats['web_fetches']}")
        print(f"   • Total messages: {stats['messages']}")
        print(f"   • Duration: {stats['duration_seconds']:.2f}s")

        # Show remaining searches
        from src.config import get_config

        config = get_config()
        remaining = config.max_web_searches - stats["web_searches"]
        print(f"   • Searches remaining: {remaining}/{config.max_web_searches}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
