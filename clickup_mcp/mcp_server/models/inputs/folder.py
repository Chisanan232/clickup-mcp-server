"""MCP input models for folder operations.

High-signal schemas with constraints and examples for FastMCP.
"""

from typing import Optional

from pydantic import BaseModel, Field


class FolderCreateInput(BaseModel):
    """
    Create a folder. HTTP: POST /space/{space_id}/folder

    When to use: You know the parent space and want to group lists into a folder.
    If you don’t know `space_id`, call `workspace.list` → `space.list` first.

    Attributes:
        space_id: Parent space ID
        name: Folder name

    Examples:
        FolderCreateInput(space_id="space_1", name="[TEST] Planning")
    """

    model_config = {"json_schema_extra": {"examples": [{"space_id": "space_1", "name": "[TEST] Planning"}]}}

    space_id: str = Field(..., min_length=1, description="Parent space ID.", examples=["space_1", "spc_abc"])
    name: str = Field(..., min_length=1, description="Folder name.", examples=["[TEST] Planning", "Roadmap"])


class FolderGetInput(BaseModel):
    """
    Get a folder. HTTP: GET /folder/{folder_id}

    When to use: Retrieve folder details by ID.

    Attributes:
        folder_id: Folder ID

    Examples:
        FolderGetInput(folder_id="folder_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"folder_id": "folder_1"}]}}

    folder_id: str = Field(..., min_length=1, description="Folder ID.", examples=["folder_1", "fld_abc"])


class FolderUpdateInput(BaseModel):
    """
    Update a folder. HTTP: PUT /folder/{folder_id}

    When to use: Rename a folder. Only name updates are supported here.

    Attributes:
        folder_id: Folder ID
        name: New folder name

    Examples:
        FolderUpdateInput(folder_id="folder_1", name="Roadmap")
    """

    model_config = {"json_schema_extra": {"examples": [{"folder_id": "folder_1", "name": "Roadmap"}]}}

    folder_id: str = Field(..., min_length=1, description="Folder ID.", examples=["folder_1", "fld_abc"])
    name: Optional[str] = Field(None, min_length=1, description="New folder name.", examples=["Roadmap", "Planning"])


class FolderDeleteInput(BaseModel):
    """
    Delete a folder. HTTP: DELETE /folder/{folder_id}

    When to use: Permanently remove a folder and its lists/tasks associations (per permissions).

    Attributes:
        folder_id: Folder ID

    Examples:
        FolderDeleteInput(folder_id="folder_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"folder_id": "folder_1"}]}}

    folder_id: str = Field(
        ..., min_length=1, description="Folder ID.", json_schema_extra={"examples": ["folder_1", "fld_abc"]}
    )


class FolderListInSpaceInput(BaseModel):
    """
    List folders in a space. HTTP: GET /space/{space_id}/folder

    When to use: Discover folders within a given space.

    Attributes:
        space_id: Space ID

    Examples:
        FolderListInSpaceInput(space_id="space_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"space_id": "space_1"}]}}

    space_id: str = Field(..., min_length=1, description="Space ID.", examples=["space_1", "spc_abc"])
