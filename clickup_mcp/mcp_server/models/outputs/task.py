"""Result models for Task tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TaskResult(BaseModel):
    """Concise task detail; normalized units."""

    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task title")
    status: Optional[str] = Field(None, description="Workflow status name")
    priority: Optional[int] = Field(None, ge=1, le=4, description="1=Low, 2=Normal, 3=High, 4=Urgent")
    list_id: Optional[str] = Field(None, description="Home list ID")
    assignee_ids: List[int | str] = Field(default_factory=list, description="Assigned user IDs")
    due_date_ms: Optional[int] = Field(None, ge=0, description="Due timestamp in epoch milliseconds")
    url: Optional[str] = Field(None, description="Canonical task URL")
    parent_id: Optional[str] = Field(None, description="Parent task ID for subtasks")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "t1",
                    "name": "Ship v1.2",
                    "status": "in progress",
                    "priority": 3,
                    "list_id": "L1",
                    "assignee_ids": [42],
                    "due_date_ms": 1731004800000,
                    "url": "https://app.clickup.com/t/t1",
                }
            ]
        }
    }


class TaskListItem(BaseModel):
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task title")
    status: Optional[str] = Field(None, description="Workflow status")
    list_id: Optional[str] = Field(None, description="Home list ID")
    url: Optional[str] = Field(None, description="Canonical URL")


class TaskListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[TaskListItem] = Field(default_factory=list)
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)")
    truncated: bool = Field(False, description="True if items were trimmed to budget")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {"id": "t1", "name": "Backfill analytics"},
                        {"id": "t2", "name": "Fix webhook retry"},
                    ],
                    "next_cursor": "page=2",
                    "truncated": False,
                }
            ]
        }
    }
