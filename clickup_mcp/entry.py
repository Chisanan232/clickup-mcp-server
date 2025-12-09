"""
Main entry point for the ClickUp MCP FastAPI server.

This module provides the entry point for running the FastAPI server
that hosts the ClickUp MCP functionality.
"""

import argparse
import logging
import sys

import uvicorn
from fastapi import FastAPI
from pydantic import ValidationError

from clickup_mcp.models.cli import LogLevel, MCPTransportType, ServerConfig
from clickup_mcp.web_server.app import create_app


def parse_args() -> ServerConfig:
    """
    Parse command line arguments into a ServerConfig model.

    This function parses CLI arguments and validates them against the ServerConfig
    model, providing a type-safe configuration object for the server.

    Supported CLI Arguments:
        --host: Server host address (default: 0.0.0.0)
        --port: Server port number (default: 8000, range: 1-65535)
        --log-level: Logging level (choices: debug, info, warning, error, critical)
        --reload: Enable auto-reload for development
        --env: Path to .env file for environment variables (default: .env)
        --token: ClickUp API token (overrides env file if provided)
        --transport: MCP transport protocol (choices: sse, http-streaming)

    Returns:
        ServerConfig instance with parsed and validated command line arguments

    Raises:
        SystemExit: If validation fails or help is requested

    Usage Examples:
        # Python - Parse arguments
        config = parse_args()

        # CLI - Run with custom host and port
        python -m clickup_mcp --host 127.0.0.1 --port 9000

        # CLI - Run with custom .env file
        python -m clickup_mcp --env .env.production

        # CLI - Run with API token
        python -m clickup_mcp --token pk_your_token_here

        # CLI - Run with HTTP streaming transport
        python -m clickup_mcp --transport http-streaming

        # CLI - Run with debug logging and auto-reload
        python -m clickup_mcp --log-level debug --reload

        # CLI - Full custom configuration
        python -m clickup_mcp \\
            --host 0.0.0.0 \\
            --port 8080 \\
            --log-level info \\
            --env .env.staging \\
            --transport sse \\
            --reload
    """
    parser = argparse.ArgumentParser(description="Run the ClickUp MCP FastAPI server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument(
        "--log-level", type=str, default="info", choices=[level.value for level in LogLevel], help="Logging level"
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument(
        "--env", type=str, dest="env_file", default=".env", help="Path to the .env file for environment variables"
    )
    parser.add_argument("--token", type=str, help="ClickUp API token (overrides token from .env file if provided)")
    parser.add_argument(
        "--transport",
        type=str,
        default="sse",
        dest="transport",
        choices=[transport_type.value for transport_type in MCPTransportType],
        help="Transport protocol to use for MCP (sse or http-streaming)",
    )

    # Parse args into a dictionary
    args_namespace = parser.parse_args()
    args_dict: dict[str, str | int | bool] = vars(args_namespace)

    try:
        # Convert to ServerConfig model
        return ServerConfig(**args_dict)
    except ValidationError as e:
        print(f"Error in server configuration: {e}", file=sys.stderr)
        sys.exit(1)


def configure_logging(log_level: str) -> None:
    """
    Configure logging with the specified log level.

    Sets up the Python logging system with a standard format that includes
    timestamps, logger names, log levels, and messages. This is applied
    globally to all loggers in the application.

    Args:
        log_level: The logging level to use (debug, info, warning, error, critical)

    Raises:
        ValueError: If an invalid log level is specified

    Usage Examples:
        # Python - Configure debug logging
        configure_logging("debug")

        # Python - Configure info logging (default)
        configure_logging("info")

        # Python - Configure error logging
        configure_logging("error")
    """
    numeric_level: int | None = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Configure logging
    logging.basicConfig(level=numeric_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def run_server(config: ServerConfig) -> None:
    """
    Run the FastAPI server with the specified configuration.

    This function is the main server execution function. It:
    1. Configures logging based on the specified log level
    2. Creates and initializes the FastAPI application
    3. Logs startup information for debugging and monitoring
    4. Starts the uvicorn ASGI server with the provided configuration

    The server will remain running until interrupted (Ctrl+C).

    Args:
        config: ServerConfig instance containing server configuration:
            - host: Server host address
            - port: Server port number
            - log_level: Logging level
            - reload: Enable auto-reload for development
            - env_file: Path to .env file
            - transport: MCP transport protocol

    Usage Examples:
        # Python - Run with default configuration
        from clickup_mcp.models.cli import ServerConfig
        from clickup_mcp.entry import run_server

        config = ServerConfig()
        run_server(config)

        # Python - Run with custom configuration
        config = ServerConfig(
            host="127.0.0.1",
            port=9000,
            log_level="debug",
            reload=True,
            transport="sse"
        )
        run_server(config)

        # CLI - Run with default settings
        python -m clickup_mcp

        # CLI - Run with custom settings
        python -m clickup_mcp --host 127.0.0.1 --port 9000 --log-level debug --reload
    """
    # Configure logging
    configure_logging(config.log_level)

    # Create and configure the FastAPI application
    app: FastAPI = create_app(server_config=config)

    # Log server startup information
    logging.info(f"Starting server on {config.host}:{config.port}")
    logging.info(f"Log level: {config.log_level}")
    logging.info(f"Auto-reload: {'enabled' if config.reload else 'disabled'}")
    logging.info(f"Environment file: {config.env_file or '.env'}")
    logging.info(f"Transport protocol: {config.transport}")

    # Run the server
    uvicorn.run(app=app, host=config.host, port=config.port, log_level=config.log_level.lower(), reload=config.reload)


def main() -> None:
    """
    Main entry point for the ClickUp MCP Server CLI.

    This function serves as the primary entry point when running the server
    from the command line. It:
    1. Parses command line arguments
    2. Validates the configuration
    3. Starts the server with the specified settings

    The server will listen for MCP protocol requests and handle ClickUp API
    interactions through the configured transport protocol (SSE or HTTP streaming).

    Usage Examples:
        # CLI - Run with default settings
        python -m clickup_mcp

        # CLI - Run with custom host and port
        python -m clickup_mcp --host 0.0.0.0 --port 8080

        # CLI - Run with debug logging
        python -m clickup_mcp --log-level debug

        # CLI - Run with custom .env file
        python -m clickup_mcp --env .env.production

        # CLI - Run with API token
        python -m clickup_mcp --token pk_your_token_here

        # CLI - Run with HTTP streaming transport
        python -m clickup_mcp --transport http-streaming

        # CLI - Run with all options
        python -m clickup_mcp \\
            --host 0.0.0.0 \\
            --port 8000 \\
            --log-level info \\
            --env .env \\
            --token pk_your_token_here \\
            --transport sse \\
            --reload
    """
    config = parse_args()
    run_server(config)


if __name__ == "__main__":
    main()
