"""Utility functions for espnapi."""

from datetime import datetime
from typing import Any


def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string from ESPN API.

    Args:
        date_str: Date string from ESPN API

    Returns:
        Parsed datetime object
    """
    try:
        # ESPN uses ISO format with 'Z' suffix sometimes
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        # Fallback to current time if parsing fails
        return datetime.now()


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        String value or default
    """
    if value is None:
        return default
    return str(value)


def safe_bool(value: Any, default: bool = False) -> bool:
    """Safely convert value to boolean.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Boolean value or default
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def extract_nested_value(data: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    """Extract nested value from dictionary safely.

    Args:
        data: Dictionary to extract from
        keys: List of keys to traverse
        default: Default value if path doesn't exist

    Returns:
        Extracted value or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current