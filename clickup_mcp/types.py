# ============================================================================
# Type Definitions for ClickUp MCP Server
# ============================================================================
# This module provides comprehensive type definitions for the ClickUp MCP Server
# package, following PEP 561, PEP 484, PEP 585, and PEP 544 standards.
# 
# Design Principles:
# - Align with ClickUp MCP server's event-driven architecture
# - Support webhook event processing and MCP tool definitions
# - Enable type-safe domain model interactions
# - Provide protocol abstractions for extensible components

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

# ============================================================================
# Webhook Event Types - Core to ClickUp MCP Architecture
# ============================================================================

# Consolidated webhook infrastructure types
type ClickUpWebhookHeaders = Dict[str, str]
"""ClickUp webhook request headers."""

type ClickUpWebhookBody = Dict[str, Any]
"""ClickUp webhook raw request body."""

# Event payload types based on ClickUp webhook structure
type ClickUpTaskEventPayload = Dict[str, Any]
"""ClickUp task event payload (taskCreated, taskUpdated, etc.)."""

type ClickUpListEventPayload = Dict[str, Any]
"""ClickUp list event payload (listCreated, listUpdated, etc.)."""

type ClickUpFolderEventPayload = Dict[str, Any]
"""ClickUp folder event payload (folderCreated, folderUpdated, etc.)."""

type ClickUpSpaceEventPayload = Dict[str, Any]
"""ClickUp space event payload (spaceCreated, spaceUpdated, etc.)."""

type ClickUpGoalEventPayload = Dict[str, Any]
"""ClickUp goal event payload (goalCreated, goalUpdated, etc.)."""

type ClickUpCommentEventPayload = Dict[str, Any]
"""ClickUp comment event payload."""

type ClickUpAttachmentEventPayload = Dict[str, Any]
"""ClickUp attachment event payload."""

# Unified event payload type
type ClickUpEventPayload = Union[
    ClickUpTaskEventPayload,
    ClickUpListEventPayload,
    ClickUpFolderEventPayload,
    ClickUpSpaceEventPayload,
    ClickUpGoalEventPayload,
    ClickUpCommentEventPayload,
    ClickUpAttachmentEventPayload,
]

# ============================================================================
# MCP Tool Types - Core to ClickUp MCP Architecture
# ============================================================================

type MCPToolName = str
"""MCP tool name identifier (e.g., 'task.create', 'space.list')."""

type MCPToolTitle = str
"""MCP tool display title."""

type MCPToolDescription = str
"""MCP tool description."""

# Consolidated MCP tool data types (all use Dict[str, Any])
type MCPToolData = Dict[str, Any]
"""Generic MCP tool data structure for arguments, results, input, and output."""

# MCP Tool Categories
type MCPTaskTool = Literal[
    "task.create", "task.get", "task.update", "task.delete",
    "task.list_in_list", "task.set_custom_field", "task.clear_custom_field",
    "task.add_dependency"
]
"""MCP task-related tool names."""

type MCPSpaceTool = Literal[
    "space.create", "space.get", "space.update", "space.delete", "space.list"
]
"""MCP space-related tool names."""

type MCPListTool = Literal[
    "list.create", "list.get", "list.update", "list.delete",
    "list.list_in_folder", "list.list_folderless"
]
"""MCP list-related tool names."""

type MCPFolderTool = Literal[
    "folder.create", "folder.get", "folder.update", "folder.delete", "folder.list"
]
"""MCP folder-related tool names."""

type MCPWorkspaceTool = Literal[
    "workspace.list", "workspace.get"
]
"""MCP workspace-related tool names."""

# ============================================================================
# Transport Types
# ============================================================================

type TransportType = Literal["stdio", "sse", "http-streaming"]
"""MCP transport types supported by the server."""

# ============================================================================
# Event Processing Types - ClickUp MCP Specific
# ============================================================================

type EventSinkType = Literal["local", "queue"]
"""Event sink backend types."""

type QueueBackend = Literal["kafka", "rabbitmq", "redis", "sqs"]
"""Message queue backend types."""

type EventDeliveryStatus = Literal["pending", "delivered", "failed", "retry"]
"""Event delivery status."""

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
# Event Handler Types - Enhanced for ClickUp MCP
# ============================================================================

type SyncEventHandlerFunc = Callable[[ClickUpEventPayload], None]
"""Synchronous event handler function signature."""

type AsyncEventHandlerFunc = Callable[[ClickUpEventPayload], Awaitable[None]]
"""Asynchronous event handler function signature."""

type EventHandlerFunc = Union[SyncEventHandlerFunc, AsyncEventHandlerFunc]
"""Event handler function that can be sync or async."""

type WebhookEventHandlerFunc = Callable[["ClickUpWebhookEvent"], Awaitable[None]]
"""Webhook event handler function signature for normalized events."""

# ============================================================================
# Protocol Definitions - Aligned with ClickUp MCP Architecture
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
class WebhookEventHandlerProtocol(Protocol):
    """Protocol for handling normalized ClickUp webhook events.
    
    This protocol is designed for the ClickUp MCP server's webhook processing
    architecture, where events are normalized into ClickUpWebhookEvent objects.
    
    Example:
        >>> class MyWebhookHandler:
        ...     async def handle_webhook_event(self, event: ClickUpWebhookEvent) -> None:
        ...         print(f"Handling webhook: {event.type.value}")
        >>>
        >>> handler: WebhookEventHandlerProtocol = MyWebhookHandler()
    """
    
    async def handle_webhook_event(self, event: "ClickUpWebhookEvent") -> None:
        """Handle a normalized ClickUp webhook event.
        
        Args:
            event: The normalized ClickUp webhook event
        """
        ...


