"""Synchronous ESPN API client."""

from datetime import datetime
from typing import Any

import httpx
import structlog

from espnapi.client.base import BaseESPNClient, ESPNEndpointDomain, ESPNResponse
from espnapi.client.retry import create_retry_config
from espnapi.config import ESPNConfig
from espnapi.exceptions import ESPNClientError

from tenacity import RetryError, Retrying

logger = structlog.get_logger(__name__)


class ESPNClient(BaseESPNClient):
    """Synchronous ESPN API client.

    This client provides synchronous access to ESPN's sports data APIs,
    including teams, events, scores, and athlete information.

    Usage:
        client = ESPNClient()
        response = client.get_scoreboard("basketball", "nba")
        teams = client.get_teams("basketball", "nba")
    """

    def __init__(self, config: ESPNConfig | None = None):
        """Initialize the synchronous ESPN client.

        Args:
            config: ESPN configuration. If None, uses default config.
        """
        super().__init__(config)
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client (lazy initialization)."""
        if self._client is None or self._client.is_closed is True:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.config.timeout),
                headers={
                    "User-Agent": self.config.user_agent,
                    "Accept": "application/json",
                },
                follow_redirects=True,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            if self._client.is_closed is False:
                self._client.close()
            self._client = None

    def __enter__(self) -> "ESPNClient":
        """Context manager entry."""
        _ = self.client
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def _request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> ESPNResponse:
        """Make HTTP request with retry logic."""
        retry_config = create_retry_config(self.config)
        retrying = Retrying(**retry_config)

        def _do_request() -> ESPNResponse:
            logger.debug("espn_request", method=method, url=url, params=params)
            response = self.client.request(method, url, params=params)
            return self._handle_response(response, url)

        try:
            return retrying(_do_request)
        except RetryError as e:
            logger.error(
                "request_failed_after_retries",
                method=method,
                url=url,
                retries=self.config.max_retries,
                error=str(e),
            )
            # Re-raise the original exception
            raise e.last_attempt.exception() from e

    def get(
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
        return self._request_with_retry("GET", url, params=params)

    # --------------------- Scoreboard Endpoints ---------------------

    def get_scoreboard(
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
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    # --------------------- Team Endpoints ---------------------

    def get_teams(self, sport: str, league: str, limit: int = 100) -> ESPNResponse:
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
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    def get_team(self, sport: str, league: str, team_id: str) -> ESPNResponse:
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
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    # --------------------- Event/Game Endpoints ---------------------

    def get_event(self, sport: str, league: str, event_id: str) -> ESPNResponse:
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
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    # --------------------- Core API Endpoints ---------------------

    def get_league_info(self, sport: str, league: str) -> ESPNResponse:
        """Get league information from core API.

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with league information
        """
        path = f"/v2/sports/{sport}/leagues/{league}"

        logger.info("fetching_league_info", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_athletes(
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
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)


# Default singleton instance
_default_client: ESPNClient | None = None


def get_espn_client() -> ESPNClient:
    """Get the default ESPN client instance.

    Returns:
        ESPNClient singleton instance
    """
    global _default_client
    if _default_client is None:
        _default_client = ESPNClient()
    return _default_client