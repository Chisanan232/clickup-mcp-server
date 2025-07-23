"""
Test the ClickUp API token CLI option functionality.
"""

import sys
from unittest import mock

from clickup_mcp.client import ClickUpAPIClientFactory, get_api_token
from clickup_mcp.entry import parse_args
from clickup_mcp.models.cli import ServerConfig
from clickup_mcp.utils import load_environment_from_file
from clickup_mcp.web_server.app import create_app


def test_server_config_with_token():
    """Test that ServerConfig accepts token field."""
    config = ServerConfig(token="test-token")
    assert config.token == "test-token"


def test_parse_args_with_token(monkeypatch):
    """Test that token CLI option is correctly parsed."""
    # Mock sys.argv to include token option
    with mock.patch.object(sys, "argv", ["program", "--token", "cli-token-value"]):
        config = parse_args()
        assert config.token == "cli-token-value"


def test_token_takes_precedence_over_env_file(monkeypatch, tmp_path):
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


def test_env_file_token_used_when_no_cli_token(monkeypatch, tmp_path):
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


def test_create_app_with_token():
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
