"""MCP input models for folder operations.

High-signal schemas with constraints and examples for FastMCP.
"""

from typing import Optional

from pydantic import BaseModel, Field


class FolderCreateInput(BaseModel):
    """Create a folder. HTTP: POST /space/{space_id}/folder

    When to use: You know the parent space and want to group lists into a folder.
    If you don’t know `space_id`, call `workspace.list` → `space.list` first.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"space_id": "space_1", "name": "[TEST] Planning"}
            ]
        }
    }

    space_id: str = Field(..., min_length=1, description="Parent space ID.")
    name: str = Field(..., min_length=1, description="Folder name.")


class FolderGetInput(BaseModel):
    """Get a folder. HTTP: GET /folder/{folder_id}

    When to use: Retrieve folder details by ID.
    """

    model_config = {
        "json_schema_extra": {"examples": [{"folder_id": "folder_1"}]}
    }

    folder_id: str = Field(..., min_length=1, description="Folder ID.")


class FolderUpdateInput(BaseModel):
    """Update a folder. HTTP: PUT /folder/{folder_id}

    When to use: Rename a folder. Only name updates are supported here.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"folder_id": "folder_1", "name": "Roadmap"}
            ]
        }
    }

    folder_id: str = Field(..., min_length=1, description="Folder ID.")
    name: Optional[str] = Field(None, min_length=1, description="New folder name.")


class FolderDeleteInput(BaseModel):
    """Delete a folder. HTTP: DELETE /folder/{folder_id}

    When to use: Permanently remove a folder and its lists/tasks associations (per permissions).
    """

    model_config = {
        "json_schema_extra": {"examples": [{"folder_id": "folder_1"}]}
    }

    folder_id: str = Field(..., min_length=1, description="Folder ID.")


class FolderListInSpaceInput(BaseModel):
    """List folders in a space. HTTP: GET /space/{space_id}/folder

    When to use: Discover folders within a given space.
    """

    model_config = {
        "json_schema_extra": {"examples": [{"space_id": "space_1"}]}
    }

    space_id: str = Field(..., min_length=1, description="Space ID.")
