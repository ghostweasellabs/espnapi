"""Asynchronous ESPN API client."""

from datetime import datetime
from typing import Any

import httpx
import structlog

from espnapi.client.base import BaseESPNClient, ESPNEndpointDomain, ESPNResponse
from espnapi.client.retry import create_retry_config
from espnapi.config import ESPNConfig
from espnapi.exceptions import ESPNClientError

from tenacity import AsyncRetrying, RetryError

logger = structlog.get_logger(__name__)


class AsyncESPNClient(BaseESPNClient):
    """Asynchronous ESPN API client.

    This client provides asynchronous access to ESPN's sports data APIs,
    including teams, events, scores, and athlete information.

    Usage:
        async with AsyncESPNClient() as client:
            response = await client.get_scoreboard("basketball", "nba")
            teams = await client.get_teams("basketball", "nba")
    """

    def __init__(self, config: ESPNConfig | None = None):
        """Initialize the asynchronous ESPN client.

        Args:
            config: ESPN configuration. If None, uses default config.
        """
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None

    @property
    async def client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client (lazy initialization)."""
        if self._client is None or self._client.is_closed is True:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers={
                    "User-Agent": self.config.user_agent,
                    "Accept": "application/json",
                },
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            if self._client.is_closed is False:
                await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncESPNClient":
        """Async context manager entry."""
        _ = await self.client
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __enter__(self) -> "AsyncESPNClient":
        """Disable sync context manager usage."""
        raise RuntimeError("Use 'async with AsyncESPNClient()' for async context management")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Disable sync context manager usage."""
        raise RuntimeError("Use 'async with AsyncESPNClient()' for async context management")

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> ESPNResponse:
        """Make HTTP request with retry logic."""
        retry_config = create_retry_config(self.config)
        async_retrying = AsyncRetrying(**retry_config)

        async def _do_request() -> ESPNResponse:
            logger.debug("espn_async_request", method=method, url=url, params=params)
            client = await self.client
            response = await client.request(method, url, params=params)
            return self._handle_response(response, url)

        try:
            return await async_retrying(_do_request)
        except RetryError as e:
            logger.error(
                "async_request_failed_after_retries",
                method=method,
                url=url,
                retries=self.config.max_retries,
                error=str(e),
            )
            # Re-raise the original exception
            raise e.last_attempt.exception() from e

    async def get(
        self,
        path: str,
        domain: ESPNEndpointDomain = ESPNEndpointDomain.SITE,
        params: dict[str, Any] | None = None,
    ) -> ESPNResponse:
        """Make GET request to ESPN API.

        Args:
            path: API path (e.g., "/apis/site/v2/sports/basketball/nba/scoreboard")
            domain: Which ESPN domain to use
            params: Query parameters

        Returns:
            ESPNResponse with parsed data
        """
        url = self._build_url(domain, path)
        return await self._request_with_retry("GET", url, params=params)

    # --------------------- Scoreboard Endpoints ---------------------

    async def get_scoreboard(
        self,
        sport: str,
        league: str,
        date: str | datetime | None = None,
        limit: int | None = None,
    ) -> ESPNResponse:
        """Get scoreboard/schedule for a sport and league.

        Args:
            sport: Sport slug (e.g., "basketball", "football")
            league: League slug (e.g., "nba", "nfl")
            date: Date to get scoreboard for (YYYYMMDD format or datetime)
            limit: Maximum number of events to return

        Returns:
            ESPNResponse with scoreboard data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/scoreboard"
        params: dict[str, Any] = {}

        if date:
            if isinstance(date, datetime):
                date = date.strftime("%Y%m%d")
            params["dates"] = date

        if limit:
            params["limit"] = limit

        logger.info("fetching_scoreboard", sport=sport, league=league, date=date)
        return await self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    # --------------------- Team Endpoints ---------------------

    async def get_teams(self, sport: str, league: str, limit: int = 100) -> ESPNResponse:
        """Get all teams for a sport and league.

        Args:
            sport: Sport slug (e.g., "basketball", "football")
            league: League slug (e.g., "nba", "nfl")
            limit: Maximum number of teams to return

        Returns:
            ESPNResponse with teams data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams"
        params = {"limit": limit}

        logger.info("fetching_teams", sport=sport, league=league)
        return await self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    async def get_team(self, sport: str, league: str, team_id: str) -> ESPNResponse:
        """Get details for a specific team.

        Args:
            sport: Sport slug
            league: League slug
            team_id: ESPN team ID

        Returns:
            ESPNResponse with team details
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}"

        logger.info("fetching_team", sport=sport, league=league, team_id=team_id)
        return await self.get(path, domain=ESPNEndpointDomain.SITE)

    # --------------------- Event/Game Endpoints ---------------------

    async def get_event(self, sport: str, league: str, event_id: str) -> ESPNResponse:
        """Get details for a specific event/game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID

        Returns:
            ESPNResponse with event details
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/summary"
        params = {"event": event_id}

        logger.info("fetching_event", sport=sport, league=league, event_id=event_id)
        return await self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    # --------------------- Core API Endpoints ---------------------

    async def get_league_info(self, sport: str, league: str) -> ESPNResponse:
        """Get league information from core API.

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with league information
        """
        path = f"/v2/sports/{sport}/leagues/{league}"

        logger.info("fetching_league_info", sport=sport, league=league)
        return await self.get(path, domain=ESPNEndpointDomain.CORE)

    async def get_athletes(
        self,
        sport: str,
        league: str,
        team_id: str | None = None,
        limit: int = 100,
        page: int = 1,
    ) -> ESPNResponse:
        """Get athletes from core API.

        Args:
            sport: Sport slug
            league: League slug
            team_id: Optional team ID to filter by
            limit: Maximum number of athletes
            page: Page number for pagination

        Returns:
            ESPNResponse with athletes data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/athletes"
        params: dict[str, Any] = {"limit": limit, "page": page}

        if team_id:
            params["teams"] = team_id

        logger.info("fetching_athletes", sport=sport, league=league, team_id=team_id)
        return await self.get(path, domain=ESPNEndpointDomain.CORE, params=params)


# Default singleton instance
_default_async_client: AsyncESPNClient | None = None


async def get_async_espn_client() -> AsyncESPNClient:
    """Get the default async ESPN client instance.

    Returns:
        AsyncESPNClient singleton instance
    """
    global _default_async_client
    if _default_async_client is None:
        _default_async_client = AsyncESPNClient()
    return _default_async_client