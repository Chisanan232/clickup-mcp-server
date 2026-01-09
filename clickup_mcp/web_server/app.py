"""
FastAPI Web Server for ClickUp MCP.

Design:
- Provides a singleton FastAPI app via `WebServerFactory`.
- Mounts the Model Context Protocol (MCP) server under either SSE or HTTP streaming
  transports using `mount_service()`.
- Integrates ClickUp webhook ingress under `/webhook`.
- Adds a `/health` endpoint for liveness checks.

Transports:
- SSE: mounted at `/sse`
- HTTP streaming: mounted at `/mcp`

High-level flow (sequence):
    Client → FastAPI → (SSE|HTTP-streaming) → MCP Server → ClickUp API
                                 ↘
                                  Webhooks → /webhook → EventSink (local|mq) → Handlers

Configuration:
- Uses `ServerConfig` for token, env file, and transport preferences.
- Loads environment from `.env` (optional) before creating the API client.

 Architecture (Mermaid):
 ```mermaid
 sequenceDiagram
     autonumber
     participant Client
     participant FastAPI as FastAPI App
     participant MCP as MCP Server
     participant ClickUp as ClickUp API
     participant WH as Webhook Router
     participant Sink as EventSink
     participant H as Handlers

     Client->>FastAPI: HTTP (SSE / HTTP-streaming)
     FastAPI->>MCP: Forward protocol traffic
     MCP->>ClickUp: REST API calls
     ClickUp-->>MCP: API responses
     MCP-->>FastAPI: Tool results
     FastAPI-->>Client: Responses

     Note over ClickUp,WH: Out-of-band webhooks
     ClickUp->>WH: POST /webhook/clickup
     WH->>Sink: Normalize and dispatch
     Sink->>H: Execute registered handlers
 ```
"""

from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from clickup_mcp._base import BaseServerFactory
from clickup_mcp.client import ClickUpAPIClientFactory, get_api_token
from clickup_mcp.config import get_settings
from clickup_mcp.mcp_server.app import mcp_factory
from clickup_mcp.models.cli import MCPTransportType, ServerConfig
from clickup_mcp.models.dto.health_check import HealthyCheckResponseDto
from clickup_mcp.web_server.event.bootstrap import import_handler_modules_from_env
from clickup_mcp.web_server.event.webhook import router as clickup_webhook_router

_WEB_SERVER_INSTANCE: Optional[FastAPI] = None


class WebServerFactory(BaseServerFactory[FastAPI]):
    """
    Factory for creating and managing FastAPI web server instances.

    This factory implements the singleton pattern to ensure only one
    FastAPI server instance exists throughout the application lifecycle.
    It provides methods for creating, retrieving, and resetting the server.

    The server is configured with:
    - CORS middleware for cross-origin requests
    - ClickUp webhook router for event handling
    - MCP server mounting for protocol support
    - Health check endpoint

    Usage Examples:
        # Python - Create and use the web server
        from clickup_mcp.web_server.app import WebServerFactory

        server = WebServerFactory.create()
        # Server is now running with MCP endpoints

        # Get existing server
        server = WebServerFactory.get()

        # Reset for testing
        WebServerFactory.reset()
    """

    @staticmethod
    def create(**kwargs) -> FastAPI:
        """
        Create and configure the web API server singleton instance.

        This method creates a new FastAPI application with the following features:
        - CORS middleware configured for all origins (adjust for production)
        - ClickUp webhook router mounted
        - MCP server lifespan management
        - Comprehensive error handling

        Args:
            **kwargs: Additional arguments (unused, but included for base class compatibility)

        Returns:
            Configured FastAPI server instance

        Raises:
            AssertionError: If a server instance already exists

        Usage Examples:
            # Python - Create the web server
            server = WebServerFactory.create()
        """
        # Create a new FastAPI instance
        global _WEB_SERVER_INSTANCE
        assert _WEB_SERVER_INSTANCE is None, "It is not allowed to create more than one instance of web server."
        # Create FastAPI app
        _WEB_SERVER_INSTANCE = FastAPI(
            title="ClickUp MCP Server",
            description="A FastAPI web server that hosts a ClickUp MCP server for interacting with ClickUp API",
            version="0.1.0",
            lifespan=mcp_factory.lifespan(),
        )

        # Configure CORS
        _WEB_SERVER_INSTANCE.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, replace with specific origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # Mount ClickUp webhook endpoint(s)
        _WEB_SERVER_INSTANCE.include_router(clickup_webhook_router)
        return _WEB_SERVER_INSTANCE

    @staticmethod
    def get() -> FastAPI:
        """
        Get the existing FastAPI web server singleton instance.

        Returns the previously created server instance. Raises an assertion
        error if no server has been created yet. Use create() to initialize
        the server before calling this method.

        Returns:
            Configured FastAPI server instance

        Raises:
            AssertionError: If the server has not been created yet

        Usage Examples:
            # Python - Get existing server
            server = WebServerFactory.get()
            # Server is ready to use
        """
        assert _WEB_SERVER_INSTANCE is not None, "It must be created web server first."
        return _WEB_SERVER_INSTANCE

    @staticmethod
    def reset() -> None:
        """
        Reset the singleton instance to None.

        This method clears the cached server instance, allowing a new one
        to be created. Primarily used for testing and in scenarios where
        you need to reinitialize the server with different configuration.

        Usage Examples:
            # Python - Reset for testing
            WebServerFactory.reset()
            server = WebServerFactory.create()
        """
        global _WEB_SERVER_INSTANCE
        _WEB_SERVER_INSTANCE = None


