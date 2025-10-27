"""
Enhanced interactive chat example with caching, persistence, and rich output.

Features:
- Session persistence (save/load/resume)
- Result caching
- Enhanced statistics
- Better error handling
- Progress indicators

Usage:
    python examples/interactive_chat.py [--session SESSION_ID]
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import (
    create_agent,
    get_config,
    get_global_cache,
    get_persistence,
    utils,
)


def print_header():
    """Print welcome header."""
    print("=" * 70)
    print("🦊 Buddy Fox - Enhanced Interactive Chat")
    print("=" * 70)
    print()
    print("Features: Session persistence, caching, enhanced stats")
    print()
    print("Commands:")
    print("  • Type your query to search the web")
    print("  • 'stats' - View session statistics")
    print("  • 'cache' - View cache statistics")
    print("  • 'save' - Save current session")
    print("  • 'sessions' - List saved sessions")
    print("  • 'clear-cache' - Clear result cache")
    print("  • 'help' - Show this help")
    print("  • 'quit' or 'exit' - End session")
    print()


def print_session_info(agent, config):
    """Print session initialization info."""
    print(f"✓ Agent initialized")
    print(f"  • Model: {utils.highlight_text(config.claude_model, 'cyan')}")
    print(f"  • Session: {utils.highlight_text(agent.session.session_id, 'cyan')}")
    print(f"  • Tools: {', '.join(config.get_allowed_tools())}")
    print()


def print_stats(agent, config, cache=None):
    """Print detailed statistics."""
    stats = agent.get_session_info()

    print()
    print(utils.highlight_text("📊 Session Statistics", "bold"))
    print("-" * 70)
    print(f"  Session ID:       {stats['session_id']}")
    print(f"  Duration:         {utils.format_duration(stats['duration_seconds'])}")
    print(f"  Web Searches:     {stats['web_searches']}/{config.max_web_searches}")
    print(f"  Web Fetches:      {stats['web_fetches']}")
    print(f"  Total Messages:   {stats['messages']}")

    # Search usage bar
    search_percent = (stats["web_searches"] / config.max_web_searches) * 100
    search_bar = utils.create_progress_bar(
        stats["web_searches"], config.max_web_searches
    )
    print(f"  Search Usage:     {search_bar} ({search_percent:.0f}%)")

    if cache:
        cache_stats = cache.get_stats()
        print()
        print(utils.highlight_text("💾 Cache Statistics", "bold"))
        print("-" * 70)
        print(f"  Cache Size:       {cache_stats['size']}/{cache_stats['max_size']}")
        print(f"  Hits:             {cache_stats['hits']}")
        print(f"  Misses:           {cache_stats['misses']}")
        print(f"  Hit Rate:         {cache_stats['hit_rate']:.1%}")

    print()


def print_session_list(persistence):
    """Print list of saved sessions."""
    sessions = persistence.list_sessions()

    if not sessions:
        print("\n📁 No saved sessions found.\n")
        return

    print()
    print(utils.highlight_text("📁 Saved Sessions", "bold"))
    print("-" * 70)

    for session in sessions[:10]:  # Show most recent 10
        session_id = session["session_id"]
        started = session["started_at"]
        searches = session["web_searches"]
        messages = session["messages"]
        print(f"  • {session_id}")
        print(f"    Started: {started} | Searches: {searches} | Messages: {messages}")

    if len(sessions) > 10:
        print(f"\n  ... and {len(sessions) - 10} more")

    print()


async def main():
    """Run enhanced interactive chat."""
    parser = argparse.ArgumentParser(description="Enhanced interactive chat")
    parser.add_argument(
        "--session", "-s", help="Resume from saved session ID", default=None
    )
    parser.add_argument(
        "--enable-cache", action="store_true", help="Enable result caching"
    )
    args = parser.parse_args()

    print_header()

    # Initialize components
    try:
        config = get_config()
        agent = await create_agent()

        # Set up persistence
        persistence = get_persistence()

        # Resume session if requested
        if args.session:
            loaded_session = persistence.load_session(args.session)
            if loaded_session:
                agent.session = loaded_session
                print(f"✓ Resumed session: {args.session}\n")
            else:
                print(f"⚠️  Could not load session: {args.session}\n")

        # Set up caching if enabled
        cache = get_global_cache() if args.enable_cache else None

        print_session_info(agent, config)

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your ANTHROPIC_API_KEY to the .env file")
        return 1

    # Interactive loop
    while True:
        try:
            # Get user input
            prompt_text = utils.highlight_text("🔍 Query: ", "blue")
            query = input(prompt_text).strip()

            if not query:
                continue

            # Handle commands
            command = query.lower()

            if command in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                stats = agent.get_session_info()
                print(f"\nSession summary:")
                print(f"  • Duration: {utils.format_duration(stats['duration_seconds'])}")
                print(f"  • Searches: {stats['web_searches']}")
                print(f"  • Fetches: {stats['web_fetches']}")
                print(f"  • Messages: {stats['messages']}")
                break

            elif command == "help":
                print_header()
                continue

            elif command == "stats":
                print_stats(agent, config, cache)
                continue

            elif command == "cache":
                if cache:
                    cache_stats = cache.get_stats()
                    print()
                    print(utils.highlight_text("💾 Cache Statistics", "bold"))
                    print("-" * 70)
                    print(f"  Size:             {cache_stats['size']}/{cache_stats['max_size']}")
                    print(f"  Hits:             {cache_stats['hits']}")
                    print(f"  Misses:           {cache_stats['misses']}")
                    print(f"  Hit Rate:         {cache_stats['hit_rate']:.1%}")
                    print(f"  Total Requests:   {cache_stats['total_requests']}")
                    print()
                else:
                    print("\n💾 Caching is not enabled. Use --enable-cache to enable.\n")
                continue

            elif command == "save":
                success = persistence.save_session(agent.session)
                if success:
                    print(f"\n✓ Session saved: {agent.session.session_id}\n")
                else:
                    print("\n❌ Failed to save session\n")
                continue

            elif command == "sessions":
                print_session_list(persistence)
                continue

            elif command == "clear-cache":
                if cache:
                    cache.clear()
                    print("\n✓ Cache cleared\n")
                else:
                    print("\n💾 Caching is not enabled\n")
                continue

            # Process query
            print()
            print(utils.highlight_text("💭 Thinking...", "yellow"))
            print()
            print("-" * 70)

            start_time = asyncio.get_event_loop().time()

            async for chunk in agent.query(query):
                print(chunk, end="", flush=True)

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            print()
            print("-" * 70)
            print(
                f"⏱️  {utils.highlight_text(f'Completed in {utils.format_duration(duration)}', 'green')}"
            )
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try another query or type 'quit' to exit.\n")
            import traceback

            traceback.print_exc()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
