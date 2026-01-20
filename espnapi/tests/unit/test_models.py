"""Unit tests for espnapi models."""

import pytest
from datetime import datetime

from espnapi.models.base import ESPNModel, Link, Logo, Record, Statistic, Address
from espnapi.models.sport import Sport, League, SPORTS, LEAGUES
from espnapi.models.team import Team
from espnapi.models.event import Event, Competitor, EventStatus
from espnapi.models.venue import Venue
from espnapi.models.athlete import Athlete


class TestESPNModel:
    """Test base ESPN model functionality."""

    def test_basic_model_creation(self):
        """Test basic model creation and validation."""
        model = ESPNModel(test_field="test_value")
        assert model.test_field == "test_value"
        assert model.model_dump() == {"test_field": "test_value"}

    def test_model_with_raw_data(self):
        """Test model with raw data preservation."""
        raw_data = {"api_field": "value", "extra": "data"}
        model = ESPNModel(raw_data=raw_data)
        assert model.raw_data == raw_data

    def test_from_dict_classmethod(self):
        """Test from_dict class method."""
        data = {"name": "Test", "value": 42}
        model = ESPNModel.from_dict(data)
        assert model.name == "Test"
        assert model.value == 42

    def test_to_dict_method(self):
        """Test to_dict method."""
        model = ESPNModel(name="Test", value=42, none_field=None)
        data = model.to_dict(exclude_none=False)
        assert "name" in data and "value" in data and "none_field" in data
        assert data["name"] == "Test"
        assert data["value"] == 42
        assert data["none_field"] is None

        data_no_none = model.to_dict(exclude_none=True)
        assert data_no_none == {"name": "Test", "value": 42}


class TestBaseModels:
    """Test base model components."""

    def test_link_model(self):
        """Test Link model."""
        link = Link(
            rel=["clubhouse"],
            href="https://example.com",
            text="Team Site"
        )
        assert link.rel == ["clubhouse"]
        assert link.href == "https://example.com"
        assert link.text == "Team Site"

    def test_logo_model(self):
        """Test Logo model."""
        logo = Logo(
            href="https://example.com/logo.png",
            width=100,
            height=100,
            alt="Team Logo"
        )
        assert logo.href == "https://example.com/logo.png"
        assert logo.width == 100
        assert logo.height == 100
        assert logo.alt == "Team Logo"

    def test_address_model(self):
        """Test Address model."""
        address = Address(
            city="Boston",
            state="MA",
            country="USA",
            zip_code="02101"
        )
        assert address.city == "Boston"
        assert address.state == "MA"
        assert address.country == "USA"
        assert address.zip_code == "02101"

    def test_record_model(self):
        """Test Record model."""
        record = Record(
            type="overall",
            summary="10-5",
            display_value="10-5",
            value=0.667,
            rank=3
        )
        assert record.type == "overall"
        assert record.summary == "10-5"
        assert record.value == 0.667
        assert record.rank == 3

    def test_statistic_model(self):
        """Test Statistic model."""
        stat = Statistic(
            name="points",
            display_name="Points",
            abbreviation="PTS",
            value=25.5,
            display_value="25.5",
            rank=1
        )
        assert stat.name == "points"
        assert stat.display_name == "Points"
        assert stat.abbreviation == "PTS"
        assert stat.value == 25.5
        assert stat.rank == 1


class TestSportModels:
    """Test Sport and League models."""

    def test_sport_creation(self):
        """Test Sport model creation."""
        sport = Sport(slug="basketball", name="Basketball")
        assert sport.slug == "basketball"
        assert sport.name == "Basketball"
        assert str(sport) == "Basketball"

    def test_league_creation(self):
        """Test League model creation."""
        sport = Sport(slug="basketball", name="Basketball")
        league = League(
            sport=sport,
            slug="nba",
            name="NBA",
            abbreviation="NBA"
        )
        assert league.sport == sport
        assert league.slug == "nba"
        assert league.name == "NBA"
        assert league.abbreviation == "NBA"
        assert league.sport_slug == "basketball"
        assert str(league) == "NBA (Basketball)"

    def test_predefined_sports(self):
        """Test predefined sports."""
        assert "basketball" in SPORTS
        assert SPORTS["basketball"].name == "Basketball"
        assert SPORTS["football"].name == "Football"

    def test_predefined_leagues(self):
        """Test predefined leagues."""
        assert "nba" in LEAGUES
        nba = LEAGUES["nba"]
        assert nba.name == "NBA"
        assert nba.abbreviation == "NBA"
        assert nba.sport.slug == "basketball"


