"""Venue model for espnapi."""

from typing import Optional

from pydantic import Field

from espnapi.models.base import ESPNModel, Address


class Venue(ESPNModel):
    """Venue/stadium entity representing a sports venue."""

    espn_id: str = Field(..., description="ESPN's unique venue identifier")
    name: str = Field(..., description="Venue name")
    city: Optional[str] = Field(None, description="City location")
    state: Optional[str] = Field(None, description="State/province")
    country: str = Field("USA", description="Country code")

    # Venue characteristics
    is_indoor: bool = Field(True, description="Whether venue is indoor")
    capacity: Optional[int] = Field(None, description="Seating capacity")

    # Full address information
    address: Optional[Address] = Field(None, description="Complete address information")

    def __str__(self) -> str:
        """String representation."""
        location_parts = [self.city, self.state]
        location = ", ".join(filter(None, location_parts))
        return f"{self.name} ({location})" if location else self.name

    @property
    def location(self) -> str:
        """Get formatted location string."""
        parts = [self.city, self.state, self.country]
        return ", ".join(filter(None, parts))

    @property
    def full_address(self) -> str:
        """Get complete address if available."""
        if self.address:
            parts = [
                self.address.city,
                self.address.state,
                self.address.zip_code,
                self.address.country,
            ]
            return ", ".join(filter(None, parts))
        return self.location

    @classmethod
    def from_espn_data(cls, data: dict) -> "Venue":
        """Create Venue instance from ESPN API data.

        Args:
            data: Raw venue data from ESPN API

        Returns:
            Venue instance
        """
        address_data = data.get("address", {})

        return cls(
            espn_id=str(data.get("id", "")),
            name=data.get("fullName", data.get("shortName", "")),
            city=address_data.get("city"),
            state=address_data.get("state"),
            country=address_data.get("country", "USA"),
            is_indoor=data.get("indoor", True),
            capacity=data.get("capacity"),
            address=Address(**address_data) if address_data else None,
            raw_data=data,
        )