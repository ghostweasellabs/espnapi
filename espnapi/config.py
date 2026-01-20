"""ESPN API client configuration."""

from dataclasses import dataclass


@dataclass
class ESPNConfig:
    """Configuration for ESPN API client."""

    # API URLs
    site_api_base_url: str = "https://site.api.espn.com"
    core_api_base_url: str = "https://sports.core.api.espn.com"

    # Request settings
    timeout: float = 30.0
    max_retries: int = 3
    retry_backoff: float = 1.0

    # Headers
    user_agent: str = "espnapi/0.1.0"

    # Rate limiting (requests per period)
    rate_limit_requests: int = 60
    rate_limit_period: int = 60

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_backoff <= 0:
            raise ValueError("retry_backoff must be positive")
        if self.rate_limit_requests <= 0:
            raise ValueError("rate_limit_requests must be positive")
        if self.rate_limit_period <= 0:
            raise ValueError("rate_limit_period must be positive")