"""
Health check DTOs for the ClickUp MCP Server.

This module provides data transfer objects for health check responses
that can be used to verify server status and availability.
"""

from pydantic import ConfigDict, Field

from clickup_mcp.models.dto.base import BaseResponseDTO


class HealthyCheckResponseDto(BaseResponseDTO):
    """
    Health check response DTO.
    
    This class represents the response from the server's health check endpoint.
    It provides information about the server status and identity.
    
    Attributes:
        status: Current status of the server (default: "ok")
        server: Name of the server instance (default: "ClickUp MCP Server")
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow", 
        arbitrary_types_allowed=True,
        frozen=True,
    )

    status: str = Field(default="ok", description="Status of the server")
    server: str = Field(default="ClickUp MCP Server", description="Name of the server")
