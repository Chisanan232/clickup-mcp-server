# ============================================================================
# Type Definitions for ClickUp MCP Server
# ============================================================================
# This module provides comprehensive type definitions for the ClickUp MCP Server
# package, following PEP 561, PEP 484, PEP 585, and PEP 544 standards.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Literal, Protocol, Union, runtime_checkable

# ============================================================================
# JSON Types
# ============================================================================

type JSONPrimitive = Union[str, int, float, bool, None]
"""Primitive JSON-compatible types."""

type JSONValue = Union[JSONPrimitive, "JSONDict", "JSONList"]
"""Any valid JSON value type."""

type JSONDict = Dict[str, JSONValue]
"""JSON object represented as a dictionary."""

type JSONList = List[JSONValue]
"""JSON array represented as a list."""

# ============================================================================
# ClickUp API Types
# ============================================================================

type ClickUpTeamID = str
"""ClickUp team ID (e.g., '123456789')."""

type ClickUpSpaceID = str
"""ClickUp space ID (e.g., '123456789')."""

type ClickUpFolderID = str
"""ClickUp folder ID (e.g., '123456789')."""

type ClickUpListID = str
"""ClickUp list ID (e.g., '123456789')."""

type ClickUpTaskID = str
"""ClickUp task ID (e.g., '123456789_abc123')."""

type ClickUpUserID = str
"""ClickUp user ID (e.g., '123456789')."""

type ClickUpToken = str
"""ClickUp API token (e.g., 'pk_1234567890abcdef...')."""

type ClickUpWebhookID = str
"""ClickUp webhook ID."""

type ClickUpCustomFieldID = str
"""ClickUp custom field ID."""

type ClickUpStatus = str
"""ClickUp task status (e.g., 'to do', 'in progress', 'done')."""

type ClickUpPriority = str
"""ClickUp task priority (e.g., 'urgent', 'high', 'normal', 'low')."""

type ClickUpDueDate = str
"""ClickUp due date timestamp (ISO 8601 format)."""

type ClickUpAPIResponse = Dict[str, Any]
"""ClickUp API response structure."""

type ClickUpEventPayload = Dict[str, Any]
"""ClickUp webhook event payload as received from the Webhooks API."""

type ClickUpTaskPayload = Dict[str, Any]
"""ClickUp task payload structure."""

type ClickUpCommentPayload = Dict[str, Any]
"""ClickUp comment payload structure."""

type ClickUpAttachmentPayload = Dict[str, Any]
"""ClickUp attachment payload structure."""

# ============================================================================
# Transport Types
# ============================================================================

type TransportType = Literal["stdio", "sse", "http-streaming"]
"""MCP transport types supported by the server."""

type MCPTransport = Literal["stdio", "sse", "http-streaming"]
"""Alias for TransportType for backward compatibility."""

# ============================================================================
# Configuration Types
# ============================================================================

type ServerHost = str
"""Server host address (e.g., 'localhost', '0.0.0.0')."""

type ServerPort = int
"""Server port number (e.g., 8000, 9000)."""

type LogLevel = Literal["debug", "info", "warning", "error", "critical"]
"""Logging level for the server."""

type EnvironmentFile = str
"""Path to environment file (.env)."""

# ============================================================================
# HTTP Client Types
# ============================================================================

type HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
"""HTTP methods supported by the client."""

type HTTPHeaders = Dict[str, str]
"""HTTP headers dictionary."""

type HTTPQueryParams = Dict[str, Union[str, int, float, bool, None]]
"""HTTP query parameters dictionary."""

type HTTPTimeout = Union[int, float]
"""HTTP request timeout in seconds."""

# ============================================================================
# MCP Server Types
# ============================================================================

type MCPToolName = str
"""MCP tool name identifier."""

type MCPToolDescription = str
"""MCP tool description."""

type MCPToolArguments = Dict[str, Any]
"""MCP tool arguments schema."""

type MCPToolResult = Dict[str, Any]
"""MCP tool execution result."""

type MCPResourceURI = str
"""MCP resource URI."""

type MCPResourceData = Dict[str, Any]
"""MCP resource data."""

# ============================================================================
# Event Handler Types
# ============================================================================

type SyncEventHandlerFunc = Callable[[ClickUpEventPayload], None]
"""Synchronous event handler function signature."""

type AsyncEventHandlerFunc = Callable[[ClickUpEventPayload], Awaitable[None]]
"""Asynchronous event handler function signature."""

type EventHandlerFunc = Union[SyncEventHandlerFunc, AsyncEventHandlerFunc]
"""Event handler function that can be sync or async."""

# ============================================================================
# Protocol Definitions
# ============================================================================

@runtime_checkable
class ClickUpClientProtocol(Protocol):
    """Protocol for ClickUp API clients.
    
    This protocol defines the interface that all ClickUp clients must implement.
    It follows PEP 544 for structural subtyping.
    
    Example:
        >>> class MyClient:
        ...     async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        ...         return {"data": "mock"}
        >>>
        >>> client: ClickUpClientProtocol = MyClient()
    """
    
    async def get(self, endpoint: str, **kwargs: Any) -> ClickUpAPIResponse:
        """Make a GET request to the ClickUp API."""
        ...
    
    async def post(self, endpoint: str, **kwargs: Any) -> ClickUpAPIResponse:
        """Make a POST request to the ClickUp API."""
        ...
    
    async def put(self, endpoint: str, **kwargs: Any) -> ClickUpAPIResponse:
        """Make a PUT request to the ClickUp API."""
        ...
    
    async def patch(self, endpoint: str, **kwargs: Any) -> ClickUpAPIResponse:
        """Make a PATCH request to the ClickUp API."""
        ...
    
    async def delete(self, endpoint: str, **kwargs: Any) -> ClickUpAPIResponse:
        """Make a DELETE request to the ClickUp API."""
        ...