class TestTeamModel:
    """Test Team model."""

    def test_team_creation(self):
        """Test Team model creation."""
        league = LEAGUES["nba"]
        team = Team(
            league=league,
            espn_id="1",
            abbreviation="LAL",
            display_name="Los Angeles Lakers",
            name="Lakers",
            location="Los Angeles",
            color="552583",
            is_active=True
        )
        assert team.league == league
        assert team.espn_id == "1"
        assert team.abbreviation == "LAL"
        assert team.display_name == "Los Angeles Lakers"
        assert team.name == "Lakers"
        assert team.location == "Los Angeles"
        assert team.color == "552583"
        assert team.is_active is True
        assert str(team) == "Los Angeles Lakers (NBA)"

    def test_team_primary_logo(self):
        """Test primary logo property."""
        league = LEAGUES["nba"]
        logos = [
            Logo(href="https://example.com/logo1.png", rel=["alt"]),
            Logo(href="https://example.com/logo2.png", rel=["default"]),
        ]
        team = Team(
            league=league,
            espn_id="1",
            abbreviation="LAL",
            display_name="Los Angeles Lakers",
            logos=logos
        )

        assert team.primary_logo == "https://example.com/logo2.png"

    def test_team_primary_logo_fallback(self):
        """Test primary logo fallback."""
        league = LEAGUES["nba"]
        logos = [Logo(href="https://example.com/logo1.png", rel=["alt"])]
        team = Team(
            league=league,
            espn_id="1",
            abbreviation="LAL",
            display_name="Los Angeles Lakers",
            logos=logos
        )

        assert team.primary_logo == "https://example.com/logo1.png"

    def test_team_no_logo(self):
        """Test team with no logos."""
        league = LEAGUES["nba"]
        team = Team(
            league=league,
            espn_id="1",
            abbreviation="LAL",
            display_name="Los Angeles Lakers"
        )

        assert team.primary_logo is None

    def test_team_name_properties(self):
        """Test team name properties."""
        league = LEAGUES["nba"]
        team = Team(
            league=league,
            espn_id="1",
            abbreviation="LAL",
            display_name="Los Angeles Lakers",
            short_display_name="Lakers",
            name="Lakers"
        )

        assert team.team_name == "Lakers"
        assert team.full_name == "Los Angeles Lakers"

    def test_from_espn_data(self):
        """Test creating Team from ESPN data."""
        league = LEAGUES["nba"]
        espn_data = {
            "id": "1",
            "abbreviation": "LAL",
            "displayName": "Los Angeles Lakers",
            "name": "Lakers",
            "location": "Los Angeles",
            "color": "552583",
            "logos": [{"href": "https://example.com/logo.png", "rel": ["default"]}],
            "links": [{"rel": ["clubhouse"], "href": "https://example.com"}]
        }

        team = Team.from_espn_data(espn_data, league)

        assert team.espn_id == "1"
        assert team.abbreviation == "LAL"
        assert team.display_name == "Los Angeles Lakers"
        assert team.logos[0].href == "https://example.com/logo.png"
        assert team.links[0].href == "https://example.com"


class TestVenueModel:
    """Test Venue model."""

    def test_venue_creation(self):
        """Test Venue model creation."""
        venue = Venue(
            espn_id="1",
            name="TD Garden",
            city="Boston",
            state="MA",
            country="USA",
            is_indoor=True,
            capacity=19580
        )

        assert venue.espn_id == "1"
        assert venue.name == "TD Garden"
        assert venue.city == "Boston"
        assert venue.state == "MA"
        assert venue.country == "USA"
        assert venue.is_indoor is True
        assert venue.capacity == 19580
        assert str(venue) == "TD Garden (Boston, MA)"

    def test_venue_location_properties(self):
        """Test venue location properties."""
        venue = Venue(
            espn_id="1",
            name="TD Garden",
            city="Boston",
            state="MA",
            country="USA"
        )

        assert venue.location == "Boston, MA, USA"
        assert venue.full_address == "Boston, MA, USA"

    def test_venue_with_address(self):
        """Test venue with detailed address."""
        address = Address(city="Boston", state="MA", zip_code="02114")
        venue = Venue(
            espn_id="1",
            name="TD Garden",
            address=address
        )

        assert venue.full_address == "Boston, MA, 02114"

    def test_from_espn_data(self):
        """Test creating Venue from ESPN data."""
        espn_data = {
            "id": "1",
            "fullName": "TD Garden",
            "address": {
                "city": "Boston",
                "state": "MA",
                "country": "USA"
            },
            "indoor": True,
            "capacity": 19580
        }

        venue = Venue.from_espn_data(espn_data)

        assert venue.espn_id == "1"
        assert venue.name == "TD Garden"
        assert venue.city == "Boston"
        assert venue.state == "MA"
        assert venue.capacity == 19580


