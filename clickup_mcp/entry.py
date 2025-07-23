"""
Main entry point for the ClickUp MCP FastAPI server.

This module provides the entry point for running the FastAPI server
that hosts the ClickUp MCP functionality.
"""

import argparse
import logging
import sys
from typing import Dict, Optional, Union

import uvicorn
from fastapi import FastAPI
from pydantic import ValidationError

from clickup_mcp.models.cli import LogLevel, ServerConfig, MCPServerType
from clickup_mcp.utils import load_environment_from_file
from clickup_mcp.web_server.app import create_app


def parse_args() -> ServerConfig:
    """
    Parse command line arguments into a ServerConfig model.

    Returns:
        ServerConfig instance with parsed command line arguments
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
    parser.add_argument(
        "--server-type", 
        type=str, 
        default="sse", 
        dest="mcp_server_type",
        choices=[server_type.value for server_type in MCPServerType],
        help="Type of MCP server to run (sse or http-streaming)"
    )

    # Parse args into a dictionary
    args_namespace = parser.parse_args()
    args_dict: Dict[str, Union[str, int, bool]] = vars(args_namespace)

    try:
        # Convert to ServerConfig model
        return ServerConfig(**args_dict)
    except ValidationError as e:
        print(f"Error in server configuration: {e}", file=sys.stderr)
        sys.exit(1)


def configure_logging(log_level: str) -> None:
    """
    Configure logging with the specified log level.

    Args:
        log_level: The logging level to use
    """
    numeric_level: Optional[int] = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(level=numeric_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def run_server(config: ServerConfig) -> None:
    """
    Run the FastAPI server with the specified configuration.

    Args:
        config: Server configuration
    """
    configure_logging(config.log_level)

    # Load environment variables from .env file
    load_environment_from_file(config.env_file)

    # Create the FastAPI app with server configuration
    app = create_app(config)

    # Log server startup information
    logging.info(f"Starting server on {config.host}:{config.port}")
    logging.info(f"Log level: {config.log_level}")
    logging.info(f"Auto-reload: {'enabled' if config.reload else 'disabled'}")
    logging.info(f"Environment file: {config.env_file or '.env'}")
    logging.info(f"MCP server type: {config.mcp_server_type}")

    # Run the server
    uvicorn.run(app=app, host=config.host, port=config.port, log_level=config.log_level.lower(), reload=config.reload)


def main() -> None:
    """
    Main entry point for the CLI.
    """
    config = parse_args()
    run_server(config)


if __name__ == "__main__":
    main()
