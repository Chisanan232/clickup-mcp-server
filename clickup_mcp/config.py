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
    
    # Optional Test/Fallback Token (keeping for backward compatibility)
    e2e_test_api_token: Optional[SecretStr] = Field(
        default=None,
        description="Fallback API token for E2E testing"
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
