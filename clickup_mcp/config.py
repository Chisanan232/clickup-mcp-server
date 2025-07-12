"""
Configuration module for ClickUp API client.

This module provides configuration management for the ClickUp API client,
including environment variable handling and validation.
"""

import os
from typing import Optional, Type

from pydantic import BaseModel, Field, field_validator


class ClickUpConfig(BaseModel):
    """Configuration model for ClickUp API client."""

    api_token: str = Field(..., description="ClickUp API token")
    base_url: str = Field(default="https://api.clickup.com/api/v2", description="Base URL for ClickUp API")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries for failed requests")
    retry_delay: float = Field(default=1.0, description="Initial delay between retries in seconds")
    rate_limit_requests_per_minute: int = Field(default=100, description="Rate limit for API requests per minute")

    @field_validator("api_token")
    @classmethod
    def validate_api_token(cls: Type["ClickUpConfig"], v: str) -> str:
        """Validate that API token is provided and not empty."""
        if not v or not v.strip():
            raise ValueError("API token cannot be empty")
        return v.strip()

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls: Type["ClickUpConfig"], v: float) -> float:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls: Type["ClickUpConfig"], v: int) -> int:
        """Validate max_retries is non-negative."""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    @field_validator("retry_delay")
    @classmethod
    def validate_retry_delay(cls: Type["ClickUpConfig"], v: float) -> float:
        """Validate retry_delay is non-negative."""
        if v < 0:
            raise ValueError("Retry delay cannot be negative")
        return v

    @field_validator("rate_limit_requests_per_minute")
    @classmethod
    def validate_rate_limit(cls: Type["ClickUpConfig"], v: int) -> int:
        """Validate rate limit is positive."""
        if v <= 0:
            raise ValueError("Rate limit must be positive")
        return v

    class Config:
        env_prefix = "CLICKUP_"
        case_sensitive = False
        extra = "forbid"


def load_config_from_env() -> ClickUpConfig:
    """
    Load configuration from environment variables.

    Environment variables:
    - CLICKUP_API_TOKEN: ClickUp API token (required)
    - CLICKUP_BASE_URL: Base URL for API (optional)
    - CLICKUP_TIMEOUT: Request timeout (optional)
    - CLICKUP_MAX_RETRIES: Maximum retries (optional)
    - CLICKUP_RETRY_DELAY: Retry delay (optional)
    - CLICKUP_RATE_LIMIT_REQUESTS_PER_MINUTE: Rate limit (optional)

    Returns:
        ClickUpConfig instance loaded from environment

    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    api_token = os.getenv("CLICKUP_API_TOKEN")
    if not api_token:
        raise ValueError("CLICKUP_API_TOKEN environment variable is required")

    return ClickUpConfig(
        api_token=api_token,
        base_url=os.getenv("CLICKUP_BASE_URL", "https://api.clickup.com/api/v2"),
        timeout=float(os.getenv("CLICKUP_TIMEOUT", "30.0")),
        max_retries=int(os.getenv("CLICKUP_MAX_RETRIES", "3")),
        retry_delay=float(os.getenv("CLICKUP_RETRY_DELAY", "1.0")),
        rate_limit_requests_per_minute=int(os.getenv("CLICKUP_RATE_LIMIT_REQUESTS_PER_MINUTE", "100")),
    )


def get_default_config(api_token: Optional[str] = None) -> ClickUpConfig:
    """
    Get default configuration, optionally with a provided API token.

    Args:
        api_token: Optional API token to use. If not provided, will try to load from environment.

    Returns:
        ClickUpConfig instance with default or environment-based configuration

    Raises:
        ValueError: If no API token is provided and none found in environment
    """
    if api_token:
        return ClickUpConfig(api_token=api_token)
    else:
        return load_config_from_env()
