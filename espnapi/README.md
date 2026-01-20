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