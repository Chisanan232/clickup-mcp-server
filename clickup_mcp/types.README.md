# Type Definitions for ClickUp MCP Server

This module provides comprehensive type definitions for the ClickUp MCP Server package, following PEP 561, PEP 484, PEP 585, and PEP 544 standards.

## Quick Start

```python
from clickup_mcp import types
from typing import Dict

# Use ClickUp-specific types
team_id: types.ClickUpTeamID = "123456789"
task_id: types.ClickUpTaskID = "123456789_abc123"
token: types.ClickUpToken = "pk_1234567890abcdef"

# Use protocol types for type safety
class MyClickUpClient:
    async def get(self, endpoint: str, **kwargs) -> types.ClickUpAPIResponse:
        return {"data": "mock"}

client: types.ClickUpClientProtocol = MyClickUpClient()

# Use type guards for validation
if types.is_clickup_task_id("123456789_abc123"):
    print("Valid task ID")
```

## PEP Standards Compliance

This type system follows these Python Enhancement Proposals:

- **PEP 561**: Distributing and Packaging Type Information
- **PEP 484**: Type Hints
- **PEP 585**: Type Hinting Generics
- **PEP 544**: Protocols (Structural Subtyping)

## Type Categories

### JSON Types

Basic JSON-compatible types for API payloads:

- `JSONPrimitive`: str, int, float, bool, None
- `JSONValue`: Any valid JSON value
- `JSONDict`: JSON object
- `JSONList`: JSON array

### ClickUp Types

ClickUp-specific identifiers and payloads:

- `ClickUpTeamID`: Team identifier (e.g., "123456789")
- `ClickUpSpaceID`: Space identifier (e.g., "123456789")
- `ClickUpFolderID`: Folder identifier (e.g., "123456789")
- `ClickUpListID`: List identifier (e.g., "123456789")
- `ClickUpTaskID`: Task identifier (e.g., "123456789_abc123")
- `ClickUpUserID`: User identifier (e.g., "123456789")
- `ClickUpToken`: API token (e.g., "pk_...")
- `ClickUpWebhookID`: Webhook identifier
- `ClickUpCustomFieldID`: Custom field identifier
- `ClickUpStatus`: Task status (e.g., "to do", "in progress", "done")
- `ClickUpPriority`: Task priority (e.g., "urgent", "high", "normal", "low")
- `ClickUpDueDate`: Due date timestamp (ISO 8601 format)
- `ClickUpAPIResponse`: API response dictionary
- `ClickUpEventPayload`: Event payload dictionary
- `ClickUpTaskPayload`: Task payload structure
- `ClickUpCommentPayload`: Comment payload structure
- `ClickUpAttachmentPayload`: Attachment payload structure
- `ClickUpClient`: ClickUp API client type
- `WebServer`: FastAPI web server type

### Transport Types

MCP transport configuration:

- `TransportType`: Literal["stdio", "sse", "http-streaming"]

### Configuration Types

Server configuration types:

- `ServerHost`: Server host address (e.g., "localhost", "0.0.0.0")
- `ServerPort`: Server port number (e.g., 8000, 9000)
- `LogLevel`: Logging level ("debug", "info", "warning", "error", "critical")
- `EnvironmentFile`: Path to environment file (.env)

### HTTP Client Types

HTTP client configuration:

- `HTTPMethod`: HTTP methods ("GET", "POST", "PUT", "PATCH", "DELETE")
- `HTTPHeaders`: HTTP headers dictionary
- `HTTPQueryParams`: HTTP query parameters dictionary
- `HTTPTimeout`: HTTP request timeout in seconds

### MCP Server Types

MCP server configuration:

- `MCPToolName`: Tool name identifier
- `MCPToolTitle`: Tool display title
- `MCPToolDescription`: Tool description
- `MCPToolData`: Generic tool data structure for arguments, results, input, and output

### Handler Types

Event handler function signatures:

- `EventHandlerFunc`: Sync or async handler
- `AsyncEventHandlerFunc`: Async-only handler
- `SyncEventHandlerFunc`: Sync-only handler

