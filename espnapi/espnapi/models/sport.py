"""Sport and League models for espnapi."""

from typing import Optional

from pydantic import Field

from espnapi.models.base import ESPNModel


class Sport(ESPNModel):
    """Sport entity (e.g., basketball, football).

    Represents a sport category that contains multiple leagues.
    """

    slug: str = Field(..., description="URL-friendly identifier (e.g., 'basketball')")
    name: str = Field(..., description="Display name (e.g., 'Basketball')")

    def __str__(self) -> str:
        """String representation."""
        return self.name


class League(ESPNModel):
    """League entity (e.g., NBA, NFL).

    Represents a specific league within a sport.
    """

    sport: Sport = Field(..., description="Parent sport")
    slug: str = Field(..., description="URL-friendly identifier (e.g., 'nba')")
    name: str = Field(..., description="Display name (e.g., 'NBA')")
    abbreviation: Optional[str] = Field(None, description="Short form (e.g., 'NBA')")

    def __str__(self) -> str:
        """String representation."""
        sport_name = self.sport.name if isinstance(self.sport, Sport) else str(self.sport)
        return f"{self.name} ({sport_name})"

    @property
    def sport_slug(self) -> str:
        """Get sport slug from sport object or string."""
        if isinstance(self.sport, Sport):
            return self.sport.slug
        return str(self.sport)


# Predefined sports for convenience
SPORTS = {
    "basketball": Sport(slug="basketball", name="Basketball"),
    "football": Sport(slug="football", name="Football"),
    "baseball": Sport(slug="baseball", name="Baseball"),
    "hockey": Sport(slug="hockey", name="Hockey"),
    "soccer": Sport(slug="soccer", name="Soccer"),
    "mma": Sport(slug="mma", name="Mixed Martial Arts"),
    "golf": Sport(slug="golf", name="Golf"),
    "tennis": Sport(slug="tennis", name="Tennis"),
    "racing": Sport(slug="racing", name="Racing"),
}

# Predefined leagues for convenience
LEAGUES = {
    "nba": League(sport=SPORTS["basketball"], slug="nba", name="NBA", abbreviation="NBA"),
    "wnba": League(sport=SPORTS["basketball"], slug="wnba", name="WNBA", abbreviation="WNBA"),
    "nfl": League(sport=SPORTS["football"], slug="nfl", name="NFL", abbreviation="NFL"),
    "mlb": League(sport=SPORTS["baseball"], slug="mlb", name="MLB", abbreviation="MLB"),
    "nhl": League(sport=SPORTS["hockey"], slug="nhl", name="NHL", abbreviation="NHL"),
    "mls": League(sport=SPORTS["soccer"], slug="mls", name="MLS", abbreviation="MLS"),
    "college-football": League(
        sport=SPORTS["football"], slug="college-football", name="College Football", abbreviation="NCAAF"
    ),
    "mens-college-basketball": League(
        sport=SPORTS["basketball"],
        slug="mens-college-basketball",
        name="Men's College Basketball",
        abbreviation="NCAAM",
    ),
}