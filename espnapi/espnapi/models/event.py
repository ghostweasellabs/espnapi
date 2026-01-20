"""Event and Competitor models for espnapi."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from espnapi.models.base import ESPNModel, Link, Record, Statistic
from espnapi.models.sport import League
from espnapi.models.team import Team
from espnapi.models.venue import Venue


class EventStatus(str, Enum):
    """Event status enumeration."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class Event(ESPNModel):
    """Event/game entity representing a sports event."""

    # League and venue
    league: League = Field(..., description="League this event belongs to")
    venue: Optional[Venue] = Field(None, description="Venue where event takes place")

    # ESPN identifiers
    espn_id: str = Field(..., description="ESPN's unique event identifier")
    uid: Optional[str] = Field(None, description="ESPN's universal identifier")

    # Event details
    date: datetime = Field(..., description="When the event occurs")
    name: str = Field(..., description="Full event name")
    short_name: Optional[str] = Field(None, description="Shortened event name")

    # Season information
    season_year: int = Field(..., description="Year of the season")
    season_type: int = Field(2, description="Season type (1=preseason, 2=regular, 3=postseason)")
    season_slug: Optional[str] = Field(None, description="Season slug")
    week: Optional[int] = Field(None, description="Week number (for seasonal sports)")

    # Status information
    status: EventStatus = Field(EventStatus.SCHEDULED, description="Current event status")
    status_detail: Optional[str] = Field(None, description="Detailed status information")
    clock: Optional[str] = Field(None, description="Game clock (e.g., '12:34')")
    period: Optional[int] = Field(None, description="Current period/quarter")

    # Event metadata
    attendance: Optional[int] = Field(None, description="Attendance count")
    broadcasts: List[dict] = Field(default_factory=list, description="Broadcast information")
    links: List[Link] = Field(default_factory=list, description="Related links")

    def __str__(self) -> str:
        """String representation."""
        date_str = self.date.strftime("%Y-%m-%d")
        name = self.short_name or self.name or "Unknown Event"
        return f"{name} ({date_str})"

    @property
    def is_completed(self) -> bool:
        """Check if event is completed."""
        return self.status in [EventStatus.FINAL, EventStatus.CANCELLED]

    @property
    def is_live(self) -> bool:
        """Check if event is currently live."""
        return self.status == EventStatus.IN_PROGRESS

    @property
    def display_status(self) -> str:
        """Get display-friendly status."""
        if self.status_detail:
            return self.status_detail
        return self.status.value.replace("_", " ").lower()

    @classmethod
    def from_espn_data(cls, data: dict, league: League) -> "Event":
        """Create Event instance from ESPN API data.

        Args:
            data: Raw event data from ESPN API
            league: League this event belongs to

        Returns:
            Event instance
        """
        # Parse status
        status_data = data.get("status", {})
        type_data = status_data.get("type", {})

        status_map = {
            "pre": EventStatus.SCHEDULED,
            "in": EventStatus.IN_PROGRESS,
            "post": EventStatus.FINAL,
        }
        status = status_map.get(type_data.get("state", "pre"), EventStatus.SCHEDULED)

        # Parse date
        date_str = data.get("date", "")
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            date = datetime.now()

        # Parse season info
        season_data = data.get("season", {})

        # Convert links
        links = []
        if data.get("links"):
            for link_data in data["links"]:
                if isinstance(link_data, dict):
                    links.append(Link(**link_data))

        return cls(
            league=league,
            espn_id=str(data.get("id", "")),
            uid=data.get("uid"),
            date=date,
            name=data.get("name", ""),
            short_name=data.get("shortName"),
            season_year=season_data.get("year", date.year),
            season_type=season_data.get("type", 2),
            season_slug=season_data.get("slug"),
            week=data.get("week", {}).get("number"),
            status=status,
            status_detail=type_data.get("detail"),
            clock=status_data.get("displayClock"),
            period=status_data.get("period"),
            attendance=None,  # Will be set from competition data
            broadcasts=[],    # Will be set from competition data
            links=links,
            raw_data=data,
        )


class Competitor(ESPNModel):
    """Competitor in an event (links team to event with game-specific data)."""

    # Relationships
    event: Event = Field(..., description="Event this competitor is participating in")
    team: Team = Field(..., description="Team competing in this event")

    # Home/away designation
    home_away: str = Field(..., description="'home' or 'away' designation")

    # Score and result
    score: str = Field("", description="Current/final score as string")
    winner: Optional[bool] = Field(None, description="Whether this team won")

    # Game statistics
    line_scores: List[dict] = Field(default_factory=list, description="Period-by-period scores")
    records: List[Record] = Field(default_factory=list, description="Team records")
    statistics: List[Statistic] = Field(default_factory=list, description="Game statistics")
    leaders: List[dict] = Field(default_factory=list, description="Game leaders")

    # Display order
    order: int = Field(0, description="Display order (usually 0 for away, 1 for home)")

    def __str__(self) -> str:
        """String representation."""
        if hasattr(self.event, 'short_name') and hasattr(self.event, 'name'):
            event_name = self.event.short_name or self.event.name
        else:
            event_name = str(self.event)
        return f"{self.team.abbreviation} ({self.home_away}) - {event_name}"

    @property
    def score_int(self) -> Optional[int]:
        """Get score as integer."""
        try:
            return int(self.score) if self.score else None
        except ValueError:
            return None

    @property
    def is_home(self) -> bool:
        """Check if this is the home team."""
        return self.home_away == "home"

    @property
    def is_away(self) -> bool:
        """Check if this is the away team."""
        return self.home_away == "away"

    @classmethod
    def from_espn_data(cls, data: dict, event: Event, league: League) -> "Competitor":
        """Create Competitor instance from ESPN API data.

        Args:
            data: Raw competitor data from ESPN API
            event: Event this competitor is in
            league: League for team lookup

        Returns:
            Competitor instance
        """
        team_data = data.get("team", {})

        # Create team if we don't have it
        team = Team.from_espn_data({"team": team_data}, league)

        # Convert records and statistics
        records = []
        if data.get("records"):
            for record_data in data["records"]:
                if isinstance(record_data, dict):
                    records.append(Record(**record_data))

        statistics = []
        if data.get("statistics"):
            for stat_data in data["statistics"]:
                if isinstance(stat_data, dict):
                    statistics.append(Statistic(**stat_data))

        return cls(
            event=event,
            team=team,
            home_away=data.get("homeAway", "away"),
            score=data.get("score", ""),
            winner=data.get("winner"),
            line_scores=data.get("linescores", []),
            records=records,
            statistics=statistics,
            leaders=data.get("leaders", []),
            order=data.get("order", 0),
            raw_data=data,
        )