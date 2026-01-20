"""Retry logic and decorators for ESPN API client."""

import asyncio
from typing import Any, Callable, TypeVar

import structlog
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from espnapi.config import ESPNConfig
from espnapi.exceptions import ESPNClientError, ESPNRateLimitError

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def create_retry_config(config: ESPNConfig) -> dict[str, Any]:
    """Create tenacity retry configuration from ESPN config.

    Args:
        config: ESPN configuration

    Returns:
        Dict with tenacity retry parameters
    """
    return {
        "retry": retry_if_exception_type((ESPNClientError, ESPNRateLimitError)),
        "stop": stop_after_attempt(config.max_retries),
        "wait": wait_exponential(
            multiplier=config.retry_backoff,
            min=config.retry_backoff,
            max=10.0,
        ),
        "reraise": True,
    }


def retry_request(config: ESPNConfig) -> Callable[[F], F]:
    """Decorator for retrying synchronous HTTP requests.

    Args:
        config: ESPN configuration

    Returns:
        Decorated function
    """
    retry_config = create_retry_config(config)

    def decorator(func: F) -> F:
        retrying = Retrying(**retry_config)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return retrying(func, *args, **kwargs)
            except RetryError as e:
                logger.error(
                    "request_failed_after_retries",
                    func_name=func.__name__,
                    retries=config.max_retries,
                    error=str(e),
                )
                # Re-raise the original exception
                raise e.last_attempt.exception() from e

        return wrapper  # type: ignore

    return decorator


def async_retry_request(config: ESPNConfig) -> Callable[[F], F]:
    """Decorator for retrying asynchronous HTTP requests.

    Args:
        config: ESPN configuration

    Returns:
        Decorated async function
    """
    retry_config = create_retry_config(config)

    def decorator(func: F) -> F:
        async_retrying = AsyncRetrying(**retry_config)

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await async_retrying(func, *args, **kwargs)
            except RetryError as e:
                logger.error(
                    "async_request_failed_after_retries",
                    func_name=func.__name__,
                    retries=config.max_retries,
                    error=str(e),
                )
                # Re-raise the original exception
                raise e.last_attempt.exception() from e

        return wrapper  # type: ignore

    return decorator


def should_retry_exception(exc: Exception) -> bool:
    """Determine if an exception should trigger a retry.

    Args:
        exc: Exception to check

    Returns:
        True if exception should trigger retry
    """
    return isinstance(exc, (ESPNClientError, ESPNRateLimitError))