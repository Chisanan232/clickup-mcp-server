"""
ClickUp MCP Server - A Model Context Protocol server for ClickUp integration.

This package provides a comprehensive API client and MCP server for interacting
with ClickUp's API, enabling AI assistants to manage tasks, projects, and teams.
"""

# Import types module for PEP 561 compliance
from . import types
from .api.space import SpaceAPI
from .client import (
    APIResponse,
    ClickUpAPIClient,
    ClickUpAPIClientFactory,
)
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
)
from .models.domain.space import ClickUpSpace, Space

__version__ = "0.0.0"
__author__ = "Chisanan232"
__email__ = "chi10211201@cycu.org.tw"

__all__ = [
    # Client classes
    "ClickUpAPIClient",
    "APIResponse",
    # Factory functions
    "ClickUpAPIClientFactory",
    # Exceptions
    "ClickUpError",
    "ClickUpAPIError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ConfigurationError",
    "NetworkError",
    "TimeoutError",
    "RetryExhaustedError",
    "MCPError",
    "MCPToolError",
    # DTO Models
    # Domain Models (new preferred approach)
    "ClickUpSpace",
    "Space",
    # API Resource Managers
    "SpaceAPI",
    # Type definitions (PEP 561 compliance)
    "types",
]
