"""Result models for List tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ListStatusOutput(BaseModel):
    """
    Status metadata defined on a List.

    Attributes:
        name: Status name as configured on the list (display label)
        type: Status type classification (e.g., open/closed/active/done)
        color: UI color hex or token
        orderindex: Ordering index within the list's statuses
    """

    name: str = Field(..., description="Status name as configured on the list", examples=["Open", "In progress"])
    type: str | None = Field(None, description="Status type (open/closed/active/done)", examples=["open"])
    color: str | None = Field(None, description="UI color (hex or token)", examples=["#6a5acd"])
    orderindex: int | None = Field(None, description="Ordering index", examples=[1])


class ListResult(BaseModel):
    """
    Concise list detail for LLM planning.

    Attributes:
        id: List ID
        name: List name
        status: Status label (if any)
        folder_id: Parent folder ID (if present)
        space_id: Parent space ID (if present)
        statuses: Effective statuses for this list (authoritative for task create/update)
    """

    id: str = Field(..., description="List ID", examples=["list_1", "lst_abc"])
    name: str = Field(..., description="List name", examples=["Sprint 12", "Sprint Backlog"])
    status: Optional[str] = Field(None, description="Status label", examples=["Open", "In progress", "Done"])
    folder_id: Optional[str] = Field(None, description="Parent folder ID", examples=["folder_1", "fld_abc"])
    space_id: Optional[str] = Field(None, description="Parent space ID", examples=["space_1", "spc_abc"])
    statuses: list[ListStatusOutput] | None = Field(
        default=None,
        description="Effective statuses for this list (authoritative for task create/update)",
        examples=[
            [
                {"name": "Open", "type": "open"},
                {"name": "In progress", "type": "active"},
                {"name": "Done", "type": "closed"},
            ]
        ],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "list_1",
                    "name": "Sprint 12",
                    "status": "Open",
                    "folder_id": "folder_1",
                }
            ]
        }
    }


class ListListItem(BaseModel):
    """Item shape for list summaries returned by MCP tools."""

    id: str = Field(..., description="List ID", examples=["list_1", "lst_abc"])
    name: str = Field(..., description="List name", examples=["Sprint Backlog", "Bugs"])


class ListListResult(BaseModel):
    items: List[ListListItem] = Field(
        default_factory=list,
        description="Lists in a folder/space",
        examples=[[{"id": "list_1", "name": "Sprint Backlog"}]],
    )

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "list_1", "name": "Sprint Backlog"}]}]}}
