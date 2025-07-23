"""
Tests for environment variable loading.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from clickup_mcp.client import (
    ClickUpAPIClientFactory,
    get_api_token,
)


class TestEnvLoading:
    """Tests for environment variable loading functions."""

    def test_get_api_token(self, monkeypatch):
        """Test getting API token from environment."""
        # Set up environment variable
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_from_env")

        # Test getting token from environment
        token = get_api_token()
        assert token == "test_token_from_env"

    def test_clickup_api_client_factory(self, monkeypatch):
        """Test creating ClickUp client with token."""
        # Reset singleton before test
        import clickup_mcp.client
        clickup_mcp.client._CLICKUP_API_CLIENT = None
        
        with patch("clickup_mcp.client.ClickUpAPIClient") as mock_client:
            # Create client with explicit token
            client = ClickUpAPIClientFactory.create(api_token="test_token")

            # Check that the client was created with the correct token
            mock_client.assert_called_once()
            call_args = mock_client.call_args[1]
            assert call_args["api_token"] == "test_token"
        
        # Reset singleton after test
        clickup_mcp.client._CLICKUP_API_CLIENT = None

    def test_get_api_token_missing(self, monkeypatch):
        """Test error when API token is missing from environment."""
        # Ensure environment is clean
        monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

        # Test that ValueError is raised when token is missing
        with pytest.raises(ValueError, match="ClickUp API token not found"):
            get_api_token()

    def test_entry_point_env_loading(self, monkeypatch):
        """Test environment loading at entry point."""
        from clickup_mcp.entry import run_server
        from clickup_mcp.models.cli import ServerConfig
        from clickup_mcp.web_server.app import WebServerFactory
        from clickup_mcp.mcp_server.app import MCPServerFactory
        from clickup_mcp.client import ClickUpAPIClientFactory

        # Reset all singletons before test
        WebServerFactory.reset()
        MCPServerFactory.reset()
        ClickUpAPIClientFactory.reset()

        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as temp_file:
            temp_file.write(b"CLICKUP_API_TOKEN=test_token_from_entry_point")

        try:
            # Ensure environment is clean
            monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

            # Create web server and MCP server first to avoid assertion errors
            WebServerFactory.create()
            MCPServerFactory.create()

            # Mock uvicorn.run to prevent actual server startup and patch the create_app in the entry module
            with patch("uvicorn.run"), patch("clickup_mcp.entry.create_app") as mock_create_app:
                # Create server config with our temp env file
                config = ServerConfig(env_file=temp_file.name)

                # Run the server (should load environment from our file)
                run_server(config)

                # Check that create_app was called with the correct config
                mock_create_app.assert_called_once_with(config)
                
                # Check that environment was loaded correctly
                assert os.environ.get("CLICKUP_API_TOKEN") == "test_token_from_entry_point"
        finally:
            # Clean up
            Path(temp_file.name).unlink(missing_ok=True)
            
            # Reset all singletons after test
            WebServerFactory.reset()
            MCPServerFactory.reset()
            ClickUpAPIClientFactory.reset()
