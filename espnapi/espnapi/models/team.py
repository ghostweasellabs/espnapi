"""Team model for espnapi."""

from typing import List, Optional

from pydantic import Field

from espnapi.models.base import ESPNModel, Link, Logo
from espnapi.models.sport import League


class Team(ESPNModel):
    """Team entity representing a sports team.

    Contains team information, branding, and metadata.
    """

    # League association
    league: League = Field(..., description="League this team belongs to")

    # ESPN identifiers
    espn_id: str = Field(..., description="ESPN's unique team identifier")
    uid: Optional[str] = Field(None, description="ESPN's universal identifier")
    slug: Optional[str] = Field(None, description="URL-friendly slug")

    # Names and branding
    abbreviation: str = Field(..., description="Team abbreviation (e.g., 'LAL')")
    display_name: str = Field(..., description="Full display name (e.g., 'Los Angeles Lakers')")
    short_display_name: Optional[str] = Field(None, description="Shortened display name")
    name: Optional[str] = Field(None, description="Team name only (e.g., 'Lakers')")
    nickname: Optional[str] = Field(None, description="City/location nickname")
    location: Optional[str] = Field(None, description="Team location/city")

    # Colors and branding
    color: Optional[str] = Field(None, description="Primary team color (hex)")
    alternate_color: Optional[str] = Field(None, description="Secondary team color (hex)")

    # Status
    is_active: bool = Field(True, description="Whether team is currently active")
    is_all_star: bool = Field(False, description="Whether this is an All-Star team")

    # Media assets
    logos: List[Logo] = Field(default_factory=list, description="Team logos")
    links: List[Link] = Field(default_factory=list, description="Related links")

    def __str__(self) -> str:
        """String representation."""
        league_abbr = self.league.abbreviation or self.league.slug.upper()
        return f"{self.display_name} ({league_abbr})"

    @property
    def primary_logo(self) -> Optional[str]:
        """Get the primary logo URL.

        Returns:
            URL of the primary logo, or None if no logos available
        """
        if not self.logos:
            return None

        # Look for default logo first
        for logo in self.logos:
            if "default" in logo.rel:
                return logo.href

        # Fallback to first logo
        return self.logos[0].href if self.logos else None

    @property
    def logo_url(self) -> Optional[str]:
        """Alias for primary_logo for backward compatibility."""
        return self.primary_logo

    @property
    def team_name(self) -> str:
        """Get the team name, preferring short forms."""
        return (
            self.name or
            self.short_display_name or
            self.display_name
        )

    @property
    def full_name(self) -> str:
        """Get the full team name."""
        return self.display_name

    @classmethod
    def from_espn_data(cls, data: dict, league: League) -> "Team":
        """Create Team instance from ESPN API data.

        Args:
            data: Raw team data from ESPN API
            league: League this team belongs to

        Returns:
            Team instance
        """
        # Extract nested team data if present
        team_data = data.get("team", data)

        # Convert logos and links
        logos = []
        if team_data.get("logos"):
            for logo_data in team_data["logos"]:
                if isinstance(logo_data, dict):
                    logos.append(Logo(**logo_data))

        links = []
        if team_data.get("links"):
            for link_data in team_data["links"]:
                if isinstance(link_data, dict):
                    links.append(Link(**link_data))

        return cls(
            league=league,
            espn_id=str(team_data.get("id", "")),
            uid=team_data.get("uid"),
            slug=team_data.get("slug"),
            abbreviation=team_data.get("abbreviation", ""),
            display_name=team_data.get("displayName", ""),
            short_display_name=team_data.get("shortDisplayName"),
            name=team_data.get("name"),
            nickname=team_data.get("nickname"),
            location=team_data.get("location"),
            color=team_data.get("color"),
            alternate_color=team_data.get("alternateColor"),
            is_active=team_data.get("isActive", True),
            is_all_star=team_data.get("isAllStar", False),
            logos=logos,
            links=links,
            raw_data=team_data,
        )