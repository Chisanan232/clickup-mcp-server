"""
Folder DTOs for ClickUp API requests and responses.

These DTOs handle serialization/deserialization of Folder data
for API interactions.
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "The name of the folder"


class FolderCreate(BaseRequestDTO):
    """DTO for creating a new folder.

    POST /space/{space_id}/folder
    https://developer.clickup.com/reference/createfolder
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)


class FolderUpdate(BaseRequestDTO):
    """DTO for updating an existing folder.

    PUT /folder/{folder_id}
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)


class FolderResp(BaseResponseDTO):
    """DTO for folder API responses.

    Represents a folder returned from the ClickUp API.
    """

    id: str = Field(description="The unique identifier for the folder")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    orderindex: int | None = Field(default=None, description="The order index of the folder")
    override_statuses: bool = Field(default=False, description="Whether this folder overrides statuses")
    hidden: bool = Field(default=False, description="Whether the folder is hidden")
    space: Dict[str, Any] | None = Field(default=None, description="The space this folder belongs to")
    task_count: int | None = Field(default=None, description="The number of tasks in this folder")
    lists: List[Dict[str, Any]] | None = Field(default=None, description="Lists in this folder")
