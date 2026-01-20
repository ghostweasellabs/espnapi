import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

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
