"""Result models for List tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ListResult(BaseModel):
    """Concise list detail for LLM planning."""

    id: str = Field(..., description="List ID")
    name: str = Field(..., description="List name")
    status: Optional[str] = Field(None, description="Status label")
    folder_id: Optional[str] = Field(None, description="Parent folder ID")
    space_id: Optional[str] = Field(None, description="Parent space ID")

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": "list_1", "name": "Sprint 12", "status": "Open", "folder_id": "folder_1"}]
        }
    }


class ListListItem(BaseModel):
    id: str = Field(..., description="List ID")
    name: str = Field(..., description="List name")


class ListListResult(BaseModel):
    items: List[ListListItem] = Field(default_factory=list, description="Lists in a folder/space")

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "list_1", "name": "Sprint Backlog"}]}]}}
