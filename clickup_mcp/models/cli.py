"""
Web server data models.

This module provides data models for the web server configuration.
"""

from enum import Enum

from pydantic import BaseModel, Field, validator


class LogLevel(str, Enum):
    """Log levels enumeration for type safety."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ServerConfig(BaseModel):
    """
    Server configuration data model.

    This model represents the configuration options for the web server,
    with validation and default values.
    """

    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to bind the server to", ge=1, le=65535)
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    reload: bool = Field(default=False, description="Enable auto-reload for development")

    @validator("port")
    def validate_port_range(cls, v: int) -> int:
        """Validate that the port is in the valid range."""
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True  # Use string values from enums
