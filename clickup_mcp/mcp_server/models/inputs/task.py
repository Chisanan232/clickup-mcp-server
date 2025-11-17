"""MCP input models for task operations.

These inputs are LLM-friendly contracts used by FastMCP tools. They map to
Domain entities first, then DTOs for ClickUp wire format.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TaskCreateInput(BaseModel):
    """Create a task or subtask. HTTP: POST /list/{list_id}/task

    When to use: You know the target list and want to create a task. Set `parent` to create a subtask
    in the same list. If you don’t know `list_id`, call `workspace.list` → `space.list` →
    `list.list_in_folder` or `list.list_in_space_folderless`.
    Constraints: `priority` 1..4; time fields are epoch ms. Custom fields are not set here; use
    `task.set_custom_field` after creation.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "list_id": "123",
                    "name": "Ship v1.2",
                    "status": "in progress",
                    "priority": 3,
                    "assignees": [42],
                    "due_date": 1731523200000,
                },
                {
                    "list_id": "123",
                    "name": "Implement child task",
                    "parent": "task_abc",
                },
            ]
        }
    }

    list_id: str = Field(
        ...,
        min_length=1,
        description="Target ClickUp list ID (home list for the new task).",
        examples=["123", "list_1"],
    )
    name: str = Field(..., min_length=1, description="Short task title.", examples=["Ship v1.2", "Fix login bug"])
    description: Optional[str] = Field(
        None, description="Markdown/plaintext body.", examples=["We need to ship v1.2 by Friday."]
    )
    status: Optional[str] = Field(
        None,
        description="Workflow status by name (e.g., 'Open', 'In progress').",
        examples=["open", "in progress", "done"],
    )
    priority: Optional[int] = Field(
        None, ge=1, le=4, description="1=Low, 2=Normal, 3=High, 4=Urgent.", examples=[1, 2, 3, 4]
    )
    assignees: List[int | str] = Field(
        default_factory=list,
        description="Assignee user IDs.",
        examples=[[42], ["usr_abc"], [42, 43]],
    )
    due_date: Optional[int] = Field(None, description="Due timestamp in epoch milliseconds.", examples=[1731523200000])
    time_estimate: Optional[int] = Field(None, description="Estimate in milliseconds.", examples=[3600000, 14400000])
    parent: Optional[str] = Field(
        None, description="Parent task ID to create a subtask in the same list.", examples=["task_abc"]
    )


class TaskUpdateInput(BaseModel):
    """Update a task (no custom fields). HTTP: PUT /task/{task_id}

    When to use: Change core fields like name/status/priority/assignees/due/estimate.
    To change custom fields, call `task.set_custom_field` instead.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_id": "task_123",
                    "status": "done",
                    "priority": 2,
                    "assignees": [42, 43],
                }
            ]
        }
    }

    task_id: str = Field(..., min_length=1, description="Target task ID.", examples=["task_123", "CU-123"])
    name: Optional[str] = Field(
        None, min_length=1, description="New task title.", examples=["Update changelog", "Ship v1.2"]
    )
    description: Optional[str] = Field(
        None, description="Markdown/plaintext body.", examples=["Release notes and migration steps."]
    )
    status: Optional[str] = Field(
        None, description="Workflow status by name.", examples=["open", "in progress", "done"]
    )
    priority: Optional[int] = Field(None, ge=1, le=4, description="1..4 priority.", examples=[1, 2, 3, 4])
    assignees: Optional[List[int | str]] = Field(
        None, description="Assignee user IDs.", examples=[[42], ["usr_abc"], [42, 43]]
    )
    due_date: Optional[int] = Field(None, description="Due timestamp in epoch milliseconds.", examples=[1731523200000])
    time_estimate: Optional[int] = Field(None, description="Estimate in milliseconds.", examples=[7200000])


class TaskGetInput(BaseModel):
    """Get a task. HTTP: GET /task/{task_id}

    When to use: You have a task ID and need its details. If using custom task IDs,
    set `custom_task_ids=true` and provide `team_id`.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"task_id": "task_123"},
                {"task_id": "CU-123", "custom_task_ids": True, "team_id": "team_1"},
            ]
        }
    }

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "CU-123"])
    subtasks: Optional[bool] = Field(None, description="Include subtasks (true/false).", examples=[True, False])
    custom_task_ids: bool = Field(False, description="Whether using custom task IDs.", examples=[True, False])
    team_id: Optional[str] = Field(
        None,
        description="Team ID (required when custom_task_ids=true).",
        examples=["team_1", "9018752317"],
    )


class TaskListInListInput(BaseModel):
    """List tasks in a list. HTTP: GET /list/{list_id}/task

    When to use: Retrieve tasks from a specific list with pagination and filters.
    Constraints: `limit` ≤ 100 per API; set `include_timl` to include tasks present in multiple lists.
    If you don’t know `list_id`, call discovery tools first.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"list_id": "123", "limit": 50, "statuses": ["open", "in progress"]},
                {"list_id": "123", "page": 1, "limit": 100, "include_timl": True},
            ]
        }
    }

    list_id: str = Field(..., min_length=1, description="List ID.", examples=["123", "list_1"])
    page: int = Field(0, ge=0, description="Page number (0-indexed).", examples=[0, 1, 2])
    limit: int = Field(100, ge=1, le=100, description="Page size (cap 100 by API).", examples=[25, 50, 100])
    include_closed: bool = Field(False, description="Include closed tasks.", examples=[True, False])
    include_timl: bool = Field(False, description="Include tasks from other lists (TIML).", examples=[True, False])
    statuses: Optional[List[str]] = Field(
        None, description="Filter by status names.", examples=[["open"], ["open", "in progress"]]
    )
    assignees: Optional[List[int | str]] = Field(
        None, description="Filter by assignee user IDs.", examples=[[42], ["usr_abc"]]
    )


class TaskSetCustomFieldInput(BaseModel):
    """Set a task custom field. HTTP: POST /task/{task_id}/field/{field_id}

    When to use: Set or change a single custom field value.
    Body is always {"value": ...} as required by ClickUp API.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"task_id": "task_123", "field_id": "cf_priority", "value": 3},
                {"task_id": "task_123", "field_id": "cf_text", "value": "Ready to ship"},
            ]
        }
    }

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "CU-123"])
    field_id: str = Field(..., min_length=1, description="Custom field ID.", examples=["cf_priority", "cf_text"])
    value: object = Field(
        ...,
        description="Value to set (type depends on field).",
        examples=[3, "Ready to ship", True, 1700000000000],
    )


class TaskClearCustomFieldInput(BaseModel):
    """Clear a task custom field. HTTP: DELETE /task/{task_id}/field/{field_id}

    When to use: Remove a custom field value from a task.
    """

    model_config = {"json_schema_extra": {"examples": [{"task_id": "task_123", "field_id": "cf_priority"}]}}

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "CU-123"])
    field_id: str = Field(..., min_length=1, description="Custom field ID.", examples=["cf_priority", "cf_text"])


class TaskAddDependencyInput(BaseModel):
    """Add a dependency. HTTP: POST /task/{task_id}/dependency

    When to use: Add a dependency relationship between two tasks.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [{"task_id": "task_123", "depends_on": "task_456", "dependency_type": "waiting_on"}]
        }
    }

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123"])
    depends_on: str = Field(
        ..., min_length=1, description="The ID of the task this task depends on.", examples=["task_456"]
    )
    dependency_type: str = Field(
        "waiting_on",
        description="Dependency type (waiting_on/blocking).",
        examples=["waiting_on", "blocking"],
    )