## Protocol Definitions

### ClickUpClientProtocol

Protocol for ClickUp API clients:

```python
from clickup_mcp import types

class MyClickUpClient:
    async def get(self, endpoint: str, **kwargs) -> types.ClickUpAPIResponse:
        return {"data": "mock"}

    async def post(self, endpoint: str, **kwargs) -> types.ClickUpAPIResponse:
        return {"data": "created"}

# Type checking ensures all required methods are implemented
client: types.ClickUpClientProtocol = MyClickUpClient()
```

### EventHandlerDecoratorProtocol

Protocol for event handler decorator factories that create and register event handlers:

```python
from clickup_mcp import types
from clickup_mcp.web_server.event.handler.decorators import ClickUpEventDecorator

# The decorator factory implements EventHandlerDecoratorProtocol
decorator: types.EventHandlerDecoratorProtocol = ClickUpEventDecorator()

# It creates decorators for specific event types
task_decorator = decorator(types.ClickUpWebhookEventType.TASK_CREATED)

# The decorator registers handlers that implement EventHandlerProtocol
@task_decorator
async def handle_task_created(event: types.ClickUpWebhookEvent) -> None:
    print(f"Task created: {event.body.get('task_id')}")

# The handler itself implements EventHandlerProtocol
handler: types.EventHandlerProtocol = handle_task_created
```

**Note**: `EventHandlerDecoratorProtocol` is for decorator factories (producers), while `EventHandlerProtocol` is for the actual event handlers (consumers). They serve different roles in the architecture.

### EventHandlerProtocol

Protocol for ClickUp webhook event handlers that can be called directly with events:

```python
from clickup_mcp import types
from clickup_mcp.web_server.event.handler.decorators import clickup_event
from clickup_mcp.web_server.event.handler.oop import BaseClickUpWebhookHandler

# Decorator style
@clickup_event.task_created
async def handle_task_created(event: types.ClickUpWebhookEvent) -> None:
    print(f"Task created: {event.body.get('task_id')}")

handler: types.EventHandlerProtocol = handle_task_created

# OOP style
class TaskHandler(BaseClickUpWebhookHandler):
    async def on_task_created(self, event: types.ClickUpWebhookEvent) -> None:
        print(f"Task created: {event.body.get('task_id')}")

handler: types.EventHandlerProtocol = TaskHandler()

# Both are callable
await handler(event)
```

### MCPServerProtocol

Protocol for MCP server implementations:

```python
from clickup_mcp import types

class MyMCPServer:
    async def list_tools(self) -> List[Dict[str, Any]]:
        return [{"name": "test_tool", "description": "Test tool"}]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": f"Called {name} with {arguments}"}

server: types.MCPServerProtocol = MyMCPServer()
```

### WebhookEventHandlerProtocol

Protocol for handling normalized ClickUp webhook events:

```python
from clickup_mcp import types

class MyWebhookHandler:
    async def handle_webhook_event(self, event: types.ClickUpWebhookEvent) -> None:
        print(f"Handling webhook: {event.type.value}")

handler: types.WebhookEventHandlerProtocol = MyWebhookHandler()
```

### EventSinkProtocol

Protocol for event sink implementations:

```python
from clickup_mcp import types

class MyEventSink:
    async def handle(self, event: types.ClickUpWebhookEvent) -> None:
        print(f"Processing event: {event.type}")

sink: types.EventSinkProtocol = MyEventSink()
```

### MCPToolProtocol

Protocol for MCP tool implementations:

```python
from clickup_mcp import types

class MyTool:
    async def execute(self, input: types.MCPToolData) -> types.MCPToolData:
        return {"result": "success"}

tool: types.MCPToolProtocol = MyTool()
```

## Type Guards

Type guards provide runtime validation for type checking:

```python
from clickup_mcp import types

def process_task_id(task_id: str) -> None:
    if types.is_clickup_task_id(task_id):
        print(f"Processing task: {task_id}")
    else:
        raise ValueError(f"Invalid task ID: {task_id}")

# Usage
process_task_id("123456789_abc123")  # ✅ Valid
process_task_id("invalid")          # ❌ Raises ValueError
```

