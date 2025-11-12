"""
Custom exceptions for ClickUp MCP server.

This module defines custom exception classes for better error handling
throughout the ClickUp API client and MCP server.
"""

from typing import Any, Dict, Optional


class ClickUpError(Exception):
    """Base exception class for all ClickUp-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ClickUpAPIError(ClickUpError):
    """Exception raised for ClickUp API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.endpoint = endpoint

    def __str__(self) -> str:
        parts = [self.message]

        if self.status_code:
            parts.append(f"Status: {self.status_code}")

        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")

        if self.response_data:
            parts.append(f"Response: {self.response_data}")

        return " | ".join(parts)


class AuthenticationError(ClickUpAPIError):
    """Exception raised when authentication with ClickUp API fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class AuthorizationError(ClickUpAPIError):
    """Exception raised when authorization fails (insufficient permissions)."""

    def __init__(self, message: str = "Insufficient permissions", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class RateLimitError(ClickUpAPIError):
    """Exception raised when API rate limit is exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: Optional[float] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.retry_after:
            return f"{base_str} | Retry after: {self.retry_after} seconds"
        return base_str


class ResourceNotFoundError(ClickUpAPIError):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id

    def __str__(self) -> str:
        parts = [self.message]

        if self.resource_type and self.resource_id:
            parts.append(f"Resource: {self.resource_type} ({self.resource_id})")
        elif self.resource_type:
            parts.append(f"Resource type: {self.resource_type}")
        elif self.resource_id:
            parts.append(f"Resource ID: {self.resource_id}")

        if self.status_code:
            parts.append(f"Status: {self.status_code}")

        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")

        return " | ".join(parts)


class ValidationError(ClickUpError):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        parts = [self.message]

        if self.field:
            parts.append(f"Field: {self.field}")

        if self.value is not None:
            parts.append(f"Value: {self.value}")

        return " | ".join(parts)


class ConfigurationError(ClickUpError):
    """Exception raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.config_key = config_key

    def __str__(self) -> str:
        if self.config_key:
            return f"{self.message} (Config key: {self.config_key})"
        return self.message


class NetworkError(ClickUpError):
    """Exception raised for network-related errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.original_error = original_error

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (Original error: {self.original_error})"
        return self.message


class TimeoutError(NetworkError):
    """Exception raised when a request times out."""

    def __init__(self, message: str = "Request timed out", timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.timeout_duration:
            return f"{base_str} (Timeout: {self.timeout_duration}s)"
        return base_str


class RetryExhaustedError(ClickUpError):
    """Exception raised when all retry attempts have been exhausted."""

    def __init__(
        self,
        message: str = "All retry attempts exhausted",
        attempts: Optional[int] = None,
        last_error: Optional[Exception] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.attempts = attempts
        self.last_error = last_error

    def __str__(self) -> str:
        parts = [self.message]

        if self.attempts:
            parts.append(f"Attempts: {self.attempts}")

        if self.last_error:
            parts.append(f"Last error: {self.last_error}")

        return " | ".join(parts)


class MCPError(ClickUpError):
    """Exception raised for MCP-specific errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, tool_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.error_code = error_code
        self.tool_name = tool_name

    def __str__(self) -> str:
        parts = [self.message]

        if self.error_code:
            parts.append(f"Code: {self.error_code}")

        if self.tool_name:
            parts.append(f"Tool: {self.tool_name}")

        return " | ".join(parts)


class MCPToolError(MCPError):
    """Exception raised when an MCP tool encounters an error."""

    def __init__(self, message: str, tool_name: str, parameters: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, tool_name=tool_name, **kwargs)
        self.parameters = parameters or {}

    def __str__(self) -> str:
        parts = [self.message, f"Tool: {self.tool_name}"]

        if self.parameters:
            parts.append(f"Parameters: {self.parameters}")

        if self.error_code:
            parts.append(f"Code: {self.error_code}")

        return " | ".join(parts)


# Convenience functions for creating specific errors
def create_api_error(
    status_code: int, response_data: Optional[Dict[str, Any]] = None, endpoint: Optional[str] = None
) -> ClickUpAPIError:
    """Create an appropriate API error based on status code."""

    if status_code == 401:
        return AuthenticationError(
            "Invalid API token or authentication failed",
            status_code=status_code,
            response_data=response_data,
            endpoint=endpoint,
        )
    elif status_code == 403:
        return AuthorizationError(
            "Insufficient permissions for this operation",
            status_code=status_code,
            response_data=response_data,
            endpoint=endpoint,
        )
    elif status_code == 404:
        return ResourceNotFoundError(
            "The requested resource was not found",
            status_code=status_code,
            response_data=response_data,
            endpoint=endpoint,
        )
    elif status_code == 429:
        retry_after = None
        if response_data and "retry_after" in response_data:
            retry_after = response_data["retry_after"]

        return RateLimitError(
            "API rate limit exceeded",
            status_code=status_code,
            response_data=response_data,
            endpoint=endpoint,
            retry_after=retry_after,
        )
    else:
        error_message = "API request failed"
        if response_data and "err" in response_data:
            error_message = response_data["err"]
        elif response_data and "error" in response_data:
            error_message = response_data["error"]

        return ClickUpAPIError(error_message, status_code=status_code, response_data=response_data, endpoint=endpoint)


def create_validation_error(field: str, value: Any, message: str) -> ValidationError:
    """Create a validation error for a specific field."""
    return ValidationError(message=f"Invalid value for field '{field}': {message}", field=field, value=value)


def create_network_error(original_error: Exception, context: str = "") -> NetworkError:
    """Create a network error from an original exception."""
    message = f"Network error occurred{': ' + context if context else ''}"
    return NetworkError(message=message, original_error=original_error)
