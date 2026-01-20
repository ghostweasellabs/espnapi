# espnapi

A modern, async-capable Python client for ESPN public APIs.

## Features

- Sync and async clients
- Typed models (Pydantic)
- Configurable retries and timeouts
- Structured logging
- Unit + integration tests

## Install

```bash
uv add espnapi
```

## Quick Start (Sync)

```python
from espnapi import ESPNClient

client = ESPNClient()
response = client.get_scoreboard("basketball", "nba")
print(response.data)
client.close()
```

## Quick Start (Async)

```python
import asyncio
from espnapi import AsyncESPNClient


async def main():
    async with AsyncESPNClient() as client:
        response = await client.get_teams("basketball", "nba", limit=10)
        print(response.data)


asyncio.run(main())
```

## Examples

Run the bundled examples:

```bash
uv run python examples/sync_scoreboard.py
uv run python examples/async_teams.py
uv run python examples/e2e_flow.py
```

Sync scoreboard with basic error handling:

```python
from espnapi import ESPNClient, ESPNClientError


def main() -> None:
    try:
        with ESPNClient() as client:
            response = client.get_scoreboard("basketball", "nba")
            print(response.data.get("events", []))
    except ESPNClientError as exc:
        print(f"ESPN error: {exc}")


if __name__ == "__main__":
    main()
```

Async teams fetch:

```python
import asyncio

from espnapi import AsyncESPNClient


async def main() -> None:
    async with AsyncESPNClient() as client:
        response = await client.get_teams("football", "nfl", limit=5)
        print(response.data.get("sports", []))


if __name__ == "__main__":
    asyncio.run(main())
```

End-to-end flow (scoreboard -> event detail):

```python
from espnapi import ESPNClient


def main() -> None:
    with ESPNClient() as client:
        scoreboard = client.get_scoreboard("basketball", "nba", limit=1)
        events = scoreboard.data.get("events", [])
        if not events:
            print("No events found.")
            return
        event_id = events[0]["id"]
        detail = client.get_event("basketball", "nba", event_id)
        print(detail.data.get("boxscore", {}).get("id"))


if __name__ == "__main__":
    main()
```

## Configuration

```python
from espnapi import ESPNClient, ESPNConfig

config = ESPNConfig(
    timeout=20.0,
    max_retries=3,
    retry_backoff=1.0,
    user_agent="my-app/1.0",
)

client = ESPNClient(config)
```

## Models

```python
from espnapi.models import Team, League

league = League(sport={"slug": "basketball", "name": "Basketball"}, slug="nba", name="NBA")
team = Team.from_espn_data({"id": "1", "displayName": "Los Angeles Lakers"}, league)
print(team.display_name)
```

## Tests

```bash
# Unit tests (default skips integration)
uv run pytest

# Run integration tests explicitly
uv run pytest -m integration

# Run end-to-end tests explicitly
uv run pytest -m e2e

# Run the full suite (unit + integration + e2e) with coverage
uv run pytest -m "not slow"
```

### Example Tests

Unit test example (mocked httpx client):

```python
from unittest.mock import MagicMock

import httpx

from espnapi.client.sync import ESPNClient


def test_get_scoreboard_unit():
    client = ESPNClient()
    mock_httpx = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"events": []}
    mock_httpx.request.return_value = mock_response
    client._client = mock_httpx

    response = client.get_scoreboard("basketball", "nba")
    assert response.is_success
```

Integration test example (real API call):

```python
import pytest

from espnapi.client import ESPNClient


@pytest.mark.integration
def test_get_nba_teams_integration():
    with ESPNClient() as client:
        response = client.get_teams("basketball", "nba", limit=1)
        assert response.is_success
```

E2E test example (real flow):

```python
import pytest

from espnapi.client import ESPNClient


@pytest.mark.e2e
def test_scoreboard_to_event_e2e():
    with ESPNClient() as client:
        scoreboard = client.get_scoreboard("basketball", "nba", limit=1)
        events = scoreboard.data.get("events", [])
        assert events
        event_id = events[0]["id"]
        event = client.get_event("basketball", "nba", event_id)
        assert event.is_success
```

## Development

```bash
uv sync
uv run black .
uv run ruff check .
uv run mypy espnapi
```

## License

MIT
