"""Shared test fixtures and utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock


def pytest_configure(config: pytest.Config) -> None:
    """Keep strict coverage for unit runs; relax for integration/e2e-only runs."""
    # Default to the pyproject threshold unless we detect integration/e2e-only.
    config.option.cov_fail_under = getattr(config.option, "cov_fail_under", 90)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Disable coverage gating if only integration/e2e tests are selected."""
    if not items:
        return

    def _has_marker(item: pytest.Item, name: str) -> bool:
        return item.get_closest_marker(name) is not None

    all_integration_or_e2e = all(
        _has_marker(item, "integration") or _has_marker(item, "e2e") for item in items
    )

    if all_integration_or_e2e:
        config.option.cov_fail_under = 0


@pytest.fixture
def mock_response():
    """Mock httpx Response object."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"test": "data"}
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_async_response():
    """Mock httpx AsyncResponse object."""
    response = AsyncMock()
    response.status_code = 200
    response.json.return_value = {"test": "data"}
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "id": "1",
        "uid": "s:20~l:28~t:1",
        "slug": "los-angeles-lakers",
        "abbreviation": "LAL",
        "displayName": "Los Angeles Lakers",
        "shortDisplayName": "Lakers",
        "name": "Lakers",
        "nickname": "Los Angeles",
        "location": "Los Angeles",
        "color": "552583",
        "alternateColor": "FDB927",
        "isActive": True,
        "isAllStar": False,
        "logos": [{"href": "https://example.com/logo.png"}],
        "links": [{"rel": ["clubhouse"], "href": "https://example.com"}],
    }


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "id": "401468034",
        "uid": "s:20~l:28~e:401468034",
        "date": "2024-01-15T20:00Z",
        "name": "Los Angeles Lakers at Boston Celtics",
        "shortName": "LAL @ BOS",
        "season": {"year": 2024, "type": 2, "slug": "regular-season"},
        "status": {
            "clock": "0.0",
            "displayClock": "0:00",
            "period": 1,
            "type": {"id": "1", "name": "STATUS_SCHEDULED", "state": "pre", "completed": False},
        },
        "competitions": [
            {
                "venue": {"id": "2132", "fullName": "TD Garden"},
                "competitors": [
                    {
                        "id": "2",
                        "team": {
                            "id": "2",
                            "abbreviation": "BOS",
                            "displayName": "Boston Celtics",
                        },
                        "score": "0",
                        "homeAway": "home",
                        "winner": False,
                    },
                    {
                        "id": "13",
                        "team": {
                            "id": "13",
                            "abbreviation": "LAL",
                            "displayName": "Los Angeles Lakers",
                        },
                        "score": "0",
                        "homeAway": "away",
                        "winner": False,
                    },
                ],
            }
        ],
    }