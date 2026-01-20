from functools import lru_cache
from typing import Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from clickup_mcp.types import ClickUpToken, LogLevel, EnvironmentFile


class Settings(BaseSettings):
    """
    Application settings model using Pydantic Settings.

    This model handles configuration loading from environment variables and .env files.
    It provides type safety, validation, and secure handling of secrets.
    """

    # ClickUp API Configuration
    clickup_api_token: Optional[SecretStr] = Field(default=None, description="ClickUp API token for authentication")

    # Logging Configuration
    log_level: LogLevel = Field(default="info", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    @field_validator('log_level', mode='before')
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        """Normalize log level to lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v

    # Webhook Handler Configuration
    clickup_webhook_handler_modules: str = Field(
        default="", description="Comma-separated list of Python module paths to import for webhook handling"
    )

    # CORS Configuration
    cors_allow_origins: list[str] = Field(
        default=["*"], description="List of origins that are allowed to make cross-origin requests"
    )
    cors_allow_credentials: bool = Field(
        default=True, description="Indicate that cookies should be supported for cross-origin requests"
    )
    cors_allow_methods: list[str] = Field(default=["*"], description="List of allowed HTTP methods")
    cors_allow_headers: list[str] = Field(default=["*"], description="List of allowed HTTP headers")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)


@lru_cache
def get_settings(env_file: Optional[EnvironmentFile] = None) -> Settings:
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
