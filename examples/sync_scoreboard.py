import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from espnapi import ESPNClient, ESPNClientError


def main() -> None:
    try:
        with ESPNClient() as client:
            response = client.get_scoreboard("basketball", "nba")
            events = response.data.get("events", [])
            print(events)
    except ESPNClientError as exc:
        print(f"ESPN error: {exc}")


if __name__ == "__main__":
    main()
