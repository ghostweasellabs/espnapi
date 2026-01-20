"""Base ESPN API client with shared logic."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

from espnapi.config import ESPNConfig
from espnapi.exceptions import ESPNClientError, ESPNNotFoundError, ESPNRateLimitError

logger = structlog.get_logger(__name__)


class ESPNEndpointDomain(str, Enum):
    """ESPN API domain types."""

    SITE = "site"  # site.api.espn.com
    CORE = "core"  # sports.core.api.espn.com


@dataclass
class ESPNResponse:
    """Wrapper for ESPN API responses."""

    data: dict[str, Any]
    status_code: int
    url: str

    @property
    def is_success(self) -> bool:
        """Check if response is successful."""
        return 200 <= self.status_code < 300


class BaseESPNClient(ABC):
    """Base ESPN API client with shared logic.

    This class provides the common functionality used by both sync and async clients,
    including URL building, response handling, and configuration management.
    """

    def __init__(self, config: ESPNConfig | None = None):
        """Initialize the ESPN client.

        Args:
            config: ESPN configuration. If None, uses default config.
        """
        self.config = config or ESPNConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate client configuration."""
        if self.config.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.config.max_retries < 0:
            raise ValueError("max_retries must be non-negative")

    def _get_base_url(self, domain: ESPNEndpointDomain) -> str:
        """Get base URL for the given domain.

        Args:
            domain: ESPN API domain

        Returns:
            Base URL string
        """
        if domain == ESPNEndpointDomain.SITE:
            return self.config.site_api_base_url
        return self.config.core_api_base_url

    def _build_url(self, domain: ESPNEndpointDomain, path: str) -> str:
        """Build full URL from domain and path.

        Args:
            domain: ESPN API domain
            path: API path (with or without leading slash)

        Returns:
            Full URL string
        """
        base_url = self._get_base_url(domain)
        path = path.lstrip("/")
        return f"{base_url}/{path}"

    def _handle_response(self, response: Any, url: str) -> ESPNResponse:
        """Handle HTTP response and convert to ESPNResponse.

        Args:
            response: HTTP response object (httpx.Response)
            url: Request URL for logging

        Returns:
            ESPNResponse with parsed data

        Raises:
            ESPNNotFoundError: If resource not found (404)
            ESPNRateLimitError: If rate limited (429)
            ESPNClientError: For other HTTP errors
        """
        # Handle HTTP errors
        if response.status_code == 404:
            logger.warning("espn_resource_not_found", url=url)
            raise ESPNNotFoundError(f"ESPN resource not found: {url}")

        if response.status_code == 429:
            logger.warning("espn_rate_limited", url=url)
            raise ESPNRateLimitError("ESPN API rate limit exceeded")

        if response.status_code >= 500:
            logger.error(
                "espn_server_error",
                url=url,
                status_code=response.status_code,
            )
            raise ESPNClientError(f"ESPN server error: {response.status_code}")

        if response.status_code >= 400:
            logger.error(
                "espn_client_error",
                url=url,
                status_code=response.status_code,
            )
            raise ESPNClientError(f"ESPN API error: {response.status_code}")

        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            logger.error("espn_json_parse_error", url=url, error=str(e))
            raise ESPNClientError(f"Failed to parse ESPN response: {e}") from e

        return ESPNResponse(data=data, status_code=response.status_code, url=url)

    @abstractmethod
    def close(self) -> None:
        """Close the HTTP client."""
        pass

    @abstractmethod
    def __enter__(self) -> "BaseESPNClient":
        """Context manager entry."""
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        pass