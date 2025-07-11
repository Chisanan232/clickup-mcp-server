"""
ClickUp MCP Server - A Model Context Protocol server for ClickUp integration.

This package provides a comprehensive API client and MCP server for interacting
with ClickUp's API, enabling AI assistants to manage tasks, projects, and teams.
"""

from .client import (
    APIResponse,
    ClickUpAPIClient,
    create_clickup_client,
)
from .clickup import ClickUpResourceClient, create_resource_client
from .config import ClickUpConfig, get_default_config, load_config_from_env
from .exceptions import (
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
)
from .utils import (
    ClickUpURLBuilder,
    build_query_params,
    extract_clickup_ids_from_url,
    format_clickup_date,
    format_priority,
    format_status,
    parse_clickup_date,
    sanitize_task_name,
    validate_clickup_id,
)

__version__ = "0.0.0"
__author__ = "Chisanan232"
__email__ = "chi10211201@cycu.org.tw"

__all__ = [
    # Client classes
    "ClickUpAPIClient",
    "ClickUpResourceClient",
    "APIResponse",
    # Factory functions
    "create_clickup_client",
    "create_resource_client",
    # Configuration
    "ClickUpConfig",
    "load_config_from_env",
    "get_default_config",
    # Exceptions
    "ClickUpError",
    "ClickUpAPIError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ValidationError",
    "ConfigurationError",
    "NetworkError",
    "TimeoutError",
    "RetryExhaustedError",
    "MCPError",
    "MCPToolError",
    # Utilities
    "validate_clickup_id",
    "format_clickup_date",
    "parse_clickup_date",
    "build_query_params",
    "sanitize_task_name",
    "extract_clickup_ids_from_url",
    "format_priority",
    "format_status",
    "ClickUpURLBuilder",
]
