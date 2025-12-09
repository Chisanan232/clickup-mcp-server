"""
Folder DTOs for ClickUp API requests and responses.

These DTOs provide serialization/deserialization helpers for folder creation,
update, and response shapes.

Usage Examples:
    # Python - Create folder payload
    from clickup_mcp.models.dto.folder import FolderCreate

    FolderCreate(name="Planning").to_payload()  # {"name": "Planning"}
"""

from typing import List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "The name of the folder"


class FolderCreate(BaseRequestDTO):
    """
    DTO for creating a new folder.

    API:
        POST /space/{space_id}/folder
        Docs: https://developer.clickup.com/reference/createfolder

    Attributes:
        name: Folder name

    Examples:
        # Python
        FolderCreate(name="Planning").to_payload()
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)


class FolderUpdate(BaseRequestDTO):
    """
    DTO for updating an existing folder.

    API:
        PUT /folder/{folder_id}

    Attributes:
        name: New folder name

    Examples:
        # Python
        FolderUpdate(name="Roadmap").to_payload()
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)


class FolderResp(BaseResponseDTO):
    """
    DTO for folder API responses.

    Represents a folder returned from the ClickUp API with typed refs for space and lists.

    Attributes:
        id: Folder ID
        name: Folder name
        orderindex: Order index
        override_statuses: Whether this folder overrides statuses
        hidden: Whether the folder is hidden
        space: Parent space reference
        task_count: Number of tasks in this folder
        lists: Lists contained in this folder

    Examples:
        # Python - Deserialize from API JSON
        FolderResp.deserialize({"id": "fld_1", "name": "Planning"})
    """

    id: str = Field(description="The unique identifier for the folder")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    orderindex: int | None = Field(default=None, description="The order index of the folder")
    override_statuses: bool = Field(default=False, description="Whether this folder overrides statuses")
    hidden: bool = Field(default=False, description="Whether the folder is hidden")

    # Lightweight typed refs for clarity
    class SpaceRef(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)

    class ListSummary(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)
        orderindex: int | None = Field(default=None)

    space: SpaceRef | None = Field(default=None, description="The space this folder belongs to")
    task_count: int | None = Field(default=None, description="The number of tasks in this folder")
    lists: List[ListSummary] | None = Field(default=None, description="Lists in this folder")
