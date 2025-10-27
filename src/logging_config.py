"""
Structured JSON logging for observability.

Provides JSON-formatted logs with consistent structure for metrics,
tracing, and monitoring.
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Optional
from pathlib import Path
import uuid


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON.

    Each log entry includes:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - logger: Logger name
    - message: Log message
    - Extra fields passed via logging.LoggerAdapter
    """

    def __init__(self, include_traceback: bool = True):
        """
        Initialize JSON formatter.

        Args:
            include_traceback: Whether to include stack traces in errors
        """
        super().__init__()
        self.include_traceback = include_traceback

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                # Handle special types
                if isinstance(value, (datetime,)):
                    log_data[key] = value.isoformat()
                elif isinstance(value, (Path,)):
                    log_data[key] = str(value)
                elif isinstance(value, (set,)):
                    log_data[key] = list(value)
                else:
                    try:
                        json.dumps(value)  # Test if serializable
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)

        # Add exception info if present
        if record.exc_info and self.include_traceback:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        return json.dumps(log_data)


class StructuredLogger:
    """
    Wrapper for Python logger that adds structured logging capabilities.

    Provides methods for logging common observability events with
    consistent structure.
    """

    def __init__(self, logger: logging.Logger, correlation_id: Optional[str] = None):
        """
        Initialize structured logger.

        Args:
            logger: Python logger instance
            correlation_id: Optional correlation ID for request tracing
        """
        self.logger = logger
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal log method that adds common fields."""
        extra = {
            "correlation_id": self.correlation_id,
            **kwargs,
        }
        self.logger.log(level, message, extra=extra)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log error message."""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
        self._log(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    # Observability-specific methods

    def log_agent_init(
        self,
        session_id: str,
        model: str,
        tools: list[str],
        **kwargs,
    ) -> None:
        """Log agent initialization."""
        self.info(
            "Agent initialized",
            event_type="agent.initialized",
            session_id=session_id,
            model=model,
            tools=tools,
            **kwargs,
        )

    def log_query_start(self, query: str, **kwargs) -> None:
        """Log query start."""
        self.info(
            "Query started",
            event_type="query.started",
            query=query[:200],  # Truncate long queries
            query_length=len(query),
            **kwargs,
        )

    def log_query_complete(
        self,
        duration_ms: float,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
        **kwargs,
    ) -> None:
        """Log query completion."""
        self.info(
            "Query completed",
            event_type="query.completed",
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            **kwargs,
        )

    def log_tool_use(
        self,
        tool_name: str,
        tool_input: dict,
        duration_ms: Optional[float] = None,
        success: bool = True,
        **kwargs,
    ) -> None:
        """Log tool usage."""
        self.info(
            f"Tool used: {tool_name}",
            event_type="tool.used",
            tool_name=tool_name,
            tool_input=tool_input,
            duration_ms=duration_ms,
            success=success,
            **kwargs,
        )

    def log_cache_event(
        self,
        event: str,  # "hit", "miss", "set", "evict"
        key: str,
        **kwargs,
    ) -> None:
        """Log cache event."""
        self.debug(
            f"Cache {event}",
            event_type=f"cache.{event}",
            cache_key=key,
            **kwargs,
        )

    def log_retry_attempt(
        self,
        attempt: int,
        max_attempts: int,
        delay_ms: float,
        error: Exception,
        **kwargs,
    ) -> None:
        """Log retry attempt."""
        self.warning(
            f"Retry attempt {attempt}/{max_attempts}",
            event_type="retry.attempt",
            attempt=attempt,
            max_attempts=max_attempts,
            delay_ms=delay_ms,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs,
        )

    def log_session_event(
        self,
        event: str,  # "created", "saved", "loaded", "ended"
        session_id: str,
        **kwargs,
    ) -> None:
        """Log session event."""
        self.info(
            f"Session {event}",
            event_type=f"session.{event}",
            session_id=session_id,
            **kwargs,
        )

    def log_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        **kwargs,
    ) -> None:
        """Log custom metric."""
        self.info(
            f"Metric: {metric_name}",
            event_type="metric",
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            **kwargs,
        )


def setup_logging(
    log_level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[Path] = None,
    include_console: bool = True,
) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON formatting for logs
        log_file: Optional file path for log output
        include_console: Whether to include console output
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str, correlation_id: Optional[str] = None) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)
        correlation_id: Optional correlation ID for request tracing

    Returns:
        StructuredLogger: Configured structured logger
    """
    logger = logging.getLogger(name)
    return StructuredLogger(logger, correlation_id)


def create_correlation_id() -> str:
    """
    Create a new correlation ID for request tracing.

    Returns:
        str: UUID correlation ID
    """
    return str(uuid.uuid4())


# Log parsing utilities for observability

def parse_json_log(log_line: str) -> Optional[dict]:
    """
    Parse a JSON log line.

    Args:
        log_line: JSON log line

    Returns:
        dict or None: Parsed log data
    """
    try:
        return json.loads(log_line)
    except json.JSONDecodeError:
        return None


def filter_logs_by_event(logs: list[dict], event_type: str) -> list[dict]:
    """
    Filter logs by event type.

    Args:
        logs: List of parsed log entries
        event_type: Event type to filter (e.g., "query.completed")

    Returns:
        list[dict]: Filtered logs
    """
    return [log for log in logs if log.get("event_type") == event_type]


def extract_metrics(logs: list[dict]) -> dict[str, list[float]]:
    """
    Extract metrics from logs.

    Args:
        logs: List of parsed log entries

    Returns:
        dict: Dictionary of metric names to values
    """
    metrics: dict[str, list[float]] = {}

    for log in logs:
        if log.get("event_type") == "metric":
            metric_name = log.get("metric_name")
            metric_value = log.get("metric_value")
            if metric_name and metric_value is not None:
                if metric_name not in metrics:
                    metrics[metric_name] = []
                metrics[metric_name].append(metric_value)

        # Extract common metrics from events
        if "duration_ms" in log:
            if "duration_ms" not in metrics:
                metrics["duration_ms"] = []
            metrics["duration_ms"].append(log["duration_ms"])

        if "tokens_used" in log:
            if "tokens_used" not in metrics:
                metrics["tokens_used"] = []
            metrics["tokens_used"].append(log["tokens_used"])

        if "cost_usd" in log:
            if "cost_usd" not in metrics:
                metrics["cost_usd"] = []
            metrics["cost_usd"].append(log["cost_usd"])

    return metrics


def calculate_stats(values: list[float]) -> dict:
    """
    Calculate basic statistics for a list of values.

    Args:
        values: List of numeric values

    Returns:
        dict: Statistics (count, min, max, avg, sum)
    """
    if not values:
        return {"count": 0, "min": 0, "max": 0, "avg": 0, "sum": 0}

    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
        "sum": sum(values),
    }
