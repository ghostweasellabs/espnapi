"""Unit tests for retry helpers."""

import pytest

from espnapi.client.retry import (
    async_retry_request,
    create_retry_config,
    retry_request,
    should_retry_exception,
)
from espnapi.config import ESPNConfig
from espnapi.exceptions import ESPNClientError, ESPNRateLimitError


class TestRetryHelpers:
    """Test retry helpers."""

    def test_create_retry_config(self):
        """Retry config uses config values."""
        config = ESPNConfig(max_retries=5, retry_backoff=2.0)
        retry_config = create_retry_config(config)
        assert retry_config["stop"].max_attempt_number == 5
        assert retry_config["wait"].multiplier == 2.0

    def test_should_retry_exception(self):
        """Retry eligibility for exceptions."""
        assert should_retry_exception(ESPNClientError("x"))
        assert should_retry_exception(ESPNRateLimitError("x"))
        assert not should_retry_exception(ValueError("x"))

    def test_retry_request_success_after_failures(self):
        """Retry succeeds after transient failures."""
        config = ESPNConfig(max_retries=3, retry_backoff=0.01)
        attempts = {"count": 0}

        @retry_request(config)
        def flaky():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ESPNClientError("fail")
            return "ok"

        assert flaky() == "ok"
        assert attempts["count"] == 3

    @pytest.mark.asyncio
    async def test_async_retry_request_success_after_failures(self):
        """Async retry succeeds after transient failures."""
        config = ESPNConfig(max_retries=3, retry_backoff=0.01)
        attempts = {"count": 0}

        @async_retry_request(config)
        async def flaky_async():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ESPNClientError("fail")
            return "ok"

        assert await flaky_async() == "ok"
        assert attempts["count"] == 3
