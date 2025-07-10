"""
ClickUp MCP Server - A Model Context Protocol server for ClickUp integration.

This package provides a comprehensive API client and MCP server for interacting
with ClickUp's API, enabling AI assistants to manage tasks, projects, and teams.
"""

from .client import (
    ClickUpAPIClient,
    ClickUpResourceClient,
    create_clickup_client,
    create_resource_client,
    APIResponse
)
from .config import ClickUpConfig, load_config_from_env, get_default_config
from .exceptions import (
    ClickUpError,
    ClickUpAPIError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
    ConfigurationError,
    NetworkError,
    TimeoutError,
    RetryExhaustedError,
    MCPError,
    MCPToolError
)
from .utils import (
    validate_clickup_id,
    format_clickup_date,
    parse_clickup_date,
    build_query_params,
    sanitize_task_name,
    extract_clickup_ids_from_url,
    format_priority,
    format_status,
    ClickUpURLBuilder
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
