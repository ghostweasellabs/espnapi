"""ESPN API exceptions.

Custom exception classes for ESPN API client errors.
"""


class ESPNServiceError(Exception):
    """Base exception for ESPN service errors."""

    pass


class ESPNClientError(ESPNServiceError):
    """Error communicating with ESPN API."""

    pass


class ESPNRateLimitError(ESPNClientError):
    """ESPN API rate limit exceeded."""

    pass


class ESPNNotFoundError(ESPNClientError):
    """ESPN resource not found."""

    pass


class IngestionError(ESPNServiceError):
    """Error during data ingestion."""

    pass


class ValidationError(ESPNServiceError):
    """Validation error for API requests."""

    pass