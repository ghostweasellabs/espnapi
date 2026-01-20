"""Integration tests for ESPN API client."""

import asyncio
import pytest

from espnapi.client import ESPNClient


class TestESPNAPIIntegration:
    """Integration tests against real ESPN API."""

    @pytest.mark.integration
    def test_get_nba_teams(self, real_client):
        """Test getting NBA teams from real API."""
        response = real_client.get_teams("basketball", "nba", limit=5)

        assert response.is_success
        # ESPN API nests teams under sports[0].leagues[0].teams
        assert "sports" in response.data
        sports = response.data["sports"]
        assert len(sports) > 0

        leagues = sports[0].get("leagues", [])
        assert len(leagues) > 0

        teams = leagues[0].get("teams", [])
        assert len(teams) > 0

        # Check that we have team data
        team_data = teams[0]["team"]
        assert "id" in team_data
        assert "displayName" in team_data

    @pytest.mark.integration
    def test_get_nfl_teams(self, real_client):
        """Test getting NFL teams from real API."""
        response = real_client.get_teams("football", "nfl", limit=5)

        assert response.is_success
        # ESPN API nests teams under sports[0].leagues[0].teams
        assert "sports" in response.data
        sports = response.data["sports"]
        assert len(sports) > 0

        leagues = sports[0].get("leagues", [])
        assert len(leagues) > 0

        teams = leagues[0].get("teams", [])
        assert len(teams) > 0

    @pytest.mark.integration
    def test_get_scoreboard_today(self, real_client):
        """Test getting today's scoreboard."""
        response = real_client.get_scoreboard("basketball", "nba")

        assert response.is_success
        assert "events" in response.data
        # May or may not have events depending on the day

    @pytest.mark.integration
    def test_get_specific_team(self, real_client):
        """Test getting a specific team by ID."""
        # First get a team ID
        teams_response = real_client.get_teams("basketball", "nba", limit=1)
        assert teams_response.is_success

        # Extract team ID from nested structure
        sports = teams_response.data["sports"]
        leagues = sports[0]["leagues"]
        teams = leagues[0]["teams"]
        team_id = teams[0]["team"]["id"]

        # Now get that specific team
        team_response = real_client.get_team("basketball", "nba", team_id)
        assert team_response.is_success
        assert "team" in team_response.data

    @pytest.mark.integration
    def test_get_league_info(self, real_client):
        """Test getting league information."""
        response = real_client.get_league_info("basketball", "nba")

        assert response.is_success
        # League info structure may vary

    @pytest.mark.integration
    def test_get_athletes(self, real_client):
        """Test getting athletes."""
        response = real_client.get_athletes("basketball", "nba", limit=10)

        assert response.is_success
        # Athletes endpoint may return different structures

    @pytest.mark.integration
    def test_invalid_sport_league(self, real_client):
        """Test with invalid sport/league combination."""
        from espnapi.exceptions import ESPNClientError

        # Should raise an exception for invalid sport/league
        with pytest.raises(ESPNClientError):
            real_client.get_teams("invalid_sport", "invalid_league")

    @pytest.mark.integration
    def test_rate_limiting(self, real_client):
        """Test that rate limiting is handled gracefully."""
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = real_client.get_teams("basketball", "nba", limit=1)
            responses.append(response)

        # At least some should succeed
        success_count = sum(1 for r in responses if r.is_success)
        assert success_count > 5, f"Too many failed requests: {success_count}/10 succeeded"


class TestAsyncESPNAPIIntegration:
    """Integration tests for async ESPN client."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_async_get_nba_teams(self, real_async_client):
        """Test async getting NBA teams from real API."""
        async with real_async_client as client:
            response = await client.get_teams("basketball", "nba", limit=5)

        assert response.is_success
        assert "sports" in response.data
        sports = response.data["sports"]
        assert len(sports) > 0

        leagues = sports[0].get("leagues", [])
        assert len(leagues) > 0

        teams = leagues[0].get("teams", [])
        assert len(teams) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_async_get_scoreboard(self, real_async_client):
        """Test async getting scoreboard."""
        async with real_async_client as client:
            response = await client.get_scoreboard("basketball", "nba")

        assert response.is_success
        assert "events" in response.data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_async_multiple_requests(self, real_async_client):
        """Test multiple async requests."""
        async with real_async_client as client:
            # Make concurrent requests
            teams_task = client.get_teams("basketball", "nba", limit=3)
            scoreboard_task = client.get_scoreboard("basketball", "nba")

            teams_response, scoreboard_response = await asyncio.gather(
                teams_task, scoreboard_task
            )

        assert teams_response.is_success
        assert scoreboard_response.is_success