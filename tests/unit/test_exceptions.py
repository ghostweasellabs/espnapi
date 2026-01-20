"""Unit tests for espnapi exceptions."""

import pytest

from espnapi.exceptions import (
    ESPNServiceError,
    ESPNClientError,
    ESPNRateLimitError,
    ESPNNotFoundError,
    IngestionError,
    ValidationError,
)


class TestExceptions:
    """Test exception classes."""

    def test_base_exception(self):
        """Test base ESPN service exception."""
        exc = ESPNServiceError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_client_error(self):
        """Test ESPN client error."""
        exc = ESPNClientError("API error")
        assert str(exc) == "API error"
        assert isinstance(exc, ESPNServiceError)

    def test_rate_limit_error(self):
        """Test rate limit error."""
        exc = ESPNRateLimitError("Too many requests")
        assert str(exc) == "Too many requests"
        assert isinstance(exc, ESPNClientError)
        assert isinstance(exc, ESPNServiceError)

    def test_not_found_error(self):
        """Test not found error."""
        exc = ESPNNotFoundError("Resource not found")
        assert str(exc) == "Resource not found"
        assert isinstance(exc, ESPNClientError)
        assert isinstance(exc, ESPNServiceError)

    def test_ingestion_error(self):
        """Test ingestion error."""
        exc = IngestionError("Ingestion failed")
        assert str(exc) == "Ingestion failed"
        assert isinstance(exc, ESPNServiceError)

    def test_validation_error(self):
        """Test validation error."""
        exc = ValidationError("Invalid data")
        assert str(exc) == "Invalid data"
        assert isinstance(exc, ESPNServiceError)

    def test_exception_hierarchy(self):
        """Test exception inheritance hierarchy."""
        # Test that client errors inherit from service error
        assert issubclass(ESPNClientError, ESPNServiceError)
        assert issubclass(ESPNRateLimitError, ESPNClientError)
        assert issubclass(ESPNNotFoundError, ESPNClientError)

        # Test that specific errors inherit from client error
        assert issubclass(ESPNRateLimitError, ESPNClientError)
        assert issubclass(ESPNNotFoundError, ESPNClientError)

    def test_exception_creation(self):
        """Test exception creation and message handling."""
        messages = [
            "Simple message",
            "Message with details: 123",
            "Complex error: {'key': 'value'}",
        ]

        for msg in messages:
            exc = ESPNClientError(msg)
            assert str(exc) == msg

    def test_exception_with_cause(self):
        """Test exceptions with underlying causes."""
        original_error = ValueError("Original error")
        client_error = ESPNClientError("Client error")

        # Test that we can raise with cause
        with pytest.raises(ESPNClientError):
            raise client_error from original_error

        # Verify the cause is preserved
        try:
            raise client_error from original_error
        except ESPNClientError as e:
            assert e.__cause__ == original_error

    def test_error_messages(self):
        """Test specific error message formats."""
        errors = [
            (ESPNRateLimitError, "Rate limit exceeded"),
            (ESPNNotFoundError, "Resource not found"),
            (ESPNClientError, "Client communication error"),
            (IngestionError, "Data ingestion failed"),
            (ValidationError, "Data validation failed"),
        ]

        for error_class, message in errors:
            exc = error_class(message)
            assert str(exc) == message
            assert isinstance(exc, error_class)

    def test_custom_error_codes(self):
        """Test that exceptions can be used with custom error codes."""
        # While we don't have error codes in the current implementation,
        # this tests that exceptions can be extended for future use

        class CustomESPNError(ESPNClientError):
            def __init__(self, message: str, error_code: str = "custom"):
                super().__init__(message)
                self.error_code = error_code

        custom_error = CustomESPNError("Custom error", "ERR_001")
        assert str(custom_error) == "Custom error"
        assert custom_error.error_code == "ERR_001"
        assert isinstance(custom_error, ESPNClientError)