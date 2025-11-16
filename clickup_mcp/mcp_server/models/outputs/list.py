"""Result models for List tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ListResult(BaseModel):
    """Concise list detail for LLM planning."""

    id: str = Field(..., description="List ID", examples=["list_1", "lst_abc"])
    name: str = Field(..., description="List name", examples=["Sprint 12", "Sprint Backlog"])
    status: Optional[str] = Field(None, description="Status label", examples=["Open", "In progress", "Done"])
    folder_id: Optional[str] = Field(None, description="Parent folder ID", examples=["folder_1", "fld_abc"])
    space_id: Optional[str] = Field(None, description="Parent space ID", examples=["space_1", "spc_abc"])

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": "list_1", "name": "Sprint 12", "status": "Open", "folder_id": "folder_1"}]
        }
    }


class ListListItem(BaseModel):
    id: str = Field(..., description="List ID", examples=["list_1", "lst_abc"])
    name: str = Field(..., description="List name", examples=["Sprint Backlog", "Bugs"])


class ListListResult(BaseModel):
    items: List[ListListItem] = Field(
        default_factory=list,
        description="Lists in a folder/space",
        examples=[[{"id": "list_1", "name": "Sprint Backlog"}]],
    )

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "list_1", "name": "Sprint Backlog"}]}]}}
