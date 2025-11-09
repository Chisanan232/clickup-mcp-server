"""
Space DTOs for ClickUp API requests and responses.

These DTOs handle serialization/deserialization of Space data
for API interactions.
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class SpaceCreate(BaseRequestDTO):
    """DTO for creating a new space.

    POST /team/{team_id}/space
    https://developer.clickup.com/reference/createspace
    """

    name: str = Field(description="The name of the space")
    multiple_assignees: bool = Field(default=False, description="Whether multiple assignees are allowed")
    features: Dict[str, Any] | None = Field(default=None, description="Features to enable for this space")


class SpaceUpdate(BaseRequestDTO):
    """DTO for updating an existing space.

    PUT /space/{space_id}
    """

    name: str | None = Field(default=None, description="The name of the space")
    private: bool | None = Field(default=None, description="Whether the space is private")
    multiple_assignees: bool | None = Field(default=None, description="Whether multiple assignees are allowed")


class SpaceResp(BaseResponseDTO):
    """DTO for space API responses.

    Represents a space returned from the ClickUp API.
    """

    id: str = Field(description="The unique identifier for the space")
    name: str = Field(description="The name of the space")
    private: bool = Field(default=False, description="Whether the space is private")
    statuses: List[Dict[str, Any]] = Field(default_factory=list, description="The statuses defined for this space")
    multiple_assignees: bool = Field(default=False, description="Whether multiple assignees are allowed")
    features: Dict[str, Any] | None = Field(default=None, description="Features enabled for this space")
    team_id: str | None = Field(default=None, description="The team ID this space belongs to")