@runtime_checkable
class EventSinkProtocol(Protocol):
    """Protocol for event sink implementations.
    
    This protocol defines the interface for event sinks that can process
    ClickUp webhook events, either locally or via message queues.
    
    Example:
        >>> class MyEventSink:
        ...     async def handle(self, event: ClickUpWebhookEvent) -> None:
        ...         print(f"Processing event: {event.type}")
        >>>
        >>> sink: EventSinkProtocol = MyEventSink()
    """
    
    async def handle(self, event: "ClickUpWebhookEvent") -> None:
        """Process a ClickUp webhook event.
        
        Args:
            event: The ClickUp webhook event to process
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


@runtime_checkable
class MCPToolProtocol(Protocol):
    """Protocol for MCP tool implementations.
    
    This protocol defines the interface for individual MCP tools in the
    ClickUp MCP server architecture.
    
    Example:
        >>> class MyTool:
        ...     async def execute(self, input: Dict[str, Any]) -> Dict[str, Any]:
        ...         return {"result": "success"}
        >>>
        >>> tool: MCPToolProtocol = MyTool()
    """
    
    async def execute(self, input: MCPToolData) -> MCPToolData:
        """Execute the MCP tool.
        
        Args:
            input: Tool input parameters
            
        Returns:
            Tool execution result
        """
        ...

# ============================================================================
# Data Transfer Object (DTO) Types - ClickUp MCP Specific
# ============================================================================

# Base DTO types
type DTOCreate = Dict[str, Any]
"""Base type for creation DTOs."""

type DTOUpdate = Dict[str, Any]
"""Base type for update DTOs."""

type DTOResponse = Dict[str, Any]
"""Base type for response DTOs."""

type DTOQuery = Dict[str, Any]
"""Base type for query DTOs."""

# ============================================================================
# Domain Model Types - ClickUp MCP Specific
# ============================================================================

type DomainEntityID = str
"""Base type for domain entity identifiers."""

type DomainEntity = Dict[str, Any]
"""Base type for domain entities."""

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


def is_mcp_tool_name(value: str) -> bool:
    """Type guard to check if a string is a valid MCP tool name.
    
    Args:
        value: The string to check
        
    Returns:
        True if the value matches MCP tool naming convention
        
    Example:
        >>> is_mcp_tool_name("task.create")
        True
        >>> is_mcp_tool_name("invalid_tool")
        False
    """
    return "." in value and len(value.split(".")) == 2

# ============================================================================
# Conditional Imports for Type Checking
# ============================================================================

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.web_server.app import FastAPI
    from clickup_mcp.web_server.event.models import ClickUpWebhookEvent
    
    type ClickUpClient = ClickUpAPIClient
    """Type alias for ClickUp API client."""
    
    type WebServer = FastAPI
    """Type alias for FastAPI web server."""
    
    # Forward references for protocol types
    type ClickUpWebhookEvent = ClickUpWebhookEvent
    """Type alias for normalized ClickUp webhook event."""
else:
    type ClickUpClient = Any
    type WebServer = Any
    type ClickUpWebhookEvent = Any

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
    
    # Webhook Event Types
    "ClickUpWebhookHeaders",
    "ClickUpWebhookBody",
    "ClickUpTaskEventPayload",
    "ClickUpListEventPayload",
    "ClickUpFolderEventPayload",
    "ClickUpSpaceEventPayload",
    "ClickUpGoalEventPayload",
    "ClickUpCommentEventPayload",
    "ClickUpAttachmentEventPayload",
    "ClickUpEventPayload",
    
    # MCP Tool Types
    "MCPToolName",
    "MCPToolTitle",
    "MCPToolDescription",
    "MCPToolData",
    "MCPTaskTool",
    "MCPSpaceTool",
    "MCPListTool",
    "MCPFolderTool",
    "MCPWorkspaceTool",
    
    # Transport Types
    "TransportType",
    
    # Event Processing Types
    "EventSinkType",
    "QueueBackend",
    "EventDeliveryStatus",
    
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
    
    # Event Handler Types
    "SyncEventHandlerFunc",
    "AsyncEventHandlerFunc",
    "EventHandlerFunc",
    "WebhookEventHandlerFunc",
    
    # DTO Types
    "DTOCreate",
    "DTOUpdate",
    "DTOResponse",
    "DTOQuery",
    
    # Domain Model Types
    "DomainEntityID",
    "DomainEntity",
    
    # Protocol Definitions
    "ClickUpClientProtocol",
    "EventHandlerProtocol",
    "WebhookEventHandlerProtocol",
    "EventSinkProtocol",
    "MCPServerProtocol",
    "MCPToolProtocol",
    
    # Type Guards
    "is_clickup_team_id",
    "is_clickup_space_id",
    "is_clickup_task_id",
    "is_clickup_user_id",
    "is_clickup_token",
    "is_mcp_tool_name",
    
    # Conditional Types
    "ClickUpClient",
    "WebServer",
    "ClickUpWebhookEvent",
]
