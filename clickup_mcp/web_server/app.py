"""
FastAPI Web Server for ClickUp MCP.

This module provides a FastAPI web server that mounts the MCP server
for exposing ClickUp functionality through a RESTful API.
"""

from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from clickup_mcp._base import BaseServerFactory
from clickup_mcp.client import ClickUpAPIClientFactory, get_api_token
from clickup_mcp.mcp_server.app import MCPServerFactory
from clickup_mcp.models.cli import MCPTransportType, ServerConfig
from clickup_mcp.utils import load_environment_from_file

_WEB_SERVER_INSTANCE: Optional[FastAPI] = None


class WebServerFactory(BaseServerFactory[FastAPI]):
    @staticmethod
    def create(**kwargs) -> FastAPI:
        """
        Create and configure the web API server.

        Args:
            **kwargs: Additional arguments (unused, but included for base class compatibility)

        Returns:
            Configured FastAPI server instance
        """
        # Create a new FastAPI instance
        global _WEB_SERVER_INSTANCE
        assert _WEB_SERVER_INSTANCE is None, "It is not allowed to create more than one instance of web server."
        # Create FastAPI app
        _WEB_SERVER_INSTANCE = FastAPI(
            title="ClickUp MCP Server",
            description="A FastAPI web server that hosts a ClickUp MCP server for interacting with ClickUp API",
            version="0.1.0",
        )

        # Configure CORS
        _WEB_SERVER_INSTANCE.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, replace with specific origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return _WEB_SERVER_INSTANCE

    @staticmethod
    def get() -> FastAPI:
        """
        Get the web API server instance

        Returns:
            Configured FastAPI server instance
        """
        assert _WEB_SERVER_INSTANCE is not None, "It must be created web server first."
        return _WEB_SERVER_INSTANCE

    @staticmethod
    def reset() -> None:
        """
        Reset the singleton instance (for testing purposes).
        """
        global _WEB_SERVER_INSTANCE
        _WEB_SERVER_INSTANCE = None


web = WebServerFactory.create()
mcp_server = MCPServerFactory.get()


def mount_service(transport: str = MCPTransportType.SSE) -> None:
    """
    Mount a FastAPI service into the web server.

    Args:
        transport: The transport protocol to use for MCP (sse or http-streaming).
    """
    match transport:
        case MCPTransportType.SSE:
            web.mount("/mcp", mcp_server.sse_app())
        case MCPTransportType.HTTP_STREAMING:
            web.mount("/mcp", mcp_server.streamable_http_app())
        case _:
            raise ValueError(f"Unknown transport protocol: {transport}")


def create_app(
    server_config: ServerConfig | None = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application with MCP server mounted.

    Args:
        server_config: Optional server configuration.

    Returns:
        Configured FastAPI application
    """
    # Load environment variables from file if provided
    load_environment_from_file(server_config.env_file if server_config else None)

    app = WebServerFactory.get()

    # Create client with the token from configuration or environment
    ClickUpAPIClientFactory.create(api_token=get_api_token(server_config))

    # Use default server type if no configuration is provided
    transport = server_config.transport if server_config else MCPTransportType.SSE

    # Mount MCP routes
    mount_service(transport=transport)

    # Root endpoint for health checks
    @app.get("/", response_class=JSONResponse)
    async def root() -> Dict[str, str]:
        """
        Root endpoint providing basic health check.

        Returns:
            JSON response with server status
        """
        return {"status": "ok", "server": "ClickUp MCP Server"}

    # Add MCP endpoints
    @app.get("/mcp/resources", response_class=JSONResponse)
    async def list_resources(request: Request) -> Dict[str, Any]:
        """
        List available MCP resources.

        Args:
            request: FastAPI request object

        Returns:
            JSON response containing available MCP resources
        """
        resources = mcp_server.list_resources()
        return {"resources": resources}

    @app.get("/mcp/tools", response_class=JSONResponse)
    async def get_tools(request: Request) -> Dict[str, Any]:
        """
        Get available MCP tools.

        Args:
            request: FastAPI request object

        Returns:
            JSON response containing available MCP tools
        """
        tools = mcp_server.list_tools()
        return {"tools": tools}

    @app.post("/mcp/execute/{tool_name}", response_class=JSONResponse)
    async def execute_tool(tool_name: str, params: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        """
        Execute an MCP tool with the provided parameters.

        Args:
            tool_name: Name of the MCP tool to execute
            params: Parameters to pass to the tool

        Returns:
            JSON response with the result of the tool execution
        """
        # Handle both async and sync execute methods
        execute_method = mcp_server.execute

        # Check if the execute method is a coroutine function
        import inspect

        if inspect.iscoroutinefunction(execute_method):
            result = await execute_method(tool_name, **params)
        else:
            result = execute_method(tool_name, **params)

        return {"result": result}

    return app
