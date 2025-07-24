"""
Tests for the CLI --env option functionality.
"""

import tempfile
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from unittest import mock

import pytest

from clickup_mcp.client import ClickUpAPIClientFactory, get_api_token
from clickup_mcp.utils import load_environment_from_file
from clickup_mcp.web_server.app import create_app, mount_service
from clickup_mcp.entry import parse_args, run_server
from clickup_mcp.models.cli import MCPServerType, ServerConfig


class TestCliOptionEnv:
    """Tests for the CLI --env option."""

    def test_env_cli_parameter(self):
        """Test parsing the --env CLI parameter."""
        # Create a temporary env file path
        temp_env_path = "/tmp/custom_test.env"

        # Simulate CLI args with --env
        with patch("sys.argv", ["clickup_mcp", "--env", temp_env_path]):
            config = parse_args()
            assert isinstance(config, ServerConfig)
            assert config.env_file == temp_env_path

    def test_env_file_passed_to_create_app(self, monkeypatch):
        """Test that the env file path is correctly passed to create_app."""
        # Create a temp .env file with a test token
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_file.write("CLICKUP_API_TOKEN=test_token_from_cli_env\n")
            env_path = temp_file.name

        try:
            # Create a config with our temp env file
            config = ServerConfig(env_file=env_path)

            # Ensure environment is clean
            monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

            # Mock create_app and uvicorn.run to prevent actual server startup
            with (
                patch("clickup_mcp.entry.create_app") as mock_create_app,
                patch("clickup_mcp.entry.uvicorn.run") as mock_run,
            ):
                # Run the server with our config
                run_server(config)

                # Check that create_app was called with our config containing the env_file path
                mock_create_app.assert_called_once_with(config)

                # Verify the config passed to create_app has the correct env_file
                call_args = mock_create_app.call_args[0][0]
                assert call_args.env_file == env_path

                # Verify uvicorn.run was called
                assert mock_run.called

        finally:
            # Clean up temp file
            Path(env_path).unlink(missing_ok=True)


