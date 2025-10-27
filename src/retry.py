"""
Retry logic with exponential backoff for handling transient failures.
"""

import asyncio
from typing import TypeVar, Callable, Optional, Any
from functools import wraps
import random

from .logging_config import get_logger

_logger = get_logger(__name__)

T = TypeVar("T")


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


async def exponential_backoff_async(
    func: Callable[..., Any],
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    **kwargs,
) -> T:
    """
    Execute an async function with exponential backoff retry logic.

    Args:
        func: Async function to execute
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        retryable_exceptions: Tuple of exceptions that should trigger retry
        on_retry: Optional callback function(attempt, exception) called on each retry
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from func

    Raises:
        RetryError: When all retries are exhausted
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)

        except retryable_exceptions as e:
            last_exception = e

            # Don't retry if this was the last attempt
            if attempt >= max_retries:
                break

            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base**attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random())

            # Log retry attempt
            _logger.log_retry_attempt(
                attempt=attempt + 1,
                max_attempts=max_retries + 1,
                delay_ms=delay * 1000,
                error=e,
                function_name=func.__name__,
            )

            # Call retry callback if provided
            if on_retry:
                on_retry(attempt + 1, e)

            # Wait before retrying
            await asyncio.sleep(delay)

        except Exception as e:
            # Non-retryable exception, raise immediately
            _logger.error(
                "Non-retryable exception",
                error=e,
                function_name=func.__name__,
            )
            raise

    # All retries exhausted
    raise RetryError(
        f"Failed after {max_retries + 1} attempts",
        last_exception=last_exception,
    )


def exponential_backoff_sync(
    func: Callable[..., Any],
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    **kwargs,
) -> T:
    """
    Execute a sync function with exponential backoff retry logic.

    Args:
        func: Sync function to execute
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        retryable_exceptions: Tuple of exceptions that should trigger retry
        on_retry: Optional callback function(attempt, exception) called on each retry
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from func

    Raises:
        RetryError: When all retries are exhausted
    """
    import time

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)

        except retryable_exceptions as e:
            last_exception = e

            # Don't retry if this was the last attempt
            if attempt >= max_retries:
                break

            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base**attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random())

            # Log retry attempt
            _logger.log_retry_attempt(
                attempt=attempt + 1,
                max_attempts=max_retries + 1,
                delay_ms=delay * 1000,
                error=e,
                function_name=func.__name__,
            )

            # Call retry callback if provided
            if on_retry:
                on_retry(attempt + 1, e)

            # Wait before retrying
            time.sleep(delay)

        except Exception as e:
            # Non-retryable exception, raise immediately
            _logger.error(
                "Non-retryable exception",
                error=e,
                function_name=func.__name__,
            )
            raise

    # All retries exhausted
    raise RetryError(
        f"Failed after {max_retries + 1} attempts",
        last_exception=last_exception,
    )


def retry_async(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
):
    """
    Decorator for async functions with exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        retryable_exceptions: Tuple of exceptions that should trigger retry

    Example:
        @retry_async(max_retries=3, initial_delay=1.0)
        async def fetch_data():
            # Your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await exponential_backoff_async(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                retryable_exceptions=retryable_exceptions,
                **kwargs,
            )

        return wrapper

    return decorator


def retry_sync(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
):
    """
    Decorator for sync functions with exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        retryable_exceptions: Tuple of exceptions that should trigger retry

    Example:
        @retry_sync(max_retries=3, initial_delay=1.0)
        def fetch_data():
            # Your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return exponential_backoff_sync(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                retryable_exceptions=retryable_exceptions,
                **kwargs,
            )

        return wrapper

    return decorator


# Common exception types for different retry scenarios
NETWORK_EXCEPTIONS = (ConnectionError, TimeoutError, OSError)
API_EXCEPTIONS = (ConnectionError, TimeoutError)


def is_retryable_status_code(status_code: int) -> bool:
    """
    Check if an HTTP status code is retryable.

    Args:
        status_code: HTTP status code

    Returns:
        bool: True if the status code indicates a transient error
    """
    # 429 = Too Many Requests
    # 500-599 = Server errors
    return status_code == 429 or (500 <= status_code < 600)
