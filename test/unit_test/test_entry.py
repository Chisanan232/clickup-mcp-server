"""
Unit tests for the entry point module.

This module tests the command-line parsing, configuration, and server setup
functionality in the entry.py module.
"""

import logging
from typing import Any, List, Optional
from unittest.mock import MagicMock, call, patch

import pytest
from fastapi import FastAPI

from clickup_mcp.entry import configure_logging, main, parse_args, run_server
from clickup_mcp.models.cli import LogLevel, ServerConfig


class TestEntry:
    """Test suite for the entry module."""

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_args_default_values(self, mock_parse_args: MagicMock) -> None:
        """Test parsing command-line arguments with default values."""
        # Set up mock to return default values
        namespace = MagicMock()
        namespace.host = "0.0.0.0"
        namespace.port = 8000
        namespace.log_level = LogLevel.INFO
        namespace.reload = False
        mock_parse_args.return_value = namespace

        # Call the function
        config = parse_args()

        # Verify the result
        assert isinstance(config, ServerConfig)
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.log_level == LogLevel.INFO
        assert config.reload is False

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_args_custom_values(self, mock_parse_args: MagicMock) -> None:
        """Test parsing command-line arguments with custom values."""
        # Set up mock to return custom values
        namespace = MagicMock()
        namespace.host = "127.0.0.1"
        namespace.port = 9000
        namespace.log_level = LogLevel.DEBUG
        namespace.reload = True
        mock_parse_args.return_value = namespace

        # Call the function
        config = parse_args()

        # Verify the result
        assert isinstance(config, ServerConfig)
        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.log_level == LogLevel.DEBUG
        assert config.reload is True

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_args_invalid_port(self, mock_parse_args: MagicMock) -> None:
        """Test parsing command-line arguments with an invalid port."""
        # Set up mock to return invalid port value
        namespace = MagicMock()
        namespace.host = "127.0.0.1"
        namespace.port = 70000  # Invalid port
        namespace.log_level = LogLevel.INFO
        namespace.reload = False
        mock_parse_args.return_value = namespace

        # Call the function and verify it raises an exception
        with patch("sys.exit") as mock_exit:
            parse_args()
            mock_exit.assert_called_once_with(1)

    @patch("logging.basicConfig")
    def test_configure_logging(self, mock_basic_config: MagicMock) -> None:
        """Test configuring logging with various log levels."""
        # Test each log level
        for level in LogLevel:
            configure_logging(level)
            numeric_level = getattr(logging, level.name)
            mock_basic_config.assert_called_with(
                level=numeric_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

    def test_configure_logging_invalid_level(self) -> None:
        """Test configuring logging with an invalid log level."""
        with pytest.raises(ValueError, match=r"Invalid log level"):
            configure_logging("invalid_level")

    @patch("uvicorn.run")
    @patch("clickup_mcp.entry.create_app")
    @patch("logging.info")
    def test_run_server(self, mock_logging: MagicMock, mock_create_app: MagicMock, mock_uvicorn_run: MagicMock) -> None:
        """Test running the server with a configuration."""
        # Set up mocks
        mock_app = FastAPI()
        mock_create_app.return_value = mock_app

        # Create a configuration
        config = ServerConfig(host="127.0.0.1", port=8888, log_level=LogLevel.DEBUG, reload=True)

        # Call the function
        run_server(config)

        # Verify logging calls
        assert mock_logging.call_count >= 3
        mock_logging.assert_has_calls(
            [call("Starting server on 127.0.0.1:8888"), call("Log level: debug"), call("Auto-reload: enabled")],
            any_order=True,
        )

        # Verify uvicorn.run was called with the right parameters
        mock_uvicorn_run.assert_called_once_with(
            app=mock_app, host="127.0.0.1", port=8888, log_level="debug", reload=True
        )

    @patch("clickup_mcp.entry.parse_args")
    @patch("clickup_mcp.entry.run_server")
    def test_main(self, mock_run_server: MagicMock, mock_parse_args: MagicMock) -> None:
        """Test the main entry point function."""
        # Set up mock configuration
        config = ServerConfig()
        mock_parse_args.return_value = config

        # Call the function
        main()

        # Verify functions were called
        mock_parse_args.assert_called_once()
        mock_run_server.assert_called_once_with(config)
