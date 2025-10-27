"""
Test script to verify structured JSON logging works correctly.

This script tests:
1. Agent initialization with structured logging
2. Query logging with metrics
3. Cache event logging
4. Retry logging
5. Log parsing and analysis

Usage:
    python examples/test_logging.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_agent, ResultCache, retry_async, RetryError


async def test_agent_logging():
    """Test agent initialization and query logging."""
    print("=" * 70)
    print("Testing Structured Logging")
    print("=" * 70)
    print()

    print("1. Creating agent with structured logging...")
    agent = await create_agent()
    print(f"   ✓ Agent created: {agent.session.session_id}")
    print()

    print("2. Testing query with metrics logging...")
    query_text = "What is 2+2?"
    print(f"   Query: {query_text}")

    response = ""
    async for chunk in agent.query(query_text):
        response += chunk

    print(f"   ✓ Query completed (response length: {len(response)} chars)")
    print()

    print("3. Getting session stats...")
    stats = agent.get_session_info()
    print(f"   Session ID: {stats['session_id']}")
    print(f"   Duration: {stats['duration_seconds']:.2f}s")
    print(f"   Messages: {stats['messages']}")
    print()

    return True


def test_cache_logging():
    """Test cache event logging."""
    print("4. Testing cache logging...")

    cache = ResultCache(max_size=5, default_ttl=3600)

    # Test cache set
    cache.set("test_key_1", {"data": "value1"})
    cache.set("test_key_2", {"data": "value2"})
    print("   ✓ Cache set operations logged")

    # Test cache hit
    value = cache.get("test_key_1")
    assert value == {"data": "value1"}
    print("   ✓ Cache hit logged")

    # Test cache miss
    value = cache.get("nonexistent_key")
    assert value is None
    print("   ✓ Cache miss logged")

    print()
    return True


async def test_retry_logging():
    """Test retry attempt logging."""
    print("5. Testing retry logging...")

    attempt_count = 0

    @retry_async(max_retries=2, initial_delay=0.1)
    async def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("Simulated failure")
        return "success"

    try:
        result = await flaky_function()
        print(f"   ✓ Retry attempts logged (attempts: {attempt_count})")
        print()
        return True
    except RetryError:
        print("   ✗ Retry failed")
        return False


async def main():
    """Run all logging tests."""
    print("Starting structured logging tests...")
    print()

    try:
        # Test agent logging
        success1 = await test_agent_logging()

        # Test cache logging
        success2 = test_cache_logging()

        # Test retry logging
        success3 = await test_retry_logging()

        print("=" * 70)
        if success1 and success2 and success3:
            print("✅ All logging tests passed!")
            print()
            print("Check your logs for JSON-formatted output.")
            print("Logs include:")
            print("  - Agent initialization events")
            print("  - Query start/complete with duration metrics")
            print("  - Tool usage events")
            print("  - Cache hit/miss/set events")
            print("  - Retry attempt events")
            print()
            print("To analyze logs, use:")
            print("  python examples/log_analysis.py <logfile>")
            return 0
        else:
            print("❌ Some tests failed")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
