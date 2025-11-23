"""
Tests for environment variable loading.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest import MonkeyPatch

from clickup_mcp.client import (
    ClickUpAPIClientFactory,
    get_api_token,
)


class TestEnvLoading:
    """Tests for environment variable loading functions."""

    def test_get_api_token(self, monkeypatch: MonkeyPatch) -> None:
        """Test getting API token from environment."""
        # Set up environment variable
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_from_env")

        # Test getting token from environment
        token = get_api_token()
        assert token == "test_token_from_env"

    def test_get_api_token_with_config(self, monkeypatch: MonkeyPatch) -> None:
        """Test getting API token from ServerConfig."""
        # Set up environment variable (should be ignored when config has token)
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_from_env")

        # Create config with token
        from clickup_mcp.models.cli import ServerConfig

        config = ServerConfig(token="test_token_from_config")

        # Test getting token from config
        token = get_api_token(config)
        assert token == "test_token_from_config"

    def test_get_api_token_missing(self, monkeypatch: MonkeyPatch) -> None:
        """Test error when API token is missing from environment."""
        # Ensure environment is clean
        monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)
        monkeypatch.delenv("E2E_TEST_API_TOKEN", raising=False)

        # Test that ValueError is raised when token is missing
        with pytest.raises(ValueError, match="ClickUp API token not found"):
            get_api_token()

    def test_get_api_token_loads_from_env_file(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """Token should be read from the provided env_file even if create_app wasn't called."""
        # Ensure environment is clean
        monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

        # Create .env file containing the token
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=token-from-env-file\n")

        # Build a ServerConfig that points to this env file, without CLI token
        from clickup_mcp.models.cli import ServerConfig

        config = ServerConfig(env_file=str(env_file))

        # get_api_token should load env file internally and return its value
        token = get_api_token(config)
        assert token == "token-from-env-file"

        # Also ensure the environment was actually populated
        assert os.environ.get("CLICKUP_API_TOKEN") == "token-from-env-file"

    def test_get_api_token_missing_with_nonexistent_env_file(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """When env_file doesn't exist and no env var present, an error should be raised."""
        # Ensure environment is clean
        monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)
        monkeypatch.delenv("E2E_TEST_API_TOKEN", raising=False)

        # Point to a non-existent env file
        missing_env = tmp_path / "does_not_exist.env"

        from clickup_mcp.models.cli import ServerConfig

        config = ServerConfig(env_file=str(missing_env))

        with pytest.raises(ValueError, match="ClickUp API token not found"):
            get_api_token(config)

    def test_env_auto_discovery_with_parent_dotenv(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """Ensure find_dotenv discovers .env in parent when running from a subdirectory."""
        # Create parent .env with fallback variable
        parent_env = tmp_path / ".env"
        parent_env.write_text("E2E_TEST_API_TOKEN=parent-token\n")

        # Create a subdirectory and chdir into it (no .env here)
        subdir = tmp_path / "child"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        # Ensure environment is clean
        monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)
        monkeypatch.delenv("E2E_TEST_API_TOKEN", raising=False)

        from clickup_mcp.models.cli import ServerConfig

        # Use default env_file (".env"); discovery should find parent's .env
        config = ServerConfig()
        token = get_api_token(config)
        assert token == "parent-token"

    def test_clickup_api_client_factory(self, monkeypatch: MonkeyPatch) -> None:
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

    def test_entry_point_env_loading(self, monkeypatch: MonkeyPatch) -> None:
        """Test environment loading at entry point."""
        # Create a temp file with test token
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_file.write("CLICKUP_API_TOKEN=test_token_from_entry_point\n")

        try:
            # Reset all singletons before test
            from clickup_mcp.mcp_server.app import MCPServerFactory
            from clickup_mcp.web_server.app import WebServerFactory

            WebServerFactory.reset()
            MCPServerFactory.reset()
            ClickUpAPIClientFactory.reset()

            # Ensure environment is clean
            monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)

            # Create MCP server first, then web server (important for dependency order)
            MCPServerFactory.create()
            WebServerFactory.create()

            # Create a mock function that simulates create_app loading environment variables
            from fastapi import FastAPI

            from clickup_mcp.models.cli import ServerConfig

            def mock_create_app_impl(server_config: ServerConfig | None = None) -> FastAPI:
                # Simulate loading environment from file as create_app would do
                if server_config is not None and server_config.env_file:
                    from pathlib import Path

                    from dotenv import load_dotenv

                    env_path = Path(server_config.env_file)
                    if env_path.exists():
                        load_dotenv(env_path)
                return WebServerFactory.get()

            # Mock uvicorn.run to prevent actual server startup and patch the create_app in the entry module
            from clickup_mcp.entry import run_server

            with patch("uvicorn.run"), patch("clickup_mcp.entry.create_app") as mock_create_app:
                # Set up the mock to call our implementation
                mock_create_app.side_effect = mock_create_app_impl

                # Create server config with our temp env file
                config = ServerConfig(env_file=temp_file.name)

                # Run the server (should pass config to create_app which loads the environment)
                run_server(config)

                # Check that create_app was called with the correct parameters
                mock_create_app.assert_called_once_with(server_config=config)

                # Check that environment was loaded correctly by our mock implementation
                assert os.environ.get("CLICKUP_API_TOKEN") == "test_token_from_entry_point"
        finally:
            # Clean up
            Path(temp_file.name).unlink(missing_ok=True)

            # Reset all singletons after test
            WebServerFactory.reset()
            MCPServerFactory.reset()
            ClickUpAPIClientFactory.reset()
