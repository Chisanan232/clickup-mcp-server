"""
Unit tests for the clickup_mcp.exceptions module.

This module contains comprehensive tests for all custom exception classes
and utility functions in the exceptions module.
"""

import pytest

from clickup_mcp.exceptions import (  # Base exceptions; Specific API exceptions; Utility functions
    AuthenticationError,
    AuthorizationError,
    ClickUpAPIError,
    ClickUpError,
    ConfigurationError,
    MCPError,
    MCPToolError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    RetryExhaustedError,
    TimeoutError,
    ValidationError,
    create_api_error,
    create_network_error,
    create_validation_error,
)


class TestConfigurationError:
    """Test cases for the ConfigurationError exception."""

    def test_basic_creation(self):
        """Test basic ConfigurationError creation."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"
        assert error.config_key is None

    def test_with_config_details(self):
        """Test ConfigurationError with config details."""
        error = ConfigurationError(
            "Invalid API token", config_key="api_token", details={"config_value": "invalid_token"}
        )
        assert error.message == "Invalid API token"
        assert error.config_key == "api_token"
        assert error.details.get("config_value") == "invalid_token"

    def test_inheritance(self):
        """Test that ConfigurationError inherits from ClickUpError."""
        error = ConfigurationError("Test error")
        assert isinstance(error, ClickUpError)
        assert isinstance(error, ConfigurationError)


class TestCreateApiError:
    """Test cases for the create_api_error utility function."""

    def test_create_authentication_error(self):
        """Test creating AuthenticationError for 401 status code."""
        error = create_api_error(401)
        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401
        assert "Invalid API token" in error.message

    def test_create_authorization_error(self):
        """Test creating AuthorizationError for 403 status code."""
        error = create_api_error(403)
        assert isinstance(error, AuthorizationError)
        assert error.status_code == 403
        assert "Insufficient permissions" in error.message

    def test_create_resource_not_found_error(self):
        """Test creating ResourceNotFoundError for 404 status code."""
        error = create_api_error(404)
        assert isinstance(error, ResourceNotFoundError)
        assert error.status_code == 404
        assert "not found" in error.message

    def test_create_rate_limit_error(self):
        """Test creating RateLimitError for 429 status code."""
        error = create_api_error(429)
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429
        assert "rate limit" in error.message

    def test_create_rate_limit_error_with_retry_after(self):
        """Test creating RateLimitError with retry_after in response data."""
        response_data = {"retry_after": 60}
        error = create_api_error(429, response_data=response_data)
        assert isinstance(error, RateLimitError)
        assert error.retry_after == 60

    def test_create_generic_api_error(self):
        """Test creating generic ClickUpAPIError for other status codes."""
        error = create_api_error(500)
        assert isinstance(error, ClickUpAPIError)
        assert not isinstance(error, AuthenticationError)
        assert not isinstance(error, AuthorizationError)
        assert not isinstance(error, ResourceNotFoundError)
        assert not isinstance(error, RateLimitError)
        assert error.status_code == 500

    def test_create_api_error_with_response_data(self):
        """Test creating API error with response data."""
        response_data = {"err": "Custom error message"}
        error = create_api_error(500, response_data=response_data)
        assert error.response_data == response_data
        assert error.message == "Custom error message"

    def test_create_api_error_with_error_field(self):
        """Test creating API error with 'error' field in response data."""
        response_data = {"error": "Another custom error"}
        error = create_api_error(500, response_data=response_data)
        assert error.response_data == response_data
        assert error.message == "Another custom error"

    def test_create_api_error_with_endpoint(self):
        """Test creating API error with endpoint information."""
        endpoint = "/api/v2/task/123"
        error = create_api_error(404, endpoint=endpoint)
        assert error.endpoint == endpoint

    def test_create_api_error_fallback_message(self):
        """Test creating API error with fallback message."""
        error = create_api_error(500)
        assert error.message == "API request failed"

    @pytest.mark.parametrize(
        "status_code,expected_type",
        [
            (401, AuthenticationError),
            (403, AuthorizationError),
            (404, ResourceNotFoundError),
            (429, RateLimitError),
            (400, ClickUpAPIError),
            (500, ClickUpAPIError),
            (502, ClickUpAPIError),
        ],
    )
    def test_create_api_error_status_code_mapping(self, status_code, expected_type):
        """Test that create_api_error returns correct exception types."""
        error = create_api_error(status_code)
        assert isinstance(error, expected_type)
        assert error.status_code == status_code


class TestCreateValidationError:
    """Test cases for the create_validation_error utility function."""

    def test_create_validation_error_basic(self):
        """Test basic validation error creation."""
        error = create_validation_error("priority", "invalid", "must be 1-4")
        assert isinstance(error, ValidationError)
        assert error.field == "priority"
        assert error.value == "invalid"
        assert "Invalid value for field 'priority'" in error.message
        assert "must be 1-4" in error.message

    def test_create_validation_error_with_none_value(self):
        """Test validation error creation with None value."""
        error = create_validation_error("name", None, "is required")
        assert error.field == "name"
        assert error.value is None
        assert "Invalid value for field 'name'" in error.message
        assert "is required" in error.message

    def test_create_validation_error_with_complex_value(self):
        """Test validation error creation with complex value."""
        value = {"nested": "object"}
        error = create_validation_error("data", value, "invalid structure")
        assert error.field == "data"
        assert error.value == value
        assert "invalid structure" in error.message

    @pytest.mark.parametrize(
        "field,value,message",
        [
            ("email", "invalid-email", "must be a valid email address"),
            ("priority", 5, "must be between 1 and 4"),
            ("status", "", "cannot be empty"),
            ("assignee", ["invalid", "ids"], "must be valid user IDs"),
        ],
    )
    def test_create_validation_error_parametrized(self, field, value, message):
        """Test validation error creation with various field types."""
        error = create_validation_error(field, value, message)
        assert error.field == field
        assert error.value == value
        assert field in error.message
        assert message in error.message


class TestCreateNetworkError:
    """Test cases for the create_network_error utility function."""

    def test_create_network_error_basic(self):
        """Test basic network error creation."""
        original_error = ConnectionError("Connection failed")
        error = create_network_error(original_error)
        assert isinstance(error, NetworkError)
        assert error.original_error == original_error
        assert error.message == "Network error occurred"

    def test_create_network_error_with_context(self):
        """Test network error creation with context."""
        original_error = TimeoutError("Request timeout")
        context = "while fetching user data"
        error = create_network_error(original_error, context)
        assert error.original_error == original_error
        assert error.message == f"Network error occurred: {context}"

    def test_create_network_error_with_empty_context(self):
        """Test network error creation with empty context."""
        original_error = OSError("Network unreachable")
        error = create_network_error(original_error, "")
        assert error.original_error == original_error
        assert error.message == "Network error occurred"

    @pytest.mark.parametrize(
        "original_error,context,expected_message",
        [
            (ConnectionError("Failed"), "during API call", "Network error occurred: during API call"),
            (TimeoutError("Timeout"), "fetching tasks", "Network error occurred: fetching tasks"),
            (OSError("No connection"), "", "Network error occurred"),
            (Exception("Generic error"), "unknown operation", "Network error occurred: unknown operation"),
        ],
    )
    def test_create_network_error_parametrized(self, original_error, context, expected_message):
        """Test network error creation with various original errors and contexts."""
        error = create_network_error(original_error, context)
        assert error.original_error == original_error
        assert error.message == expected_message


class TestExceptionIntegration:
    """Integration tests for exception handling scenarios."""

    def test_api_error_chain(self):
        """Test creating a chain of API errors."""
        # Create a network error first
        network_error = NetworkError("Connection failed")

        # Create a retry exhausted error
        retry_error = RetryExhaustedError("Failed after 3 attempts", attempts=3, last_error=network_error)

        # Verify the chain
        assert retry_error.last_error == network_error
        assert retry_error.attempts == 3
        assert isinstance(retry_error.last_error, NetworkError)

    def test_validation_error_with_multiple_fields(self):
        """Test validation error with multiple validation errors."""
        validation_errors = [
            {"field": "name", "error": "Required"},
            {"field": "priority", "error": "Invalid value"},
            {"field": "assignee", "error": "User not found"},
        ]

        error = ValidationError("Multiple validation failures", details={"validation_errors": validation_errors})

        assert len(error.details.get("validation_errors", [])) == 3
        assert error.details["validation_errors"][0]["field"] == "name"
        assert error.details["validation_errors"][1]["field"] == "priority"
        assert error.details["validation_errors"][2]["field"] == "assignee"

    def test_mcp_error_with_nested_data(self):
        """Test MCP error with nested error data."""
        nested_data = {
            "type": "tool_error",
            "tool": "create_task",
            "parameters": {"name": "test", "priority": "invalid"},
            "validation_errors": [{"field": "priority", "message": "Invalid priority value"}],
        }

        error = MCPError(
            "Tool execution failed",
            error_code="TOOL_EXECUTION_ERROR",
            tool_name="create_task",
            details={"error_data": nested_data},
        )

        assert error.error_code == "TOOL_EXECUTION_ERROR"
        assert error.tool_name == "create_task"
        assert error.details["error_data"]["type"] == "tool_error"
        assert error.details["error_data"]["tool"] == "create_task"
        assert len(error.details["error_data"]["validation_errors"]) == 1

    def test_error_serialization(self):
        """Test that errors can be properly serialized (useful for logging)."""
        response_data = {"error": "Invalid request", "code": 400}
        error = ClickUpAPIError("Test error", status_code=400, response_data=response_data, endpoint="/api/v2/task")

        # Test that we can access all attributes
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.response_data == response_data
        assert error.endpoint == "/api/v2/task"

        # Test string representation
        error_str = str(error)
        assert "Test error" in error_str


class TestAdditionalUtilityFunctions:
    """Test cases for additional utility functions in the exception module."""

    def test_timeout_error_in_create_network_error(self):
        """Test that TimeoutError works correctly with create_network_error."""
        original_timeout = TimeoutError("Request timed out", timeout_duration=30.0)
        network_error = create_network_error(original_timeout, "while fetching task data")

        assert isinstance(network_error, NetworkError)
        assert network_error.original_error == original_timeout
        assert "while fetching task data" in network_error.message
        assert isinstance(network_error.original_error, TimeoutError)
        assert network_error.original_error.timeout_duration == 30.0

    def test_mcp_tool_error_integration(self):
        """Test MCPToolError integration with other error types."""
        # Test creating MCPToolError with validation error details
        validation_error = ValidationError("Invalid priority", field="priority", value="invalid")

        mcp_tool_error = MCPToolError(
            "Tool validation failed",
            tool_name="create_task",
            parameters={"name": "Test Task", "priority": "invalid"},
            error_code="VALIDATION_ERROR",
            details={"validation_error": validation_error},
        )

        assert isinstance(mcp_tool_error, MCPToolError)
        assert mcp_tool_error.tool_name == "create_task"
        assert mcp_tool_error.error_code == "VALIDATION_ERROR"
        assert mcp_tool_error.details["validation_error"] == validation_error
        assert mcp_tool_error.parameters["priority"] == "invalid"