class TestAthleteModel:
    """Test Athlete model."""

    def test_athlete_creation(self):
        """Test Athlete model creation."""
        team = Team.from_espn_data({
            "id": "1",
            "abbreviation": "LAL",
            "displayName": "Los Angeles Lakers"
        }, LEAGUES["nba"])

        athlete = Athlete(
            espn_id="1",
            first_name="LeBron",
            last_name="James",
            full_name="LeBron James",
            display_name="LeBron James",
            position="Forward",
            jersey="23",
            team=team
        )

        assert athlete.espn_id == "1"
        assert athlete.first_name == "LeBron"
        assert athlete.last_name == "James"
        assert athlete.full_name == "LeBron James"
        assert athlete.position == "Forward"
        assert athlete.jersey == "23"
        assert athlete.team == team
        assert str(athlete) == "LeBron James (LAL)"

    def test_athlete_properties(self):
        """Test athlete property methods."""
        athlete = Athlete(
            espn_id="1",
            first_name="LeBron",
            last_name="James",
            full_name="LeBron James",
            display_name="LeBron James",
            position_abbreviation="SF"
        )

        assert athlete.name == "LeBron James"
        assert athlete.position_display == "SF"
        assert athlete.team_name is None  # No team

    def test_from_espn_data(self):
        """Test creating Athlete from ESPN data."""
        espn_data = {
            "id": "1",
            "firstName": "LeBron",
            "lastName": "James",
            "fullName": "LeBron James",
            "displayName": "LeBron James",
            "position": {"name": "Forward", "abbreviation": "SF"},
            "jersey": "23",
            "active": True,
            "height": "6'8\"",
            "weight": 250,
            "links": [{"rel": ["stats"], "href": "https://example.com"}]
        }

        athlete = Athlete.from_espn_data(espn_data)

        assert athlete.espn_id == "1"
        assert athlete.first_name == "LeBron"
        assert athlete.last_name == "James"
        assert athlete.position == "Forward"
        assert athlete.position_abbreviation == "SF"
        assert athlete.jersey == "23"
        assert athlete.height == "6'8\""
        assert athlete.weight == 250
        assert athlete.links[0].href == "https://example.com"


class TestEventModel:
    """Test Event and Competitor models."""

    def test_event_creation(self):
        """Test Event model creation."""
        league = LEAGUES["nba"]
        event_date = datetime(2024, 12, 15, 20, 0)

        event = Event(
            league=league,
            espn_id="1",
            date=event_date,
            name="Lakers vs Celtics",
            short_name="LAL @ BOS",
            status=EventStatus.SCHEDULED,
            season_year=2024,
            season_type=2
        )

        assert event.league == league
        assert event.espn_id == "1"
        assert event.date == event_date
        assert event.name == "Lakers vs Celtics"
        assert event.status == EventStatus.SCHEDULED
        assert event.season_year == 2024
        assert event.is_completed is False
        assert event.is_live is False
        assert str(event) == "LAL @ BOS (2024-12-15)"

    def test_event_status_properties(self):
        """Test event status properties."""
        league = LEAGUES["nba"]
        event = Event(
            league=league,
            espn_id="1",
            date=datetime.now(),
            name="Test Event",
            status=EventStatus.FINAL,
            season_year=2024
        )

        assert event.is_completed is True
        assert event.display_status == EventStatus.FINAL.value

        # Test live event
        event.status = EventStatus.IN_PROGRESS
        assert event.is_live is True

    def test_competitor_creation(self):
        """Test Competitor model creation."""
        league = LEAGUES["nba"]
        team = Team.from_espn_data({
            "id": "1",
            "abbreviation": "LAL",
            "displayName": "Los Angeles Lakers"
        }, league)

        event = Event(
            league=league,
            espn_id="1",
            date=datetime.now(),
            name="Test Event",
            season_year=2024
        )

        competitor = Competitor(
            event=event,
            team=team,
            home_away="home",
            score="100",
            winner=True
        )

        assert competitor.event == event
        assert competitor.team == team
        assert competitor.home_away == "home"
        assert competitor.score == "100"
        assert competitor.winner is True
        assert competitor.score_int == 100
        assert competitor.is_home is True
        assert competitor.is_away is False
        assert str(competitor) == "LAL (home) - Test Event"