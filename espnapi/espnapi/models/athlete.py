"""Athlete model for espnapi."""

from datetime import date
from typing import List, Optional

from pydantic import Field

from espnapi.models.base import ESPNModel, Link
from espnapi.models.team import Team


class Athlete(ESPNModel):
    """Athlete entity representing a player or competitor."""

    # ESPN identifiers
    espn_id: str = Field(..., description="ESPN's unique athlete identifier")
    uid: Optional[str] = Field(None, description="ESPN's universal identifier")

    # Names
    first_name: str = Field(..., description="Athlete's first name")
    last_name: str = Field(..., description="Athlete's last name")
    full_name: str = Field(..., description="Complete athlete name")
    display_name: str = Field(..., description="Display name for athlete")
    short_name: Optional[str] = Field(None, description="Shortened display name")

    # Team association
    team: Optional[Team] = Field(None, description="Current team (null for free agents)")

    # Position information
    position: Optional[str] = Field(None, description="Full position name")
    position_abbreviation: Optional[str] = Field(None, description="Position abbreviation")

    # Jersey and status
    jersey: Optional[str] = Field(None, description="Jersey number")
    is_active: bool = Field(True, description="Whether athlete is currently active")

    # Physical attributes
    height: Optional[str] = Field(None, description="Height (e.g., '6'8\"')")
    weight: Optional[int] = Field(None, description="Weight in pounds")
    age: Optional[int] = Field(None, description="Age in years")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    birth_place: Optional[str] = Field(None, description="Place of birth")

    # Media
    headshot: Optional[str] = Field(None, description="Headshot image URL")

    # Links
    links: List[Link] = Field(default_factory=list, description="Related links")

    def __str__(self) -> str:
        """String representation."""
        team_abbr = self.team.abbreviation if self.team else "FA"
        return f"{self.display_name} ({team_abbr})"

    @property
    def name(self) -> str:
        """Get preferred name for display."""
        return self.display_name or self.full_name

    @property
    def team_name(self) -> Optional[str]:
        """Get team name if athlete has a team."""
        return self.team.display_name if self.team else None

    @property
    def position_display(self) -> str:
        """Get position for display."""
        return self.position_abbreviation or self.position or "Unknown"

    @classmethod
    def from_espn_data(cls, data: dict, team: Optional[Team] = None) -> "Athlete":
        """Create Athlete instance from ESPN API data.

        Args:
            data: Raw athlete data from ESPN API
            team: Current team (if known)

        Returns:
            Athlete instance
        """
        # Handle nested athlete data
        athlete_data = data.get("athlete", data)

        # Convert links
        links = []
        if athlete_data.get("links"):
            for link_data in athlete_data["links"]:
                if isinstance(link_data, dict):
                    links.append(Link(**link_data))

        return cls(
            espn_id=str(athlete_data.get("id", "")),
            uid=athlete_data.get("uid"),
            first_name=athlete_data.get("firstName", ""),
            last_name=athlete_data.get("lastName", ""),
            full_name=athlete_data.get("fullName", ""),
            display_name=athlete_data.get("displayName", ""),
            short_name=athlete_data.get("shortName"),
            team=team,
            position=athlete_data.get("position", {}).get("name"),
            position_abbreviation=athlete_data.get("position", {}).get("abbreviation"),
            jersey=athlete_data.get("jersey"),
            is_active=athlete_data.get("active", True),
            height=athlete_data.get("height"),
            weight=athlete_data.get("weight"),
            age=athlete_data.get("age"),
            birth_date=athlete_data.get("dateOfBirth"),
            birth_place=athlete_data.get("birthPlace", {}).get("city"),
            headshot=athlete_data.get("headshot", {}).get("href"),
            links=links,
            raw_data=athlete_data,
        )