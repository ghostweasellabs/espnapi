import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from espnapi import AsyncESPNClient


async def main() -> None:
    async with AsyncESPNClient() as client:
        response = await client.get_teams("football", "nfl", limit=5)
        print(response.data.get("sports", []))


if __name__ == "__main__":
    asyncio.run(main())