Available type guards:

- `is_clickup_team_id()`: Validate team ID format
- `is_clickup_space_id()`: Validate space ID format
- `is_clickup_task_id()`: Validate task ID format
- `is_clickup_user_id()`: Validate user ID format
- `is_clickup_token()`: Validate API token format
- `is_mcp_tool_name()`: Validate MCP tool name format

## Usage Examples

### Event Handler with Type Safety

```python
from clickup_mcp import types
from typing import Dict, Any

class TaskEventHandler:
    async def handle_event(self, event: types.ClickUpEventPayload) -> None:
        """Handle ClickUp task events with type safety."""
        event_type = event.get("event")

        if event_type == "task.created":
            await self.handle_task_created(event)
        elif event_type == "task.updated":
            await self.handle_task_updated(event)

    async def handle_task_created(self, event: types.ClickUpEventPayload) -> None:
        task_data: types.ClickUpTaskPayload = event.get("task", {})
        task_id: types.ClickUpTaskID = task_data.get("id")

        if types.is_clickup_task_id(task_id):
            print(f"New task created: {task_id}")
```

### ClickUp Client Implementation

```python
from clickup_mcp import types
from typing import Optional

class ClickUpClient:
    def __init__(self, token: types.ClickUpToken):
        self.token = token

    async def get_task(
        self,
        task_id: types.ClickUpTaskID
    ) -> Optional[types.ClickUpTaskPayload]:
        """Get a task with type-safe parameters."""
        if not types.is_clickup_task_id(task_id):
            raise ValueError(f"Invalid task ID: {task_id}")

        # Implementation here
        return {"id": task_id, "name": "Sample Task"}

    async def create_task(
        self,
        name: str,
        list_id: types.ClickUpListID,
        **kwargs
    ) -> types.ClickUpTaskPayload:
        """Create a task with type-safe parameters."""
        if not types.is_clickup_list_id(list_id):
            raise ValueError(f"Invalid list ID: {list_id}")

        # Implementation here
        return {"id": "new_task_id", "name": name, "list_id": list_id}
```

### Transport Configuration

```python
from clickup_mcp import types
from typing import Dict, Any

def configure_server(
    host: types.ServerHost = "localhost",
    port: types.ServerPort = 8000,
    transport: types.TransportType = "sse",
    log_level: types.LogLevel = "info"
) -> Dict[str, Any]:
    """Configure MCP server with type-safe parameters."""
    return {
        "host": host,
        "port": port,
        "transport": transport,
        "log_level": log_level
    }

# Usage
config = configure_server(
    host="0.0.0.0",
    port=9000,
    transport="http-streaming",
    log_level="debug"
)
```

## Running Type Checks

### MyPy Integration

```bash
# Install development dependencies
uv sync --dev

# Run type checking
uv run mypy clickup_mcp/

# Check specific module
uv run mypy clickup_mcp/types.py

# Show detailed error messages
uv run mypy --show-error-codes clickup_mcp/
```

### IDE Integration

The type definitions work seamlessly with IDEs that support Python type checking:

- **PyCharm**: Automatic type inference and completion
- **VS Code**: Python extension with Pylance/Pyright
- **Vim/Neovim**: coc-python or pyright plugins
- **Emacs**: lsp-mode with python-lsp-server

## Package Distribution

This package includes type information for distribution:

- `py.typed` marker file for PEP 561 compliance
- Type definitions included in wheel distributions
- Conditional imports for TYPE_CHECKING only
- Comprehensive __all__ exports for public API

## Contributing

When adding new type definitions:

1. Follow the existing naming conventions
2. Add comprehensive docstrings with examples
3. Include type guards where appropriate
4. Update __all__ exports
5. Add tests for type guards and protocols
6. Update this documentation

## References

- [PEP 561 - Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 585 - Type Hinting Generics](https://peps.python.org/pep-0585/)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [ClickUp API Documentation](https://clickup.com/api-quick-start)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
