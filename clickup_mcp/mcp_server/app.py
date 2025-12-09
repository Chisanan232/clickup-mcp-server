"""
MCP server factory and lifecycle integration.

Design:
- Provides a singleton factory for `FastMCP`, the Model Context Protocol server.
- Exposes `lifespan()` for FastAPI integration to pre-initialize transports and
  manage the MCP session manager lifecycle.

Transports:
- SSE app mounted at `/sse` via `FastMCP.sse_app()`
- HTTP streaming app mounted at `/mcp` via `FastMCP.streamable_http_app()`

Usage Examples:
    # Create and retrieve MCP server
    from clickup_mcp.mcp_server.app import MCPServerFactory
    mcp = MCPServerFactory.create()
    same = MCPServerFactory.get()

    # Use with FastAPI lifespan
    from fastapi import FastAPI
    app = FastAPI(lifespan=MCPServerFactory.lifespan())

Notes:
- A default instance is created at import time for backward compatibility
  via `mcp = mcp_factory.create()`.
- Use `reset()` in tests to clear the singleton between test cases.

Architecture (Mermaid):
```mermaid
sequenceDiagram
    autonumber
    participant FA as FastAPI
    participant Factory as MCPServerFactory
    participant MCP as FastMCP

    FA->>Factory: lifespan = MCPServerFactory.lifespan()
    activate Factory
    Factory->>MCP: ensure created (create/get)
    Factory-->>FA: asynccontextmanager
    deactivate Factory

    FA->>MCP: sse_app()  (init SSE transport)
    FA->>MCP: streamable_http_app() (init HTTP streaming)
    MCP->>MCP: session_manager.run()
    Note over MCP: Runs until FastAPI shutdown
```

See also:
- `clickup_mcp.web_server.app.WebServerFactory` – FastAPI app factory that mounts MCP
- `clickup_mcp.web_server.app.mount_service` – helper to mount SSE/HTTP-streaming apps
"""

import contextlib
from collections.abc import Callable

from fastapi import FastAPI
from mcp.server import FastMCP

from clickup_mcp._base import BaseServerFactory

_MCP_SERVER_INSTANCE: FastMCP | None = None


class MCPServerFactory(BaseServerFactory[FastMCP]):
    """
    Singleton factory for the `FastMCP` server instance.

    Responsibilities:
    - `create()`: Create a new `FastMCP` instance (enforces single instance)
    - `get()`: Return the existing instance (asserts if not created)
    - `reset()`: Drop the singleton (primarily for tests)
    - `lifespan()`: FastAPI lifespan context to initialize transports and run
      the session manager.
    """

    @staticmethod
    def create(**kwargs) -> FastMCP:
        """
        Create and configure the MCP server singleton.

        Design:
        - Creates a new `FastMCP` and caches it in a module-level singleton.
        - Enforces single instance creation; subsequent calls should use `get()`.

        Args:
            **kwargs: Unused; present for base class compatibility

        Returns:
            FastMCP: Configured MCP server instance

        Examples:
            from clickup_mcp.mcp_server.app import MCPServerFactory
            mcp = MCPServerFactory.create()
        """
        # Create a new FastMCP instance
        global _MCP_SERVER_INSTANCE
        assert _MCP_SERVER_INSTANCE is None, "It is not allowed to create more than one instance of FastMCP."
        _MCP_SERVER_INSTANCE = FastMCP()
        return _MCP_SERVER_INSTANCE

    @staticmethod
    def get() -> FastMCP:
        """
        Get the MCP server instance.

        Returns:
            FastMCP: Previously created MCP server instance

        Raises:
            AssertionError: If `create()` has not been called yet
        """
        assert _MCP_SERVER_INSTANCE is not None, "It must be created FastMCP first."
        return _MCP_SERVER_INSTANCE

    @staticmethod
    def reset() -> None:
        """
        Reset the singleton instance (primarily for tests).

        Examples:
            MCPServerFactory.reset()
            MCPServerFactory.create()
        """
        global _MCP_SERVER_INSTANCE
        _MCP_SERVER_INSTANCE = None

    @staticmethod
    def lifespan() -> Callable[..., contextlib._AsyncGeneratorContextManager]:
        """
        FastAPI lifespan context manager for MCP server lifecycle.

        Behavior:
        - Ensures a `FastMCP` instance exists.
        - Initializes the SSE and HTTP streaming sub-apps to ensure the session
          manager is properly set up.
        - Runs the `session_manager` for the duration of the FastAPI app lifecycle.

        Returns:
            Callable[..., contextlib._AsyncGeneratorContextManager]: A lifespan context

        Examples:
            from fastapi import FastAPI
            app = FastAPI(lifespan=MCPServerFactory.lifespan())
        """
        try:
            _mcp_server = MCPServerFactory.get()
        except AssertionError:
            raise AssertionError("Please create a FastMCP instance first by calling *MCPServerFactory.create()*.")

        @contextlib.asynccontextmanager
        async def lifespan(_: FastAPI):
            # Initialize transport apps before accessing session_manager
            # This ensures the session manager is properly created
            _mcp_server.sse_app()
            _mcp_server.streamable_http_app()

            # Now we can safely access session_manager
            async with _mcp_server.session_manager.run():
                yield  # FastAPI would start to handle requests after yield

        return lifespan


# Create a default MCP server instance for backward compatibility
mcp_factory = MCPServerFactory
mcp = mcp_factory.create()
