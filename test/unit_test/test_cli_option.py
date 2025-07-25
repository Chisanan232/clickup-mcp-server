"""
Tests for the CLI --env option functionality.
"""

import sys
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from pytest import MonkeyPatch

from clickup_mcp.client import ClickUpAPIClientFactory, get_api_token
from clickup_mcp.entry import main, parse_args
from clickup_mcp.models.cli import MCPServerType, ServerConfig
from clickup_mcp.utils import load_environment_from_file
from clickup_mcp.web_server.app import create_app, mount_service


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
        """Test that the ServerType enum has expected values."""
        assert MCPServerType.SSE.value == "sse"
        assert MCPServerType.HTTP_STREAMING.value == "http-streaming"
        assert not hasattr(MCPServerType, "BOTH")

    def test_default_transport(self) -> None:
        """Test that the default transport protocol is 'sse'."""
        with patch("sys.argv", ["program"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.SSE.value

    def test_sse_transport(self) -> None:
        """Test that '--transport sse' sets mcp_server_type to SSE."""
        with patch("sys.argv", ["program", "--transport", "sse"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.SSE.value

    def test_http_streaming_transport(self) -> None:
        """Test that '--transport http-streaming' sets mcp_server_type to HTTP_STREAMING."""
        with patch("sys.argv", ["program", "--transport", "http-streaming"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.HTTP_STREAMING.value

    def test_invalid_transport(self) -> None:
        """Test that an invalid transport protocol raises a system exit."""
        with patch("sys.argv", ["program", "--transport", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_mount_service_sse_only(self) -> None:
        """Test that only SSE endpoints are mounted when transport protocol is SSE."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_web = MagicMock()

        # Test direct mount_service function
        with (
            patch("clickup_mcp.web_server.app.web", mock_web),
            patch("clickup_mcp.web_server.app.mcp_server", mock_mcp_server),
        ):
            mount_service(MCPServerType.SSE.value)

        # Verify that only SSE endpoint was mounted
        mock_mcp_server.sse_app.assert_called_once()
        mock_mcp_server.streamable_http_app.assert_not_called()
        assert mock_web.mount.call_count == 1
        mock_web.mount.assert_called_with("/mcp", mock_mcp_server.sse_app.return_value)

    def test_mount_service_http_streaming_only(self) -> None:
        """Test that only HTTP_STREAMING endpoints are mounted when transport protocol is HTTP_STREAMING."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_web = MagicMock()

        # Test direct mount_service function
        with (
            patch("clickup_mcp.web_server.app.web", mock_web),
            patch("clickup_mcp.web_server.app.mcp_server", mock_mcp_server),
        ):
            mount_service(MCPServerType.HTTP_STREAMING.value)

        # Verify that only HTTP_STREAMING endpoint was mounted
        mock_mcp_server.streamable_http_app.assert_called_once()
        mock_mcp_server.sse_app.assert_not_called()
        assert mock_web.mount.call_count == 1
        mock_web.mount.assert_called_with("/mcp", mock_mcp_server.streamable_http_app.return_value)

    @patch("clickup_mcp.mcp_server.app.MCPServerFactory.get")
    def test_create_app_with_sse_transport(self, mock_mcp_factory: MagicMock, monkeypatch: MonkeyPatch) -> None:
        """Test create_app with SSE transport protocol config."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_mcp_factory.return_value = mock_mcp_server
        mock_web = MagicMock()

        # Set up API token in environment
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_for_server_type")

        # Create a ServerConfig with SSE transport protocol
        config = ServerConfig(mcp_server_type=MCPServerType.SSE)

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
                    assert args[0] == config.mcp_server_type
                elif "transport" in kwargs:
                    # Check if transport is passed as a keyword arg
                    assert kwargs["transport"] == config.mcp_server_type
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
        # Mock sys.argv to include token option
        with mock.patch.object(sys, "argv", ["program", "--token", "cli-token-value"]):
            config = parse_args()
            assert config.token == "cli-token-value"

    def test_token_takes_precedence_over_env_file(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
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

    def test_env_file_token_used_when_no_cli_token(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
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

    def test_create_app_with_token(self) -> None:
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