@runtime_checkable
class EventHandlerProtocol(Protocol):
    """Protocol for objects that can handle ClickUp events.
    
    This protocol defines the interface that all event handlers must implement.
    It follows PEP 544 for structural subtyping.
    
    Example:
        >>> class MyHandler:
        ...     async def handle_event(self, event: Dict[str, Any]) -> None:
        ...         print(f"Handling event: {event['event']}")
        >>>
        >>> handler: EventHandlerProtocol = MyHandler()
    """
    
    async def handle_event(self, event: ClickUpEventPayload) -> None:
        """Handle a ClickUp event.
        
        Args:
            event: The ClickUp event payload
        """
        ...


@runtime_checkable
class MCPServerProtocol(Protocol):
    """Protocol for MCP server implementations.
    
    This protocol defines the interface that all MCP servers must implement.
    It follows PEP 544 for structural subtyping.
    
    Example:
        >>> class MyMCPServer:
        ...     async def list_tools(self) -> List[Dict[str, Any]]:
        ...         return [{"name": "test_tool", "description": "Test tool"}]
        >>>
        >>> server: MCPServerProtocol = MyMCPServer()
    """
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        ...
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        ...


# ============================================================================
# Type Guards
# ============================================================================

def is_clickup_team_id(value: str) -> bool:
    """Type guard to check if a string is a valid ClickUp team ID.
    
    Args:
        value: The string to check
        
    Returns:
        True if the value is a valid ClickUp team ID format
        
    Example:
        >>> is_clickup_team_id("123456789")
        True
        >>> is_clickup_team_id("invalid")
        False
    """
    return value.isdigit() and len(value) >= 3


def is_clickup_space_id(value: str) -> bool:
    """Type guard to check if a string is a valid ClickUp space ID.
    
    Args:
        value: The string to check
        
    Returns:
        True if the value is a valid ClickUp space ID format
        
    Example:
        >>> is_clickup_space_id("123456789")
        True
        >>> is_clickup_space_id("invalid")
        False
    """
    return value.isdigit() and len(value) >= 3


def is_clickup_task_id(value: str) -> bool:
    """Type guard to check if a string is a valid ClickUp task ID.
    
    Args:
        value: The string to check
        
    Returns:
        True if the value is a valid ClickUp task ID format
        
    Example:
        >>> is_clickup_task_id("123456789_abc123")
        True
        >>> is_clickup_task_id("invalid")
        False
    """
    return "_" in value and len(value.split("_")) == 2


def is_clickup_user_id(value: str) -> bool:
    """Type guard to check if a string is a valid ClickUp user ID.
    
    Args:
        value: The string to check
        
    Returns:
        True if the value is a valid ClickUp user ID format
        
    Example:
        >>> is_clickup_user_id("123456789")
        True
        >>> is_clickup_user_id("invalid")
        False
    """
    return value.isdigit() and len(value) >= 3


def is_clickup_token(value: str) -> bool:
    """Type guard to check if a string is a valid ClickUp API token.
    
    Args:
        value: The string to check
        
    Returns:
        True if the value is a valid ClickUp token format
        
    Example:
        >>> is_clickup_token("pk_1234567890abcdef")
        True
        >>> is_clickup_token("invalid")
        False
    """
    return value.startswith("pk_") and len(value) > 10


# ============================================================================
# Conditional Imports for Type Checking
# ============================================================================

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.web_server.app import FastAPI
    
    type ClickUpClient = ClickUpAPIClient
    """Type alias for ClickUp API client."""
    
    type WebServer = FastAPI
    """Type alias for FastAPI web server."""
else:
    type ClickUpClient = Any
    type WebServer = Any

# ============================================================================
# Public API Exports
# ============================================================================

__all__ = [
    # JSON Types
    "JSONPrimitive",
    "JSONValue", 
    "JSONDict",
    "JSONList",
    
    # ClickUp API Types
    "ClickUpTeamID",
    "ClickUpSpaceID",
    "ClickUpFolderID",
    "ClickUpListID",
    "ClickUpTaskID",
    "ClickUpUserID",
    "ClickUpToken",
    "ClickUpWebhookID",
    "ClickUpCustomFieldID",
    "ClickUpStatus",
    "ClickUpPriority",
    "ClickUpDueDate",
    "ClickUpAPIResponse",
    "ClickUpEventPayload",
    "ClickUpTaskPayload",
    "ClickUpCommentPayload",
    "ClickUpAttachmentPayload",
    
    # Transport Types
    "TransportType",
    "MCPTransport",
    
    # Configuration Types
    "ServerHost",
    "ServerPort",
    "LogLevel",
    "EnvironmentFile",
    
    # HTTP Client Types
    "HTTPMethod",
    "HTTPHeaders",
    "HTTPQueryParams",
    "HTTPTimeout",
    
    # MCP Server Types
    "MCPToolName",
    "MCPToolDescription",
    "MCPToolArguments",
    "MCPToolResult",
    "MCPResourceURI",
    "MCPResourceData",
    
    # Event Handler Types
    "SyncEventHandlerFunc",
    "AsyncEventHandlerFunc",
    "EventHandlerFunc",
    
    # Protocol Definitions
    "ClickUpClientProtocol",
    "EventHandlerProtocol",
    "MCPServerProtocol",
    
    # Type Guards
    "is_clickup_team_id",
    "is_clickup_space_id",
    "is_clickup_task_id",
    "is_clickup_user_id",
    "is_clickup_token",
    
    # Conditional Types
    "ClickUpClient",
    "WebServer",
]