class TestCliOptionServerType:
    """Test cases for server type CLI option."""

    def test_server_type_enum(self):
        """Test that the ServerType enum has expected values."""
        assert MCPServerType.SSE.value == "sse"
        assert MCPServerType.HTTP_STREAMING.value == "http-streaming"
        assert not hasattr(MCPServerType, "BOTH")

    def test_default_server_type(self):
        """Test that the default server type is 'sse'."""
        with patch("sys.argv", ["program"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.SSE.value

    def test_sse_server_type(self):
        """Test that '--server-type sse' sets server_type to SSE."""
        with patch("sys.argv", ["program", "--server-type", "sse"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.SSE.value

    def test_http_streaming_server_type(self):
        """Test that '--server-type http-streaming' sets server_type to HTTP_STREAMING."""
        with patch("sys.argv", ["program", "--server-type", "http-streaming"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.HTTP_STREAMING.value

    def test_invalid_server_type(self):
        """Test that an invalid server type raises a system exit."""
        with patch("sys.argv", ["program", "--server-type", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_mount_service_sse_only(self):
        """Test that only SSE endpoints are mounted when server_type is SSE."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_web = MagicMock()

        # Test direct mount_service function
        with patch("clickup_mcp.web_server.app.web", mock_web):
            mount_service(mock_mcp_server, MCPServerType.SSE.value)

        # Verify that only SSE endpoint was mounted
        mock_mcp_server.sse_app.assert_called_once()
        mock_mcp_server.streamable_http_app.assert_not_called()
        assert mock_web.mount.call_count == 1
        mock_web.mount.assert_called_with("/mcp", mock_mcp_server.sse_app.return_value)

    def test_mount_service_http_streaming_only(self):
        """Test that only HTTP_STREAMING endpoints are mounted when server_type is HTTP_STREAMING."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_web = MagicMock()

        # Test direct mount_service function
        with patch("clickup_mcp.web_server.app.web", mock_web):
            mount_service(mock_mcp_server, MCPServerType.HTTP_STREAMING.value)

        # Verify that only HTTP_STREAMING endpoint was mounted
        mock_mcp_server.sse_app.assert_not_called()
        mock_mcp_server.streamable_http_app.assert_called_once()
        assert mock_web.mount.call_count == 1
        mock_web.mount.assert_called_with("/mcp", mock_mcp_server.streamable_http_app.return_value)

    @patch("clickup_mcp.mcp_server.app.MCPServerFactory.get")
    def test_create_app_with_sse_server_type(self, mock_mcp_factory, monkeypatch):
        """Test create_app with SSE server type config."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_mcp_factory.return_value = mock_mcp_server
        mock_web = MagicMock()

        # Set up API token in environment
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_for_server_type")

        # Create a ServerConfig with SSE server type
        config = ServerConfig(mcp_server_type=MCPServerType.SSE.value)

        with patch("clickup_mcp.web_server.app.WebServerFactory.get", return_value=mock_web):
            with patch("clickup_mcp.web_server.app.mount_service") as mock_mount:
                # Reset client factory to ensure it will create a new instance with our token
                from clickup_mcp.client import ClickUpAPIClientFactory

                ClickUpAPIClientFactory.reset()

                create_app(config)
                mock_mount.assert_called_once_with(mock_mcp_server, MCPServerType.SSE.value)


class TestCliOptionToken:
    """Tests for the CLI --token option."""

    def test_server_config_with_token(self):
        """Test that ServerConfig accepts token field."""
        config = ServerConfig(token="test-token")
        assert config.token == "test-token"


    def test_parse_args_with_token(self, monkeypatch):
        """Test that token CLI option is correctly parsed."""
        # Mock sys.argv to include token option
        with mock.patch.object(sys, "argv", ["program", "--token", "cli-token-value"]):
            config = parse_args()
            assert config.token == "cli-token-value"


    def test_token_takes_precedence_over_env_file(self, monkeypatch, tmp_path):
        """Test that token from CLI takes precedence over token from .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=env-file-token")

        # Mock sys.argv to include both token and env file options
        with mock.patch.object(sys, "argv", ["program", "--token", "cli-token-value", "--env", str(env_file)]):
            config = parse_args()

            # Load the environment file
            load_environment_from_file(config.env_file)

            # Test that the token is loaded from CLI option
            token = get_api_token(config)
            assert token == "cli-token-value"


    def test_env_file_token_used_when_no_cli_token(self, monkeypatch, tmp_path):
        """Test that token is loaded from .env file when no CLI token is provided."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=env-file-token")

        # Mock sys.argv to include env file option but no token
        with mock.patch.object(sys, "argv", ["program", "--env", str(env_file)]):
            config = parse_args()

            # Load the environment file first
            load_environment_from_file(config.env_file)

            # Ensure no token in environment at start
            monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

            # Now test that the token is loaded from .env file
            monkeypatch.setenv("CLICKUP_API_TOKEN", "env-file-token")
            token = get_api_token(config)
            assert token == "env-file-token"


    def test_create_app_with_token(self):
        """Test that create_app uses the token from ServerConfig."""
        # Reset singletons before test
        from clickup_mcp.mcp_server.app import MCPServerFactory
        from clickup_mcp.web_server.app import WebServerFactory

        WebServerFactory.reset()
        MCPServerFactory.reset()
        ClickUpAPIClientFactory.reset()

        # Create web and MCP server instances first
        WebServerFactory.create()
        MCPServerFactory.create()

        config = ServerConfig(token="test-token")

        with mock.patch("clickup_mcp.web_server.app.ClickUpAPIClientFactory.create") as mock_create_client:
            create_app(config)
            mock_create_client.assert_called_once()
            # Check that token was passed to ClickUpAPIClientFactory.create
            args, kwargs = mock_create_client.call_args
            assert kwargs.get("api_token") == "test-token"

        # Clean up after test
        WebServerFactory.reset()
        MCPServerFactory.reset()
        ClickUpAPIClientFactory.reset()
