"""
Main entry point for the ClickUp MCP FastAPI server.

This module provides the entry point for running the FastAPI server
that hosts the ClickUp MCP functionality.
"""

import os
import logging
import argparse
from typing import Optional

import uvicorn

from .web.app import create_app


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed command line arguments
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
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    
    return parser.parse_args()


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


def run_server(
    host: str = "0.0.0.0", 
    port: int = 8000, 
    log_level: str = "info", 
    reload: bool = False
) -> None:
    """
    Run the FastAPI server with the specified configuration.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        log_level: Logging level
        reload: Whether to enable auto-reload for development
    """
    configure_logging(log_level)
    
    # Create the FastAPI app
    app = create_app()
    
    # Get the FastAPI app factory for Uvicorn
    app_factory = "clickup_mcp.main:create_app_factory()"
    
    # Run the server
    uvicorn.run(
        app=app,
        host=host,
        port=port,
        log_level=log_level.lower(),
        reload=reload
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
    args = parse_args()
    run_server(
        host=args.host, 
        port=args.port, 
        log_level=args.log_level, 
        reload=args.reload
    )


if __name__ == "__main__":
    main()
