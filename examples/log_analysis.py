"""
Log analysis example for consuming JSON logs from Buddy Fox.

This script demonstrates how to:
1. Parse JSON log files
2. Extract metrics and statistics
3. Analyze performance
4. Track errors and retry patterns
5. Generate observability reports

Usage:
    # Analyze a log file
    python examples/log_analysis.py /path/to/logfile.json

    # Analyze logs from stdin
    cat logfile.json | python examples/log_analysis.py --stdin
"""

import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logging_config import parse_json_log, filter_logs_by_event, extract_metrics, calculate_stats


def load_logs(file_path: Path = None, from_stdin: bool = False) -> List[Dict[str, Any]]:
    """Load and parse JSON logs from file or stdin."""
    logs = []

    if from_stdin:
        for line in sys.stdin:
            log = parse_json_log(line.strip())
            if log:
                logs.append(log)
    elif file_path:
        with open(file_path, "r") as f:
            for line in f:
                log = parse_json_log(line.strip())
                if log:
                    logs.append(log)
    else:
        raise ValueError("Must specify either file_path or from_stdin")

    return logs


def analyze_queries(logs: List[Dict]) -> Dict[str, Any]:
    """Analyze query performance."""
    query_logs = filter_logs_by_event(logs, "query.completed")

    if not query_logs:
        return {"error": "No completed queries found"}

    durations = [log.get("duration_ms", 0) for log in query_logs]
    durations_stats = calculate_stats(durations)

    # Count tool usage
    total_searches = sum(log.get("web_searches_used", 0) for log in query_logs)
    total_fetches = sum(log.get("web_fetches_used", 0) for log in query_logs)

    return {
        "total_queries": len(query_logs),
        "duration_ms": durations_stats,
        "total_searches": total_searches,
        "total_fetches": total_fetches,
        "avg_searches_per_query": total_searches / len(query_logs) if query_logs else 0,
        "avg_fetches_per_query": total_fetches / len(query_logs) if query_logs else 0,
    }


def analyze_cache(logs: List[Dict]) -> Dict[str, Any]:
    """Analyze cache performance."""
    cache_logs = [log for log in logs if log.get("event_type", "").startswith("cache.")]

    if not cache_logs:
        return {"error": "No cache events found"}

    hits = len([log for log in cache_logs if log.get("event_type") == "cache.hit"])
    misses = len([log for log in cache_logs if log.get("event_type") == "cache.miss"])
    sets = len([log for log in cache_logs if log.get("event_type") == "cache.set"])

    total_requests = hits + misses
    hit_rate = hits / total_requests if total_requests > 0 else 0

    # Analyze miss reasons
    miss_reasons = Counter(
        log.get("reason")
        for log in cache_logs
        if log.get("event_type") == "cache.miss" and log.get("reason")
    )

    return {
        "total_hits": hits,
        "total_misses": misses,
        "total_sets": sets,
        "hit_rate": hit_rate,
        "miss_reasons": dict(miss_reasons),
    }


def analyze_retries(logs: List[Dict]) -> Dict[str, Any]:
    """Analyze retry patterns."""
    retry_logs = filter_logs_by_event(logs, "retry.attempt")

    if not retry_logs:
        return {"error": "No retry attempts found"}

    # Group retries by function
    retries_by_function = defaultdict(list)
    for log in retry_logs:
        func_name = log.get("function_name", "unknown")
        retries_by_function[func_name].append(log)

    # Analyze retry attempts
    total_retries = len(retry_logs)
    unique_functions = len(retries_by_function)

    # Count errors
    error_types = Counter(log.get("error_type") for log in retry_logs if log.get("error_type"))

    return {
        "total_retry_attempts": total_retries,
        "unique_functions_with_retries": unique_functions,
        "error_types": dict(error_types),
        "retries_by_function": {
            func: len(attempts) for func, attempts in retries_by_function.items()
        },
    }


def analyze_errors(logs: List[Dict]) -> Dict[str, Any]:
    """Analyze errors."""
    error_logs = [log for log in logs if log.get("level") == "ERROR"]

    if not error_logs:
        return {"message": "No errors found"}

    # Count error types
    error_types = Counter(log.get("error_type") for log in error_logs if log.get("error_type"))

    # Get error messages
    error_messages = [
        {
            "timestamp": log.get("timestamp"),
            "message": log.get("message"),
            "error_type": log.get("error_type"),
            "error_message": log.get("error_message"),
        }
        for log in error_logs[:10]  # Show first 10
    ]

    return {
        "total_errors": len(error_logs),
        "error_types": dict(error_types),
        "recent_errors": error_messages,
    }


