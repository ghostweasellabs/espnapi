"""Integration test fixtures."""

import pytest


@pytest.fixture(scope="session")
def real_client():
    """Real ESPN client for integration tests."""
    from espnapi.client import ESPNClient
    return ESPNClient()


@pytest.fixture(scope="session")
def real_async_client():
    """Real async ESPN client for integration tests."""
    from espnapi.client.async_client import AsyncESPNClient
    return AsyncESPNClient()