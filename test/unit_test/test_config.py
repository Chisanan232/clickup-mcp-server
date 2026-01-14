"""
Tests for configuration and environment variable loading.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clickup_mcp.client import (
    ClickUpAPIClientFactory,
    get_api_token,
)
from clickup_mcp.config import Settings
from test.config import TestSettings, get_test_settings
from clickup_mcp.config import get_settings


class TestConfig:
    """Tests for Settings and configuration loading."""

    @pytest.fixture(autouse=True)
    def reset_settings(self):
        """Reset the lru_cache of get_settings before each test."""
        get_settings.cache_clear()

        # Also clear env vars that might affect tests
        old_env = os.environ.copy()
        for key in [
            "CLICKUP_API_TOKEN",
            "E2E_TEST_API_TOKEN",
            "LOG_LEVEL",
            "CLICKUP_WEBHOOK_HANDLER_MODULES",
            "CLICKUP_TEST_TEAM_ID",
        ]:
            if key in os.environ:
                del os.environ[key]

        yield

        # Restore env
        os.environ.clear()
        os.environ.update(old_env)

    def test_settings_defaults(self) -> None:
        """Test default settings values."""
        # Pass a non-existent file to ensure we don't load local .env
        settings = Settings(_env_file="non_existent_env_file")
        assert settings.clickup_api_token is None
        assert settings.log_level == "INFO"
        assert settings.clickup_webhook_handler_modules == ""

    def test_test_settings_defaults(self) -> None:
        """Test default TestSettings values."""
        settings = TestSettings(_env_file="non_existent_env_file")
        assert settings.e2e_test_api_token is None
        assert settings.clickup_test_team_id is None

    def test_settings_from_env_vars(self) -> None:
        """Test loading settings from environment variables."""
        os.environ["CLICKUP_API_TOKEN"] = "env_token"
        os.environ["LOG_LEVEL"] = "DEBUG"

        # Pass non-existent file to avoid .env interference
        settings = Settings(_env_file="non_existent_env_file")
        assert settings.clickup_api_token
        assert settings.clickup_api_token.get_secret_value() == "env_token"
        assert settings.log_level == "DEBUG"

    def test_test_settings_from_env_vars(self) -> None:
        """Test loading TestSettings from environment variables."""
        os.environ["E2E_TEST_API_TOKEN"] = "test_token"
        os.environ["CLICKUP_TEST_TEAM_ID"] = "12345"

        settings = TestSettings(_env_file="non_existent_env_file")
        assert settings.e2e_test_api_token
        assert settings.e2e_test_api_token.get_secret_value() == "test_token"
        assert settings.clickup_test_team_id == "12345"

    def test_settings_from_env_file(self, tmp_path: Path) -> None:
        """Test loading settings from a .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=file_token\nLOG_LEVEL=WARNING")

        settings = get_settings(str(env_file))
        assert settings.clickup_api_token
        assert settings.clickup_api_token.get_secret_value() == "file_token"
        assert settings.log_level == "WARNING"

    def test_get_api_token_priority(self, tmp_path: Path) -> None:
        """Test token resolution priority: CLI > Settings(Env Var) > Settings(Env File)."""
        from clickup_mcp.models.cli import ServerConfig

        # 1. Test CLI token priority
        with patch("clickup_mcp.client.get_settings") as mock_settings:
            mock_settings.return_value = Settings(_env_file="non_existent")
            config = ServerConfig(token="cli_token")
            assert get_api_token(config) == "cli_token"

        # 2. Test Env Var priority over File
        os.environ["CLICKUP_API_TOKEN"] = "env_var_token"
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_API_TOKEN=file_token")

        get_settings.cache_clear()
        config = ServerConfig(env_file=str(env_file))
        assert get_api_token(config) == "env_var_token"

        # 3. Test File priority when no Env Var
        del os.environ["CLICKUP_API_TOKEN"]
        get_settings.cache_clear()

        assert get_api_token(config) == "file_token"

    def test_get_api_token_missing(self) -> None:
        """Test error when no token is found."""
        mock_settings = MagicMock()
        mock_settings.clickup_api_token = None

        with patch("clickup_mcp.client.get_settings", return_value=mock_settings):
            with pytest.raises(ValueError, match="ClickUp API token not found"):
                get_api_token()

    def test_cors_settings_defaults(self) -> None:
        """Test default CORS settings."""
        settings = Settings(_env_file="non_existent_env_file")
        assert settings.cors_allow_origins == ["*"]
        assert settings.cors_allow_credentials is True
        assert settings.cors_allow_methods == ["*"]
        assert settings.cors_allow_headers == ["*"]

    def test_cors_settings_from_env_vars(self) -> None:
        """Test loading CORS settings from environment variables."""
        # Pydantic Settings parses lists from JSON strings in env vars
        os.environ["CORS_ALLOW_ORIGINS"] = '["http://localhost:3000", "https://example.com"]'
        os.environ["CORS_ALLOW_CREDENTIALS"] = "False"
        os.environ["CORS_ALLOW_METHODS"] = '["GET", "POST"]'
        os.environ["CORS_ALLOW_HEADERS"] = '["Authorization", "Content-Type"]'

        settings = Settings(_env_file="non_existent_env_file")

        assert settings.cors_allow_origins == ["http://localhost:3000", "https://example.com"]
        assert settings.cors_allow_credentials is False
        assert settings.cors_allow_methods == ["GET", "POST"]
        assert settings.cors_allow_headers == ["Authorization", "Content-Type"]

    def test_webhook_modules_parsing(self, tmp_path: Path) -> None:
        """Test parsing of webhook modules from env."""
        env_file = tmp_path / ".env"
        env_file.write_text("CLICKUP_WEBHOOK_HANDLER_MODULES=mod1, mod2")

        # Direct Settings test
        settings = Settings(_env_file=str(env_file))
        assert settings.clickup_webhook_handler_modules == "mod1, mod2"

        # Test imports via bootstrap (mocking importlib)
        from clickup_mcp.web_server.event.bootstrap import (
            import_handler_modules_from_env,
        )

        with patch("importlib.import_module") as mock_import:
            get_settings.cache_clear()

            modules = import_handler_modules_from_env(str(env_file))
            assert modules == ["mod1", "mod2"]
            assert mock_import.call_count == 2
            mock_import.assert_any_call("mod1")
            mock_import.assert_any_call("mod2")

    def test_clickup_api_client_factory_integration(self) -> None:
        """Test that factory works with the token retrieval."""
        import clickup_mcp.client

        clickup_mcp.client._CLICKUP_API_CLIENT = None

        with patch("clickup_mcp.client.get_api_token", return_value="factory_token"):
            token = "factory_token"
            client = ClickUpAPIClientFactory.create(api_token=token)
            assert client.api_token == "factory_token"

        ClickUpAPIClientFactory.reset()
