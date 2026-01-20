import pytest

from espnapi.client import ESPNClient


@pytest.mark.e2e
def test_scoreboard_to_event_flow():
    with ESPNClient() as client:
        scoreboard = client.get_scoreboard("basketball", "nba", limit=1)
        events = scoreboard.data.get("events", [])
        assert events, "Expected at least one event for the e2e flow"

        event_id = events[0]["id"]
        event = client.get_event("basketball", "nba", event_id)
        assert event.is_success
