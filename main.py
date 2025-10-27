"""
Buddy Fox - AI Web Browsing Agent
Main CLI interface
"""

import sys
import asyncio
from src import create_agent, get_config


async def interactive_mode():
    """Run the agent in interactive mode."""
    print("=" * 60)
    print("🦊 Buddy Fox - AI Web Browsing Agent")
    print("=" * 60)
    print()
    print("Type your queries and I'll search the web for answers.")
    print("Commands: 'quit' or 'exit' to end, 'stats' for session info")
    print()

    # Create agent
    try:
        agent = await create_agent()
        config = get_config()
        print(f"✓ Agent initialized with model: {config.claude_model}")
        print(f"✓ Tools enabled: {', '.join(config.get_allowed_tools())}")
        print()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your ANTHROPIC_API_KEY to the .env file")
        return 1

    while True:
        try:
            # Get user input
            query = input("\n🔍 Query: ").strip()

            if not query:
                continue

            # Handle commands
            if query.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                stats = agent.get_session_info()
                print(f"\nSession summary:")
                print(f"  • Searches: {stats['web_searches']}")
                print(f"  • Fetches: {stats['web_fetches']}")
                print(f"  • Duration: {stats['duration_seconds']:.1f}s")
                break

            if query.lower() == "stats":
                stats = agent.get_session_info()
                print(f"\n📊 Session Statistics:")
                print(f"   • Session ID: {stats['session_id']}")
                print(f"   • Web searches: {stats['web_searches']}/{config.max_web_searches}")
                print(f"   • Web fetches: {stats['web_fetches']}")
                print(f"   • Messages: {stats['messages']}")
                print(f"   • Duration: {stats['duration_seconds']:.2f}s")
                continue

            # Process query
            print("\n💭 Thinking...\n")
            print("-" * 60)

            async for chunk in agent.query(query):
                print(chunk, end="", flush=True)

            print("\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try another query or type 'quit' to exit.")

    return 0


async def single_query_mode(query: str):
    """Run a single query and exit."""
    try:
        agent = await create_agent()

        print(f"Query: {query}\n")
        print("-" * 60)

        async for chunk in agent.query(query):
            print(chunk, end="", flush=True)

        print("\n" + "-" * 60)

        stats = agent.get_session_info()
        print(f"\nSearches used: {stats['web_searches']}, Fetches: {stats['web_fetches']}")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        exit_code = asyncio.run(single_query_mode(query))
    else:
        # Interactive mode
        exit_code = asyncio.run(interactive_mode())

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
