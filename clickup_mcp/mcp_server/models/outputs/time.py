"""
Result models for Time Entry tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.

Usage Examples:
    # Python - Single time entry result
    from clickup_mcp.mcp_server.models.outputs.time import TimeEntryResult, TimeEntryListResult, TimeEntryListItem

    t = TimeEntryResult(
        id="entry_1",
        task_id="task_123",
        user_id="user_456",
        team_id="team_789",
        description="Implementation work",
        duration=3600000,
        billable=False
    )

    # Python - List result
    lr = TimeEntryListResult(items=[TimeEntryListItem(id="entry_1", task_id="task_123", description="Implementation work", duration=3600000)])
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TimeEntryResult(BaseModel):
    """Concise time entry detail; normalized units."""

    id: str = Field(..., description="Time entry ID", examples=["entry_1", "ent_123"])
    task_id: str = Field(..., description="Task ID this time entry belongs to", examples=["task_123", "tsk_abc"])
    user_id: str = Field(..., description="User ID who logged the time", examples=["user_456", "usr_xyz"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    description: Optional[str] = Field(
        None, description="Description of the work done", examples=["Implementation work"]
    )
    start: Optional[int] = Field(None, ge=0, description="Start time in epoch milliseconds", examples=[1702080000000])
    end: Optional[int] = Field(None, ge=0, description="End time in epoch milliseconds", examples=[1702083600000])
    duration: Optional[int] = Field(None, ge=0, description="Duration in milliseconds", examples=[3600000])
    billable: bool = Field(False, description="Whether the time entry is billable", examples=[False, True])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "entry_1",
                    "task_id": "task_123",
                    "user_id": "user_456",
                    "team_id": "team_789",
                    "description": "Implementation work",
                    "duration": 3600000,
                    "billable": False,
                }
            ]
        }
    }


class TimeEntryListItem(BaseModel):
    """
    Item shape for time entry summaries returned by MCP tools.

    Attributes:
        id: Time entry ID
        task_id: Task ID this time entry belongs to
        description: Description of the work done
        duration: Duration in milliseconds
    """

    id: str = Field(..., description="Time entry ID", examples=["entry_1", "ent_123"])
    task_id: str = Field(..., description="Task ID this time entry belongs to", examples=["task_123", "tsk_abc"])
    description: Optional[str] = Field(
        None, description="Description of the work done", examples=["Implementation work"]
    )
    duration: Optional[int] = Field(None, ge=0, description="Duration in milliseconds", examples=[3600000])


class TimeEntryListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[TimeEntryListItem] = Field(
        default_factory=list,
        examples=[
            [
                {"id": "entry_1", "task_id": "task_123", "description": "Implementation work", "duration": 3600000},
                {"id": "entry_2", "task_id": "task_456", "description": "Bug fix", "duration": 1800000},
            ]
        ],
    )
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)", examples=["page=2"])
    truncated: bool = Field(False, description="True if items were trimmed to budget", examples=[False])


class TimeTrackingStatus(BaseModel):
    """Time tracking status for a task."""

    active: bool = Field(..., description="Whether time tracking is currently active", examples=[True, False])
    start: Optional[int] = Field(
        None, ge=0, description="Start time of current session in epoch ms", examples=[1702080000000]
    )
    task_id: Optional[str] = Field(
        None, description="Task ID being tracked (if active)", examples=["task_123", "tsk_abc"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"active": True, "start": 1702080000000, "task_id": "task_123"},
                {"active": False, "start": None, "task_id": None},
            ]
        }
    }
