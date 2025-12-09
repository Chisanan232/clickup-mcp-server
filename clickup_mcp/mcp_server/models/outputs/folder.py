"""Result models for Folder tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class FolderResult(BaseModel):
    """
    Concise folder detail for LLM planning.

    Attributes:
        id: Folder ID
        name: Folder name
        space_id: Parent space ID if present
    """

    id: str = Field(..., description="Folder ID", examples=["folder_1", "fld_abc"])
    name: str = Field(..., description="Folder name", examples=["Planning", "Roadmap"])
    space_id: Optional[str] = Field(None, description="Parent space ID", examples=["space_1", "spc_abc"])

    model_config = {"json_schema_extra": {"examples": [{"id": "folder_1", "name": "Planning", "space_id": "space_1"}]}}


class FolderListItem(BaseModel):
    """Item shape for folder summaries returned by MCP tools."""

    id: str = Field(..., description="Folder ID", examples=["folder_1", "fld_abc"])
    name: str = Field(..., description="Folder name", examples=["Planning", "Roadmap"])


class FolderListResult(BaseModel):
    """
    List wrapper for folders within a space.

    Attributes:
        items: Folders contained in the space
    """

    items: List[FolderListItem] = Field(
        default_factory=list,
        description="Folders within a space",
        examples=[[{"id": "folder_1", "name": "Planning"}]],
    )

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "folder_1", "name": "Planning"}]}]}}
