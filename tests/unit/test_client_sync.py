"""Unit tests for synchronous ESPN client."""

import pytest
from unittest.mock import MagicMock, patch

from espnapi.client.base import ESPNEndpointDomain
from espnapi.client.sync import ESPNClient
from espnapi.config import ESPNConfig
from espnapi.exceptions import ESPNClientError, ESPNNotFoundError, ESPNRateLimitError


class TestESPNClient:
    """Test cases for synchronous ESPN client."""

    @pytest.fixture
    def config(self):
        """Test configuration."""
        return ESPNConfig(
            site_api_base_url="https://test.api.espn.com",
            core_api_base_url="https://test.core.api.espn.com",
            timeout=10.0,
            max_retries=2,
        )

    @pytest.fixture
    def client(self, config):
        """Test client instance."""
        return ESPNClient(config)

    def test_initialization(self, config):
        """Test client initialization."""
        client = ESPNClient(config)
        assert client.config == config
        assert client._client is None  # Lazy initialization

    def test_context_manager(self, client):
        """Test context manager usage."""
        with client as c:
            assert c is client
            assert c._client is not None
        assert client._client is None  # Should be closed

    @patch("httpx.Client")
    def test_client_property_lazy_init(self, mock_client_class, client):
        """Test lazy initialization of HTTP client."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        # Access client property
        http_client = client.client

        # Verify client was created
        mock_client_class.assert_called_once()
        assert http_client == mock_client_instance

    @patch("httpx.Client")
    def test_client_property_reuse(self, mock_client_class, client):
        """Test that client property reuses existing client."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        # Access client property twice
        client1 = client.client
        client2 = client.client

        # Should be the same instance
        assert client1 is client2
        mock_client_class.assert_called_once()

    @patch("httpx.Client")
    def test_client_property_recreate_after_close(self, mock_client_class, client):
        """Test client recreation after close."""
        mock_client_instance1 = MagicMock()
        mock_client_instance2 = MagicMock()
        mock_client_class.side_effect = [mock_client_instance1, mock_client_instance2]

        # Get client
        client.client
        assert client._client == mock_client_instance1

        # Close client
        client.close()
        assert client._client is None

        # Get client again - should create new instance
        client.client
        assert client._client == mock_client_instance2
        assert mock_client_class.call_count == 2

    def test_build_url_site_domain(self, client):
        """Test URL building for site domain."""
        url = client._build_url(ESPNEndpointDomain.SITE, "test/path")
        assert url == "https://test.api.espn.com/test/path"

    def test_build_url_core_domain(self, client):
        """Test URL building for core domain."""
        url = client._build_url(ESPNEndpointDomain.CORE, "test/path")
        assert url == "https://test.core.api.espn.com/test/path"

    def test_build_url_with_leading_slash(self, client):
        """Test URL building handles leading slashes."""
        url = client._build_url(ESPNEndpointDomain.SITE, "/test/path")
        assert url == "https://test.api.espn.com/test/path"

    def test_handle_response_success(self, client):
        """Test successful response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}

        result = client._handle_response(mock_response, "test_url")

        assert result.status_code == 200
        assert result.data == {"test": "data"}
        assert result.url == "test_url"

    def test_handle_response_404_error(self, client):
        """Test 404 response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with pytest.raises(ESPNNotFoundError, match="ESPN resource not found"):
            client._handle_response(mock_response, "test_url")

    def test_handle_response_429_error(self, client):
        """Test 429 response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 429

        with pytest.raises(ESPNRateLimitError, match="ESPN API rate limit exceeded"):
            client._handle_response(mock_response, "test_url")

    def test_handle_response_500_error(self, client):
        """Test 500 response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with pytest.raises(ESPNClientError, match="ESPN server error: 500"):
            client._handle_response(mock_response, "test_url")

    def test_handle_response_400_error(self, client):
        """Test 400 response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 400

        with pytest.raises(ESPNClientError, match="ESPN API error: 400"):
            client._handle_response(mock_response, "test_url")

    def test_handle_response_json_error(self, client):
        """Test JSON parsing error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with pytest.raises(ESPNClientError, match="Failed to parse ESPN response"):
            client._handle_response(mock_response, "test_url")

    @patch("httpx.Client")
    def test_get_method(self, mock_client_class, client):
        """Test GET method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_client_instance.request.return_value = mock_response

        result = client.get("test/path", params={"key": "value"})

        mock_client_instance.request.assert_called_once_with(
            "GET", "https://test.api.espn.com/test/path", params={"key": "value"}
        )
        assert result.data == {"data": "test"}
        assert result.status_code == 200

    @patch("httpx.Client")
    def test_get_scoreboard(self, mock_client_class, client):
        """Test get_scoreboard method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"events": []}
        mock_client_instance.request.return_value = mock_response

        result = client.get_scoreboard("basketball", "nba", date="20241215", limit=10)

        expected_url = "https://test.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        mock_client_instance.request.assert_called_once_with(
            "GET", expected_url, params={"dates": "20241215", "limit": 10}
        )
        assert result.data == {"events": []}

    @patch("httpx.Client")
    def test_get_scoreboard_datetime(self, mock_client_class, client):
        """Test get_scoreboard with datetime object."""
        from datetime import datetime

        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"events": []}
        mock_client_instance.request.return_value = mock_response

        test_date = datetime(2024, 12, 15)
        result = client.get_scoreboard("basketball", "nba", date=test_date)

        expected_url = "https://test.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        mock_client_instance.request.assert_called_once_with(
            "GET", expected_url, params={"dates": "20241215"}
        )

    @patch("httpx.Client")
    def test_get_teams(self, mock_client_class, client):
        """Test get_teams method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"teams": []}
        mock_client_instance.request.return_value = mock_response

        result = client.get_teams("basketball", "nba", limit=50)

        expected_url = "https://test.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        mock_client_instance.request.assert_called_once_with(
            "GET", expected_url, params={"limit": 50}
        )
        assert result.data == {"teams": []}

    @patch("httpx.Client")
    def test_get_team(self, mock_client_class, client):
        """Test get_team method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"team": {"id": "1"}}
        mock_client_instance.request.return_value = mock_response

        result = client.get_team("basketball", "nba", "1")

        expected_url = "https://test.api.espn.com/apis/site/v2/sports/basketball/nba/teams/1"
        mock_client_instance.request.assert_called_once_with("GET", expected_url, params=None)
        assert result.data == {"team": {"id": "1"}}

    @patch("httpx.Client")
    def test_get_event(self, mock_client_class, client):
        """Test get_event method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"event": {"id": "123"}}
        mock_client_instance.request.return_value = mock_response

        result = client.get_event("basketball", "nba", "123")

        expected_url = "https://test.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
        mock_client_instance.request.assert_called_once_with(
            "GET", expected_url, params={"event": "123"}
        )
        assert result.data == {"event": {"id": "123"}}

    @patch("httpx.Client")
    def test_get_league_info(self, mock_client_class, client):
        """Test get_league_info method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"league": {"id": "nba"}}
        mock_client_instance.request.return_value = mock_response

        result = client.get_league_info("basketball", "nba")

        expected_url = "https://test.core.api.espn.com/v2/sports/basketball/leagues/nba"
        mock_client_instance.request.assert_called_once_with("GET", expected_url, params=None)
        assert result.data == {"league": {"id": "nba"}}

    @patch("httpx.Client")
    def test_get_athletes(self, mock_client_class, client):
        """Test get_athletes method."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"athletes": []}
        mock_client_instance.request.return_value = mock_response

        result = client.get_athletes("basketball", "nba", team_id="1", limit=25, page=2)

        expected_url = "https://test.core.api.espn.com/v2/sports/basketball/leagues/nba/athletes"
        mock_client_instance.request.assert_called_once_with(
            "GET", expected_url, params={"limit": 25, "page": 2, "teams": "1"}
        )
        assert result.data == {"athletes": []}

    @patch("httpx.Client")
    def test_get_athletes_no_team(self, mock_client_class, client):
        """Test get_athletes method without team filter."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"athletes": []}
        mock_client_instance.request.return_value = mock_response

        result = client.get_athletes("basketball", "nba", limit=100, page=1)

        expected_url = "https://test.core.api.espn.com/v2/sports/basketball/leagues/nba/athletes"
        mock_client_instance.request.assert_called_once_with(
            "GET", expected_url, params={"limit": 100, "page": 1}
        )