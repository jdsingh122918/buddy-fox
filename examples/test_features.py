"""
Test script to verify all Buddy Fox features.

Tests:
- Configuration loading
- Agent initialization
- Caching functionality
- Session persistence
- Retry logic
- Utility functions

Usage:
    python examples/test_features.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import (
    get_config,
    create_agent,
    ResultCache,
    get_global_cache,
    get_persistence,
    utils,
    retry_async,
    RetryError,
)


def test_config():
    """Test configuration loading."""
    print("🧪 Testing configuration...")

    try:
        config = get_config()
        assert config.anthropic_api_key, "API key not loaded"
        assert config.claude_model, "Model not set"
        assert len(config.get_allowed_tools()) > 0, "No tools enabled"

        print(f"  ✓ Config loaded: {config.claude_model}")
        print(f"  ✓ Tools enabled: {', '.join(config.get_allowed_tools())}")
        return True

    except Exception as e:
        print(f"  ❌ Config test failed: {e}")
        return False


async def test_agent_creation():
    """Test agent initialization."""
    print("\n🧪 Testing agent creation...")

    try:
        agent = await create_agent()
        assert agent is not None, "Agent creation failed"
        assert agent.session is not None, "Session not initialized"

        print(f"  ✓ Agent created: {agent.session.session_id}")
        return True, agent

    except Exception as e:
        print(f"  ❌ Agent test failed: {e}")
        return False, None


def test_cache():
    """Test caching functionality."""
    print("\n🧪 Testing cache...")

    try:
        cache = ResultCache(max_size=10, default_ttl=3600)

        # Test set/get
        cache.set("test_key", {"data": "test_value"})
        value = cache.get("test_key")
        assert value == {"data": "test_value"}, "Cache get/set failed"

        # Test stats
        stats = cache.get_stats()
        assert stats["hits"] > 0, "Cache hits not tracked"
        assert stats["size"] > 0, "Cache size not tracked"

        # Test miss
        miss_value = cache.get("nonexistent_key")
        assert miss_value is None, "Cache should return None for missing keys"
        assert stats["misses"] > 0 or cache.get_stats()["misses"] > 0, "Cache misses not tracked"

        print(f"  ✓ Cache set/get works")
        print(f"  ✓ Cache stats: {cache.get_stats()}")
        return True

    except Exception as e:
        print(f"  ❌ Cache test failed: {e}")
        return False


async def test_persistence(agent):
    """Test session persistence."""
    print("\n🧪 Testing session persistence...")

    try:
        persistence = get_persistence()
        session = agent.session

        # Add some data to session
        session.add_message("user", "test message")
        session.record_search()

        # Save session
        success = persistence.save_session(session)
        assert success, "Failed to save session"
        print(f"  ✓ Session saved: {session.session_id}")

        # Load session
        loaded_session = persistence.load_session(session.session_id)
        assert loaded_session is not None, "Failed to load session"
        assert loaded_session.session_id == session.session_id, "Session ID mismatch"
        assert loaded_session.web_searches_used == 1, "Search count not preserved"
        print(f"  ✓ Session loaded: {loaded_session.session_id}")

        # List sessions
        sessions = persistence.list_sessions()
        assert len(sessions) > 0, "No sessions listed"
        print(f"  ✓ Found {len(sessions)} saved sessions")

        # Clean up test session
        persistence.delete_session(session.session_id)
        print(f"  ✓ Test session deleted")

        return True

    except Exception as e:
        print(f"  ❌ Persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_retry_logic():
    """Test retry logic with exponential backoff."""
    print("\n🧪 Testing retry logic...")

    try:
        # Test successful retry after failures
        attempt_count = 0

        @retry_async(max_retries=3, initial_delay=0.1)
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Simulated failure")
            return "success"

        result = await flaky_function()
        assert result == "success", "Retry did not succeed"
        assert attempt_count == 3, f"Expected 3 attempts, got {attempt_count}"
        print(f"  ✓ Retry succeeded after {attempt_count} attempts")

        # Test retry exhaustion
        @retry_async(max_retries=2, initial_delay=0.1)
        async def always_fails():
            raise ValueError("Always fails")

        try:
            await always_fails()
            assert False, "Should have raised RetryError"
        except RetryError as e:
            print(f"  ✓ Retry correctly exhausted: {e}")

        return True

    except Exception as e:
        print(f"  ❌ Retry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test utility functions."""
    print("\n🧪 Testing utility functions...")

    try:
        # Test duration formatting
        assert utils.format_duration(45) == "45.0s"
        assert "m" in utils.format_duration(125)  # Should contain minutes
        print(f"  ✓ Duration formatting works")

        # Test URL extraction
        text = "Check out https://example.com and https://test.org"
        urls = utils.extract_urls(text)
        assert len(urls) == 2, "URL extraction failed"
        print(f"  ✓ URL extraction works: {urls}")

        # Test text truncation
        long_text = "a" * 200
        truncated = utils.truncate_text(long_text, max_length=50)
        assert len(truncated) <= 50, "Text truncation failed"
        print(f"  ✓ Text truncation works")

        # Test domain extraction
        domain = utils.extract_domain("https://www.example.com/path")
        assert domain == "example.com", f"Domain extraction failed: {domain}"
        print(f"  ✓ Domain extraction works")

        # Test progress bar
        bar = utils.create_progress_bar(50, 100, width=20)
        assert "[" in bar and "]" in bar, "Progress bar formatting failed"
        print(f"  ✓ Progress bar: {bar}")

        return True

    except Exception as e:
        print(f"  ❌ Utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 70)
    print("🦊 Buddy Fox - Feature Test Suite")
    print("=" * 70)
    print()

    results = {}

    # Run tests
    results["config"] = test_config()

    agent_success, agent = await test_agent_creation()
    results["agent"] = agent_success

    results["cache"] = test_cache()

    if agent:
        results["persistence"] = await test_persistence(agent)
    else:
        print("\n⚠️  Skipping persistence test (agent creation failed)")
        results["persistence"] = False

    results["retry"] = await test_retry_logic()
    results["utils"] = test_utils()

    # Summary
    print()
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    for test_name, success in results.items():
        status = "✓ PASS" if success else "❌ FAIL"
        color = "green" if success else "red"
        print(f"  {utils.highlight_text(status, color)} - {test_name}")

    print()
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print()
        print(utils.highlight_text("🎉 All tests passed!", "green"))
        return 0
    else:
        print()
        print(utils.highlight_text(f"⚠️  {failed} test(s) failed", "red"))
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