def analyze_sessions(logs: List[Dict]) -> Dict[str, Any]:
    """Analyze sessions."""
    session_logs = [log for log in logs if log.get("event_type", "").startswith("session.")]

    session_ids = set(log.get("session_id") for log in logs if log.get("session_id"))

    # Count session events
    session_events = Counter(log.get("event_type") for log in session_logs)

    return {
        "unique_sessions": len(session_ids),
        "session_events": dict(session_events),
        "sessions": list(session_ids),
    }


def generate_report(logs: List[Dict]) -> str:
    """Generate a comprehensive observability report."""
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("BUDDY FOX - OBSERVABILITY REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Overall stats
    report_lines.append(f"Total log entries: {len(logs)}")
    report_lines.append(f"Log levels: {dict(Counter(log.get('level') for log in logs))}")
    report_lines.append("")

    # Query analysis
    report_lines.append("QUERY PERFORMANCE")
    report_lines.append("-" * 80)
    query_analysis = analyze_queries(logs)
    for key, value in query_analysis.items():
        report_lines.append(f"  {key}: {value}")
    report_lines.append("")

    # Cache analysis
    report_lines.append("CACHE PERFORMANCE")
    report_lines.append("-" * 80)
    cache_analysis = analyze_cache(logs)
    for key, value in cache_analysis.items():
        if key != "miss_reasons":
            report_lines.append(f"  {key}: {value}")
    if "miss_reasons" in cache_analysis:
        report_lines.append("  miss_reasons:")
        for reason, count in cache_analysis["miss_reasons"].items():
            report_lines.append(f"    - {reason}: {count}")
    report_lines.append("")

    # Retry analysis
    report_lines.append("RETRY PATTERNS")
    report_lines.append("-" * 80)
    retry_analysis = analyze_retries(logs)
    for key, value in retry_analysis.items():
        if key not in ["error_types", "retries_by_function"]:
            report_lines.append(f"  {key}: {value}")
    if "error_types" in retry_analysis:
        report_lines.append("  error_types:")
        for error_type, count in retry_analysis["error_types"].items():
            report_lines.append(f"    - {error_type}: {count}")
    report_lines.append("")

    # Error analysis
    report_lines.append("ERROR ANALYSIS")
    report_lines.append("-" * 80)
    error_analysis = analyze_errors(logs)
    for key, value in error_analysis.items():
        if key not in ["error_types", "recent_errors"]:
            report_lines.append(f"  {key}: {value}")
    if "error_types" in error_analysis:
        report_lines.append("  error_types:")
        for error_type, count in error_analysis["error_types"].items():
            report_lines.append(f"    - {error_type}: {count}")
    report_lines.append("")

    # Session analysis
    report_lines.append("SESSION ANALYSIS")
    report_lines.append("-" * 80)
    session_analysis = analyze_sessions(logs)
    for key, value in session_analysis.items():
        if key != "sessions":
            report_lines.append(f"  {key}: {value}")
    report_lines.append("")

    # Metrics extraction
    report_lines.append("EXTRACTED METRICS")
    report_lines.append("-" * 80)
    metrics = extract_metrics(logs)
    for metric_name, values in metrics.items():
        stats = calculate_stats(values)
        report_lines.append(f"  {metric_name}:")
        report_lines.append(f"    count: {stats['count']}")
        report_lines.append(f"    min: {stats['min']:.2f}")
        report_lines.append(f"    max: {stats['max']:.2f}")
        report_lines.append(f"    avg: {stats['avg']:.2f}")
        report_lines.append(f"    sum: {stats['sum']:.2f}")
    report_lines.append("")

    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze JSON logs from Buddy Fox for observability"
    )
    parser.add_argument(
        "logfile",
        nargs="?",
        type=Path,
        help="Path to JSON log file",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read logs from stdin",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Load logs
    try:
        if args.stdin:
            logs = load_logs(from_stdin=True)
        elif args.logfile:
            logs = load_logs(file_path=args.logfile)
        else:
            parser.print_help()
            return 1

        if not logs:
            print("No logs found or failed to parse logs", file=sys.stderr)
            return 1

        # Generate and display report
        if args.format == "json":
            report_data = {
                "total_logs": len(logs),
                "query_analysis": analyze_queries(logs),
                "cache_analysis": analyze_cache(logs),
                "retry_analysis": analyze_retries(logs),
                "error_analysis": analyze_errors(logs),
                "session_analysis": analyze_sessions(logs),
            }
            print(json.dumps(report_data, indent=2))
        else:
            print(generate_report(logs))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
