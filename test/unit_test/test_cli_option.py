"""
Tests for the CLI --env option functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, ANY

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from clickup_mcp.client import get_api_token
from clickup_mcp.entry import main, parse_args
from clickup_mcp.mcp_server.app import MCPServerFactory
from clickup_mcp.models.cli import MCPTransportType, ServerConfig
from clickup_mcp.utils import load_environment_from_file
from clickup_mcp.web_server.app import create_app, mount_service
from fastapi import FastAPI


class TestCliOptionEnv:
    """Tests for the CLI --env option."""

    def test_env_cli_parameter(self) -> None:
        """Test parsing the --env CLI parameter."""
        # Create a temporary env file path
        temp_env_path = "/tmp/custom_test.env"

        # Simulate CLI args with --env
        with patch("sys.argv", ["clickup_mcp", "--env", temp_env_path]):
            config = parse_args()
            assert isinstance(config, ServerConfig)
            assert config.env_file == temp_env_path

    def test_env_file_passed_to_create_app(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """Test that env_file from CLI args is passed to create_app."""
        # Create a temp file to use as env_file
        temp_file = tmp_path / "test.env"
        temp_file.write_text("# Test env file")

        # Mock the create_app function to capture its arguments
        mock_app = MagicMock()
        mock_create_app = MagicMock(return_value=mock_app)

        with patch("clickup_mcp.entry.create_app", mock_create_app):
            # Suppress server startup
            with patch("uvicorn.run"):
                # Run the server with CLI args including env_file
                sys.argv = ["clickup-mcp-server", "--env", str(temp_file)]
                main()

        # Verify create_app was called with correct arguments
        mock_create_app.assert_called_once()
        kwargs = mock_create_app.call_args.kwargs

        # Check server_config is passed and contains the correct env_file
        assert "server_config" in kwargs
        assert kwargs["server_config"].env_file == str(temp_file)


class TestCliOptionTransport:
    """Test cases for transport protocol CLI option."""

    def test_transport_enum(self) -> None:
        """Test that the TransportType enum has expected values."""
        assert MCPTransportType.SSE.value == "sse"
        assert MCPTransportType.HTTP_STREAMING.value == "http-streaming"
        assert not hasattr(MCPTransportType, "BOTH")

    def test_default_transport(self) -> None:
        """Test that the default transport protocol is 'sse'."""
        with patch("sys.argv", ["program"]):
            config = parse_args()
            assert config.transport == MCPTransportType.SSE.value

    def test_sse_transport(self) -> None:
        """Test that '--transport sse' sets mcp_transport_type to SSE."""
        with patch("sys.argv", ["program", "--transport", "sse"]):
            config = parse_args()
            assert config.transport == MCPTransportType.SSE.value

    def test_http_streaming_transport(self) -> None:
        """Test that '--transport http-streaming' sets mcp_transport_type to HTTP_STREAMING."""
        with patch("sys.argv", ["program", "--transport", "http-streaming"]):
            config = parse_args()
            assert config.transport == MCPTransportType.HTTP_STREAMING.value

    def test_invalid_transport(self) -> None:
        """Test that an invalid transport protocol raises a system exit."""
        with patch("sys.argv", ["program", "--transport", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_mount_service_sse_only(self) -> None:
        """Test that only SSE endpoints are mounted when transport protocol is SSE."""
        # Setup
        mock_mcp = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp.sse_app.return_value = mock_sse_app
        
        # Create mcp_factory mock that returns our mock_mcp
        mock_mcp_factory = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp
        
        mock_web = MagicMock()
        
        # Create a clean patch environment
        with patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp_factory), \
             patch("clickup_mcp.web_server.app.web", mock_web):
            
            # Call the function under test
            mount_service(transport=MCPTransportType.SSE)

        # Verify correct method calls and mounting
        mock_mcp_factory.get.assert_called_once()
        mock_mcp.sse_app.assert_called_once()
        mock_mcp.streamable_http_app.assert_not_called()
        mock_web.mount.assert_called_once_with("/sse", mock_sse_app)

    def test_mount_service_http_streaming_only(self) -> None:
        """Test that only HTTP streaming endpoints are mounted when transport protocol is HTTP_STREAMING."""
        # Setup
        mock_mcp = MagicMock()
        mock_streaming_app = MagicMock()
        mock_mcp.streamable_http_app.return_value = mock_streaming_app
        mock_mcp.sse_app = MagicMock()
        
        # Create mcp_factory mock that returns our mock_mcp
        mock_mcp_factory = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp
        
        mock_web = MagicMock()
        
        # Create a clean patch environment
        with patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp_factory), \
             patch("clickup_mcp.web_server.app.web", mock_web):
            
            # Call the function under test
            mount_service(transport=MCPTransportType.HTTP_STREAMING)

        # Verify correct method calls and mounting
        mock_mcp_factory.get.assert_called_once()
        mock_mcp.streamable_http_app.assert_called_once()
        mock_mcp.sse_app.assert_not_called()
        mock_web.mount.assert_called_once_with("/mcp", mock_streaming_app)

    @patch("clickup_mcp.mcp_server.app.MCPServerFactory.get")
    def test_create_app_with_sse_transport(self, mock_mcp_factory: MagicMock, monkeypatch: MonkeyPatch) -> None:
        """Test create_app with SSE transport protocol config."""
        # Setup
        mock_mcp_factory = MagicMock()
        mock_mcp_factory.return_value = mock_mcp_factory
        mock_web = MagicMock()

        # Set up API token in environment
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_for_transport_type")

        # Create a ServerConfig with SSE transport protocol
        config = ServerConfig(transport=MCPTransportType.SSE)

        with patch("clickup_mcp.web_server.app.WebServerFactory.get", return_value=mock_web):
            with patch("clickup_mcp.web_server.app.mount_service") as mock_mount:
                # Reset client factory to ensure it will create a new instance with our token
                from clickup_mcp.client import ClickUpAPIClientFactory

                ClickUpAPIClientFactory.reset()

                create_app(config)
                mock_mount.assert_called_once()

                # Extract the arguments from the call
                args, kwargs = mock_mount.call_args
                # With the new implementation, the only positional arg should be transport
                if args:
                    # Check if args is passed positionally
                    assert args[0] == config.transport
                elif "transport" in kwargs:
                    # Check if transport is passed as a keyword arg
                    assert kwargs["transport"] == config.transport
                else:
                    # Fail if neither pattern matches
                    assert False, "mount_service not called with expected transport parameter"


class TestCliOptionToken:
    """Tests for the CLI --token option."""

    def test_server_config_with_token(self) -> None:
        """Test that ServerConfig accepts token field."""
        config = ServerConfig(token="test-token")
        assert config.token == "test-token"

    def test_parse_args_with_token(self, monkeypatch: MonkeyPatch) -> None:
        """Test that token CLI option is correctly parsed."""
        # Set up CLI args with token
        test_args = ["--token", "test-token-123"]
        monkeypatch.setattr(sys, "argv", ["app.py"] + test_args)

        # Parse arguments
        with patch("clickup_mcp.entry.ServerConfig", wraps=ServerConfig) as mock_config:
            config = parse_args()

            # Verify token is correctly set in ServerConfig
            assert config.token == "test-token-123"
            mock_config.assert_called_once()
            kwargs = mock_config.call_args[1]
            assert "token" in kwargs
            assert kwargs["token"] == "test-token-123"

    def test_token_takes_precedence_over_env_file(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """Test that token from CLI takes precedence over token from .env file."""
        # Create .env file with a token
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=env-file-token")

        # Set up CLI args with both token and env file
        test_args = ["--token", "cli-token", "--env", str(env_file)]
        monkeypatch.setattr(sys, "argv", ["app.py"] + test_args)

        # Parse arguments
        config = parse_args()
        
        # Ensure CLI token is used, not env file token
        assert config.token == "cli-token"
        assert config.env_file == str(env_file)

        # Verify token precedence
        token = get_api_token(config)
        assert token == "cli-token"

    def test_env_file_token_used_when_no_cli_token(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """Test that token is loaded from .env file when no CLI token is provided."""
        # Create .env file with a token
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=env-file-token")

        # Set up CLI args with env file but no token
        test_args = ["--env", str(env_file)]
        monkeypatch.setattr(sys, "argv", ["app.py"] + test_args)

        # Parse arguments
        config = parse_args()
        
        # No token in config itself
        assert config.token is None
        assert config.env_file == str(env_file)

        # Ensure env file token is used
        monkeypatch.setenv("CLICKUP_API_TOKEN", "env-file-token")
        token = get_api_token(config)
        assert token == "env-file-token"

    def test_create_app_with_token(self) -> None:
        """Test that create_app uses the token from ServerConfig."""
        # Mock configuration
        config = ServerConfig(token="test-token-123")
        mock_mcp_factory = MagicMock()

        # Create required patchers
        client_factory_create_patcher = patch("clickup_mcp.client.ClickUpAPIClientFactory.create")
        get_token_patcher = patch("clickup_mcp.web_server.app.get_api_token", return_value="test-token-123")
        mcp_create_patcher = patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp_factory)
        mcp_get_patcher = patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp_factory)
        mount_service_patcher = patch("clickup_mcp.web_server.app.mount_service")

        # Start all patchers
        mock_client_factory = client_factory_create_patcher.start()
        mock_get_token = get_token_patcher.start()
        mock_mcp_create = mcp_create_patcher.start()
        mock_mcp_get = mcp_get_patcher.start()
        mock_mount = mount_service_patcher.start()
        
        try:
            # Reset both factories to ensure clean test environment
            import clickup_mcp.mcp_server.app as mcp_app
            import clickup_mcp.web_server.app as web_app
            mcp_app._MCP_SERVER_INSTANCE = None
            web_app._WEB_SERVER_INSTANCE = None
            
            # Call the function being tested
            result = create_app(server_config=config)
            
            # Check that token was used correctly
            mock_get_token.assert_called_once_with(config)
            mock_client_factory.assert_called_once_with(api_token="test-token-123")
            
            # Verify FastAPI app was created and returned
            assert isinstance(result, FastAPI)
            
            # Verify mount_service was called with correct transport
            mock_mount.assert_called_once_with(transport=config.transport)
        finally:
            # Stop all patchers
            client_factory_create_patcher.stop()
            get_token_patcher.stop()
            mcp_create_patcher.stop()
            mcp_get_patcher.stop()
            mount_service_patcher.stop()
