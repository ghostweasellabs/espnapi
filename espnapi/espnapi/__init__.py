"""ESPN API client library.

A modern, async-enabled Python library for accessing ESPN sports data.
"""

__version__ = "0.1.0"

from espnapi.client import ESPNClient, AsyncESPNClient
from espnapi.config import ESPNConfig
from espnapi.exceptions import (
    ESPNClientError,
    ESPNNotFoundError,
    ESPNRateLimitError,
)

__all__ = [
    "ESPNClient",
    "AsyncESPNClient",
    "ESPNConfig",
    "ESPNClientError",
    "ESPNNotFoundError",
    "ESPNRateLimitError",
]