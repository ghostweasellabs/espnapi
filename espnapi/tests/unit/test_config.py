"""Unit tests for ESPNConfig."""

import pytest

from espnapi.config import ESPNConfig


class TestESPNConfig:
    """Test ESPNConfig validation and defaults."""

    def test_defaults(self):
        """Default configuration values."""
        config = ESPNConfig()
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_backoff == 1.0

    def test_invalid_timeout(self):
        """Timeout must be positive."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            ESPNConfig(timeout=0)

    def test_invalid_max_retries(self):
        """Max retries must be non-negative."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            ESPNConfig(max_retries=-1)

    def test_invalid_retry_backoff(self):
        """Retry backoff must be positive."""
        with pytest.raises(ValueError, match="retry_backoff must be positive"):
            ESPNConfig(retry_backoff=0)

    def test_invalid_rate_limit_requests(self):
        """Rate limit requests must be positive."""
        with pytest.raises(ValueError, match="rate_limit_requests must be positive"):
            ESPNConfig(rate_limit_requests=0)

    def test_invalid_rate_limit_period(self):
        """Rate limit period must be positive."""
        with pytest.raises(ValueError, match="rate_limit_period must be positive"):
            ESPNConfig(rate_limit_period=0)
