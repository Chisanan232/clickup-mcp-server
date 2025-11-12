"""Result models for Folder tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class FolderResult(BaseModel):
    """Concise folder detail for LLM planning."""

    id: str = Field(..., description="Folder ID")
    name: str = Field(..., description="Folder name")
    space_id: Optional[str] = Field(None, description="Parent space ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"id": "folder_1", "name": "Planning", "space_id": "space_1"}
            ]
        }
    }


class FolderListItem(BaseModel):
    id: str = Field(..., description="Folder ID")
    name: str = Field(..., description="Folder name")


class FolderListResult(BaseModel):
    items: List[FolderListItem] = Field(default_factory=list, description="Folders within a space")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"items": [{"id": "folder_1", "name": "Planning"}]}
            ]
        }
    }
