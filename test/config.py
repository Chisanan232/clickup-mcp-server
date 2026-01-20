"""
Configuration settings for tests.

This module contains test-specific configuration models used across
the test suite for E2E tests, integration tests, and other test scenarios.
"""

from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    """
    Configuration settings for End-to-End tests.

    These settings are used only during testing to identify valid resources
    (Team, Space, Folder, List, etc.) in the target ClickUp workspace.
    """

    # Auth Token for Tests
    e2e_test_api_token: Optional[SecretStr] = Field(
        default=None, description="Valid ClickUp API token for running E2E tests"
    )

    # Test Resource IDs
    clickup_test_team_id: Optional[str] = Field(default=None, description="Team ID to create temporary resources in")
    clickup_test_space_id: Optional[str] = Field(default=None, description="Space ID used by folder/list tests")
    clickup_test_folder_id: Optional[str] = Field(default=None, description="Folder ID used by list tests")
    clickup_test_list_id: Optional[str] = Field(default=None, description="Primary list ID for task tests")
    clickup_test_list_id_2: Optional[str] = Field(
        default=None, description="Secondary list ID for multi-list task tests"
    )
    clickup_test_custom_field_id: Optional[str] = Field(
        default=None, description="Custom field ID for custom field tests"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)


def get_test_settings(env_file: Optional[str] = "./test/.env") -> TestSettings:
    """
    Generate and return a TestSettings instance.

    This utility function provides a convenient way to instantiate TestSettings
    with optional custom .env file path. It's used by the pytest fixture and
    can also be used directly in tests that need to load settings programmatically.

    Args:
            env_file: Optional path to a custom .env file.
                             If provided, it overrides the default .env file.

    Returns:
            TestSettings instance with loaded configuration from environment variables
            or the specified .env file.

    Example:
            >>> settings = get_test_settings()
            >>> api_token = settings.e2e_test_api_token
            >>> team_id = settings.clickup_test_team_id
    """
    if env_file:
        return TestSettings(_env_file=env_file)

    return TestSettings()