web_factory = WebServerFactory
web = web_factory.create()


def mount_service(transport: str = MCPTransportType.SSE) -> None:
    """
    Mount the MCP service into the FastAPI web server.

    This function mounts the Model Context Protocol (MCP) server as a sub-application
    on the FastAPI server, enabling MCP clients to communicate with the ClickUp API
    through the specified transport protocol.

    The MCP server can be accessed at:
    - SSE transport: http://host:port/sse
    - HTTP Streaming transport: http://host:port/mcp

    Args:
        transport: The transport protocol to use for MCP (sse or http-streaming).
                  Defaults to MCPTransportType.SSE.

    Raises:
        ValueError: If an unknown transport protocol is specified

    Usage Examples:
        # Python - Mount with SSE transport (default)
        mount_service(transport="sse")

        # Python - Mount with HTTP streaming transport
        mount_service(transport="http-streaming")

        # curl - Access MCP via SSE
        curl http://localhost:8000/sse

        # curl - Access MCP via HTTP streaming
        curl http://localhost:8000/mcp
    """
    match transport:
        case MCPTransportType.SSE:
            web_factory.get().mount("/sse", mcp_factory.get().sse_app())
        case MCPTransportType.HTTP_STREAMING:
            web_factory.get().mount("/mcp", mcp_factory.get().streamable_http_app())
        case _:
            raise ValueError(f"Unknown transport protocol: {transport}")


def create_app(
    server_config: ServerConfig | None = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application with MCP server mounted.

    This function is the main entry point for initializing the ClickUp MCP server.
    It performs the following initialization steps:

    1. Creates and configures the ClickUp API client with authentication (using Settings)
    2. Mounts the MCP server with the specified transport protocol
    3. Registers user-defined event handlers
    4. Configures health check endpoint

    The resulting FastAPI application is ready to:
    - Accept MCP protocol requests via SSE or HTTP streaming
    - Handle ClickUp webhook events
    - Provide health check status
    - Serve API documentation at /docs and /redoc

    Args:
        server_config: Optional ServerConfig instance containing:
            - env_file: Path to .env file for environment variables
            - token: ClickUp API token (overrides env variable if provided)
            - transport: MCP transport protocol (sse or http-streaming)
            - host: Server host address
            - port: Server port number
            - log_level: Logging level

    Returns:
        Configured FastAPI application ready to serve requests

    Raises:
        ValueError: If API token cannot be found
        ValueError: If unknown transport protocol is specified

    Usage Examples:
        # Python - Create with default configuration
        from clickup_mcp.web_server.app import create_app

        app = create_app()
        # App is ready to use

        # Python - Create with custom configuration
        from clickup_mcp.models.cli import ServerConfig

        config = ServerConfig(
            token="pk_...",
            env_file=".env",
            transport="sse",
            host="0.0.0.0",
            port=8000
        )
        app = create_app(server_config=config)

        # curl - Health check
        curl http://localhost:8000/health

        # curl - Access API documentation
        curl http://localhost:8000/docs

        # wget - Health check
        wget http://localhost:8000/health

        # Python - Run with uvicorn
        import uvicorn
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    # Create client with the token from configuration or environment
    # get_api_token uses get_settings() which handles environment loading
    ClickUpAPIClientFactory.create(api_token=get_api_token(server_config))

    # Use default server type if no configuration is provided
    transport = server_config.transport if server_config else MCPTransportType.SSE

    # Mount MCP routes
    mount_service(transport=transport)

    # Import user handler modules from env if provided
    import_handler_modules_from_env(server_config.env_file if server_config else None)

    # Root endpoint for health checks
    @web.get("/health", response_class=JSONResponse)
    async def root() -> HealthyCheckResponseDto:
        """
        Health check endpoint for monitoring server status.

        This endpoint provides a simple health check that returns the current
        server status. It can be used by load balancers, monitoring systems,
        and orchestration platforms to verify the server is running.

        Returns:
            HealthyCheckResponseDto with server status information

        Usage Examples:
            # curl - Check server health
            curl http://localhost:8000/health

            # wget - Check server health
            wget -O - http://localhost:8000/health

            # Python - Check server health
            import httpx
            response = httpx.get("http://localhost:8000/health")
            print(response.json())
        """
        return HealthyCheckResponseDto()

    return web
