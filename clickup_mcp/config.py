import os
from functools import lru_cache
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings model using Pydantic Settings.
    
    This model handles configuration loading from environment variables and .env files.
    It provides type safety, validation, and secure handling of secrets.
    """
    
    # ClickUp API Configuration
    clickup_api_token: Optional[SecretStr] = Field(
        default=None,
        description="ClickUp API token for authentication"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Webhook Handler Configuration
    clickup_webhook_handler_modules: str = Field(
        default="",
        description="Comma-separated list of Python module paths to import for webhook handling"
    )
    
    # CORS Configuration
    cors_allow_origins: list[str] = Field(
        default=["*"],
        description="List of origins that are allowed to make cross-origin requests"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Indicate that cookies should be supported for cross-origin requests"
    )
    cors_allow_methods: list[str] = Field(
        default=["*"],
        description="List of allowed HTTP methods"
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="List of allowed HTTP headers"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


class TestSettings(BaseSettings):
    """
    Configuration settings for End-to-End tests.
    
    These settings are used only during testing to identify valid resources
    (Team, Space, Folder, List, etc.) in the target ClickUp workspace.
    """
    
    # Auth Token for Tests
    e2e_test_api_token: Optional[SecretStr] = Field(
        default=None,
        description="Valid ClickUp API token for running E2E tests"
    )
    
    # Test Resource IDs
    clickup_test_team_id: Optional[str] = Field(
        default=None, 
        description="Team ID to create temporary resources in"
    )
    clickup_test_space_id: Optional[str] = Field(
        default=None,
        description="Space ID used by folder/list tests"
    )
    clickup_test_folder_id: Optional[str] = Field(
        default=None,
        description="Folder ID used by list tests"
    )
    clickup_test_list_id: Optional[str] = Field(
        default=None,
        description="Primary list ID for task tests"
    )
    clickup_test_list_id_2: Optional[str] = Field(
        default=None,
        description="Secondary list ID for multi-list task tests"
    )
    clickup_test_custom_field_id: Optional[str] = Field(
        default=None,
        description="Custom field ID for custom field tests"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


@lru_cache
def get_settings(env_file: Optional[str] = None) -> Settings:
    """
    Get the application settings.
    
    Args:
        env_file: Optional path to a specific .env file. 
                 If provided, it overrides the default .env file.
    
    Returns:
        Settings instance
    """
    if env_file:
        return Settings(_env_file=env_file)
        
    return Settings()
