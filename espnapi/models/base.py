"""Base Pydantic models for espnapi."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ESPNModel(BaseModel):
    """Base model for all ESPN data models.

    Provides common configuration and utility methods.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="allow",  # Allow extra fields for extensibility
    )

    # Store raw data for debugging/extensibility
    raw_data: Optional[Dict[str, Any]] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        """Called after model initialization."""
        # Store raw data if not already set
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            if self.raw_data is None:
                self.raw_data = dict(self.__pydantic_extra__)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ESPNModel":
        """Create model instance from dictionary.

        Args:
            data: Dictionary containing model data

        Returns:
            Model instance
        """
        return cls(**data)

    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary.

        Args:
            exclude_none: Whether to exclude None values

        Returns:
            Dictionary representation
        """
        data = self.model_dump(exclude_none=exclude_none)
        return data

    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}({self.model_dump(exclude_none=True)})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


class Link(ESPNModel):
    """Link model for ESPN API links."""

    rel: List[str] = Field(default_factory=list)
    href: str
    text: Optional[str] = None


class Logo(ESPNModel):
    """Logo model for team/organization logos."""

    href: str
    width: Optional[int] = None
    height: Optional[int] = None
    alt: Optional[str] = None
    rel: List[str] = Field(default_factory=list)
    last_updated: Optional[datetime] = None


class Address(ESPNModel):
    """Address model for venue/location addresses."""

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None


class Record(ESPNModel):
    """Record model for team/athlete records."""

    type: str
    summary: Optional[str] = None
    display_value: Optional[str] = None
    value: Optional[float] = None
    rank: Optional[int] = None


class Statistic(ESPNModel):
    """Statistic model for game/season stats."""

    name: str
    display_name: Optional[str] = None
    short_display_name: Optional[str] = None
    description: Optional[str] = None
    abbreviation: Optional[str] = None
    value: Optional[float] = None
    display_value: Optional[str] = None
    rank: Optional[int] = None