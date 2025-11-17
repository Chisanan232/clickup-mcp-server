"""Result models for Task tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class PriorityInfo(BaseModel):
    """Structured priority for clarity: numeric value and label."""

    value: int = Field(..., ge=1, le=4, description="Priority value (1=Urgent, 4=low)", examples=[1, 2, 3, 4])
    label: str = Field(..., description="Priority label (URGENT/HIGH/NORMAL/LOW)", examples=["HIGH"])


class TaskResult(BaseModel):
    """Concise task detail; normalized units."""

    id: str = Field(..., description="Task ID", examples=["t1", "task_123"])
    name: str = Field(..., description="Task title", examples=["Ship v1.2", "Fix login bug"])
    status: Optional[str] = Field(None, description="Workflow status name", examples=["open", "in progress", "done"])
    # Deprecated: legacy numeric priority retained for backward compatibility.
    priority: Optional[int] = Field(
        None,
        ge=1,
        le=4,
        description="[Deprecated] Numeric priority only. Use priority_info for value+label.",
        examples=[1, 2, 3, 4],
    )
    priority_info: Optional[PriorityInfo] = Field(
        None,
        description="Priority details with both numeric value and label.",
        examples=[{"value": 2, "label": "HIGH"}],
    )
    list_id: Optional[str] = Field(None, description="Home list ID", examples=["L1", "list_1"])
    assignee_ids: List[int | str] = Field(
        default_factory=list, description="Assigned user IDs", examples=[[42], ["usr_abc"], [42, 43]]
    )
    due_date_ms: Optional[int] = Field(
        None, ge=0, description="Due timestamp in epoch milliseconds", examples=[1731004800000]
    )
    url: Optional[str] = Field(None, description="Canonical task URL", examples=["https://app.clickup.com/t/t1"])
    parent_id: Optional[str] = Field(None, description="Parent task ID for subtasks", examples=["task_parent"])

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
                    "priority_info": {"value": 3, "label": "NORMAL"},
                }
            ]
        }
    }


class TaskListItem(BaseModel):
    id: str = Field(..., description="Task ID", examples=["t1", "task_123"])
    name: str = Field(..., description="Task title", examples=["Backfill analytics", "Fix webhook retry"])
    status: Optional[str] = Field(None, description="Workflow status", examples=["open", "in progress", "done"])
    list_id: Optional[str] = Field(None, description="Home list ID", examples=["L1", "list_1"])
    url: Optional[str] = Field(None, description="Canonical URL", examples=["https://app.clickup.com/t/t1"])


class TaskListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[TaskListItem] = Field(
        default_factory=list,
        examples=[[{"id": "t1", "name": "Backfill analytics"}, {"id": "t2", "name": "Fix webhook retry"}]],
    )
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)", examples=["page=2"])
    truncated: bool = Field(False, description="True if items were trimmed to budget", examples=[False])

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
