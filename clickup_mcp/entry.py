"""
Main entry point for the ClickUp MCP FastAPI server.

This module provides the entry point for running the FastAPI server
that hosts the ClickUp MCP functionality.
"""

import sys
import logging
import argparse

import uvicorn
from pydantic import ValidationError

from clickup_mcp.models.cli import ServerConfig, LogLevel
from clickup_mcp.web.app import create_app


def parse_args() -> ServerConfig:
    """
    Parse command line arguments into a ServerConfig model.
    
    Returns:
        ServerConfig instance with parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Run the ClickUp MCP FastAPI server")
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="info",
        choices=[level.value for level in LogLevel],
        help="Logging level"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    
    # Parse args into a dictionary
    args_namespace = parser.parse_args()
    args_dict = vars(args_namespace)
    
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
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def run_server(config: ServerConfig) -> None:
    """
    Run the FastAPI server with the specified configuration.
    
    Args:
        config: Server configuration
    """
    configure_logging(config.log_level)
    
    # Create the FastAPI app
    app = create_app()
    
    # Log server startup information
    logging.info(f"Starting server on {config.host}:{config.port}")
    logging.info(f"Log level: {config.log_level}")
    logging.info(f"Auto-reload: {'enabled' if config.reload else 'disabled'}")
    
    # Run the server
    uvicorn.run(
        app=app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
        reload=config.reload
    )


def create_app_factory():
    """
    Create the FastAPI app for Uvicorn's use with reload.
    
    Returns:
        The FastAPI application
    """
    return create_app()


def main() -> None:
    """
    Main entry point for the CLI.
    """
    config = parse_args()
    run_server(config)


if __name__ == "__main__":
    main()
