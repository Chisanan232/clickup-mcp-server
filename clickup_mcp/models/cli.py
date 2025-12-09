"""
Web server and CLI data models.

This module provides Pydantic data models for server configuration, transport types,
and logging levels. These models are used to validate and manage CLI arguments and
server configuration options.

Configuration Models:
- **ServerConfig**: Main server configuration with host, port, logging, transport
- **LogLevel**: Enumeration of logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **MCPTransportType**: Enumeration of MCP transport types (SSE, HTTP_STREAMING)

Usage Examples:
    # Python - Create server config from CLI args
    from clickup_mcp.models.cli import ServerConfig, LogLevel, MCPTransportType

    config = ServerConfig(
        host="127.0.0.1",
        port=8000,
        log_level=LogLevel.INFO,
        transport=MCPTransportType.SSE,
        env_file=".env"
    )

    # Python - Validate port range
    try:
        config = ServerConfig(port=99999)  # Raises ValueError
    except ValueError as e:
        print(f"Invalid config: {e}")

    # Python - Use enum values
    if config.log_level == LogLevel.DEBUG:
        print("Debug mode enabled")

    # CLI - Pass configuration
    # python -m clickup_mcp --host 0.0.0.0 --port 8000 --log-level info --transport sse
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LogLevel(str, Enum):
    """
    Log levels enumeration for type safety.

    Provides standard logging levels compatible with Python's logging module.
    Used to control verbosity of server and application logging.

    Attributes:
        DEBUG: Detailed diagnostic information (level 10)
        INFO: General informational messages (level 20)
        WARNING: Warning messages for potentially problematic situations (level 30)
        ERROR: Error messages for serious problems (level 40)
        CRITICAL: Critical messages for very serious errors (level 50)

    Usage Examples:
        # Python - Use log level
        from clickup_mcp.models.cli import LogLevel

        log_level = LogLevel.DEBUG
        print(log_level.value)  # "debug"

        # Python - Check log level
        if log_level == LogLevel.DEBUG:
            print("Debug logging enabled")

        # CLI - Set log level
        # python -m clickup_mcp --log-level debug
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MCPTransportType(str, Enum):
    """
    MCP server transport type enumeration.

    Specifies the protocol used for MCP server communication with clients.
    Different transports have different characteristics and use cases.

    Attributes:
        SSE: Server-Sent Events transport (streaming over HTTP)
        HTTP_STREAMING: HTTP streaming transport (chunked transfer encoding)

    Transport Characteristics:
    - **SSE**: Traditional server-sent events, good for browser clients
    - **HTTP_STREAMING**: Raw HTTP streaming, more flexible for various clients

    Usage Examples:
        # Python - Use transport type
        from clickup_mcp.models.cli import MCPTransportType

        transport = MCPTransportType.SSE
        print(transport.value)  # "sse"

        # Python - Check transport type
        if transport == MCPTransportType.SSE:
            print("Using SSE transport")

        # CLI - Set transport
        # python -m clickup_mcp --transport sse
        # python -m clickup_mcp --transport http-streaming
    """

    SSE = "sse"
    HTTP_STREAMING = "http-streaming"


class ServerConfig(BaseModel):
    """
    Server configuration data model.

    This model represents the configuration options for the web server,
    with validation and default values. It's typically created from CLI arguments
    and used to initialize the FastAPI server and MCP server instances.

    Attributes:
        host: Host address to bind the server to (default: "0.0.0.0")
        port: Port number to bind the server to (default: 8000, range: 1-65535)
        log_level: Logging level for the server (default: INFO)
        reload: Enable auto-reload on file changes for development (default: False)
        env_file: Path to .env file for environment variables (default: ".env")
        token: ClickUp API token (optional, takes precedence over env file)
        transport: MCP transport type - SSE or HTTP_STREAMING (default: SSE)

    Validation:
    - port: Must be between 1 and 65535 (valid port range)
    - All fields have sensible defaults for development

    Configuration Sources (in precedence order):
    1. Explicit token parameter (highest priority)
    2. Environment variables from .env file
    3. System environment variables
    4. Default values

    Usage Examples:
        # Python - Create from CLI arguments
        from clickup_mcp.models.cli import ServerConfig, LogLevel, MCPTransportType

        config = ServerConfig(
            host="127.0.0.1",
            port=8000,
            log_level=LogLevel.DEBUG,
            reload=True,
            transport=MCPTransportType.SSE
        )

        # Python - With API token
        config = ServerConfig(
            token="pk_your_token_here",
            log_level=LogLevel.INFO
        )

        # Python - Validate configuration
        try:
            config = ServerConfig(port=99999)  # Out of range
        except ValueError as e:
            print(f"Invalid port: {e}")

        # Python - Access configuration values
        print(f"Server: {config.host}:{config.port}")
        print(f"Transport: {config.transport}")
        print(f"Log level: {config.log_level}")

        # CLI - Pass configuration
        # python -m clickup_mcp --host 0.0.0.0 --port 8000 --log-level debug --reload
        # python -m clickup_mcp --token pk_xxx --transport http-streaming
        # python -m clickup_mcp --env .env.production
    """

    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to bind the server to", ge=1, le=65535)
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    reload: bool = Field(default=False, description="Enable auto-reload for development")
    env_file: str = Field(default=".env", description="Path to the .env file for environment variables")
    token: str | None = Field(
        default=None, description="ClickUp API token. If provided, takes precedence over token from env file"
    )
    transport: MCPTransportType = Field(
        default=MCPTransportType.SSE, description="Type of server to run (sse or http-streaming)"
    )

    @classmethod
    @field_validator("port")
    def validate_port_range(cls, v: int) -> int:
        """
        Validate that the port is in the valid range.

        Ensures the port number is within the valid range for network services (1-65535).
        Ports below 1024 require elevated privileges on Unix systems.

        Args:
            v: Port number to validate

        Returns:
            int: The validated port number

        Raises:
            ValueError: If port is not in range 1-65535

        Usage Examples:
            # Python - Valid port
            config = ServerConfig(port=8000)  # OK

            # Python - Invalid port
            try:
                config = ServerConfig(port=0)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")

            try:
                config = ServerConfig(port=99999)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v

    model_config = ConfigDict(use_enum_values=True)  # Use string values from enums
