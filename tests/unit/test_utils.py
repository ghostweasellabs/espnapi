"""Unit tests for espnapi utils."""

from datetime import datetime

from espnapi import utils


class TestUtils:
    """Test utility helpers."""

    def test_parse_datetime_valid(self):
        """Parse a valid ISO datetime string."""
        dt = utils.parse_datetime("2024-01-01T12:34:56Z")
        assert isinstance(dt, datetime)
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_parse_datetime_invalid(self):
        """Parse invalid datetime returns fallback."""
        dt = utils.parse_datetime("not-a-date")
        assert isinstance(dt, datetime)

    def test_safe_int(self):
        """Safe int conversion."""
        assert utils.safe_int("10") == 10
        assert utils.safe_int("bad", default=5) == 5

    def test_safe_float(self):
        """Safe float conversion."""
        assert utils.safe_float("3.14") == 3.14
        assert utils.safe_float("bad", default=1.5) == 1.5

    def test_safe_str(self):
        """Safe string conversion."""
        assert utils.safe_str(123) == "123"
        assert utils.safe_str(None, default="") == ""

    def test_safe_bool(self):
        """Safe bool conversion."""
        assert utils.safe_bool(True) is True
        assert utils.safe_bool("true") is True
        assert utils.safe_bool("false") is False
        assert utils.safe_bool(0) is False
        assert utils.safe_bool(1) is True

    def test_extract_nested_value(self):
        """Extract nested values safely."""
        data = {"a": {"b": {"c": 1}}}
        assert utils.extract_nested_value(data, ["a", "b", "c"]) == 1
        assert utils.extract_nested_value(data, ["a", "x"], default=0) == 0
