"""Result models for Folder tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class FolderResult(BaseModel):
    """Concise folder detail for LLM planning."""

    id: str = Field(..., description="Folder ID", examples=["folder_1", "fld_abc"])
    name: str = Field(..., description="Folder name", examples=["Planning", "Roadmap"])
    space_id: Optional[str] = Field(None, description="Parent space ID", examples=["space_1", "spc_abc"])

    model_config = {"json_schema_extra": {"examples": [{"id": "folder_1", "name": "Planning", "space_id": "space_1"}]}}


class FolderListItem(BaseModel):
    id: str = Field(..., description="Folder ID", examples=["folder_1", "fld_abc"])
    name: str = Field(..., description="Folder name", examples=["Planning", "Roadmap"])


class FolderListResult(BaseModel):
    items: List[FolderListItem] = Field(
        default_factory=list,
        description="Folders within a space",
        examples=[[{"id": "folder_1", "name": "Planning"}]],
    )

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "folder_1", "name": "Planning"}]}]}}
