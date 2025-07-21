"""
Tests for environment variable loading.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from clickup_mcp.client import (
    create_clickup_client,
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

    def test_create_clickup_client(self, monkeypatch):
        """Test creating ClickUp client with token."""
        with patch("clickup_mcp.client.ClickUpAPIClient") as mock_client:
            # Create client with explicit token
            client = create_clickup_client(api_token="test_token")

            # Check that the client was created with the correct token
            mock_client.assert_called_once_with(api_token="test_token")

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

        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as temp_file:
            temp_file.write(b"CLICKUP_API_TOKEN=test_token_from_entry_point")

        try:
            # Ensure environment is clean
            monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

            # Mock uvicorn.run to prevent actual server startup
            with patch("uvicorn.run"), patch("clickup_mcp.web_server.app.create_app"):
                # Create server config with our temp env file
                config = ServerConfig(env_file=temp_file.name)

                # Run the server (should load environment from our file)
                run_server(config)

                # Check that environment was loaded correctly
                assert os.environ.get("CLICKUP_API_TOKEN") == "test_token_from_entry_point"
        finally:
            # Clean up
            Path(temp_file.name).unlink(missing_ok=True)
