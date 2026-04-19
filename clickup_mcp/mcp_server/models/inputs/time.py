"""MCP input models for time tracking operations.

High-signal schemas for FastMCP with constraints and examples.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TimeEntryCreateInput(BaseModel):
    """
    Create a time entry for a task. HTTP: POST /team/{team_id}/time_entries

    When to use: Log time spent on a specific task. You need the team ID and task ID.

    Constraints:
        - `duration` must be positive (milliseconds)
        - Time fields are epoch milliseconds

    Attributes:
        team_id: Team/workspace ID
        task_id: Task ID to log time against
        description: Optional description of the time entry
        start: Start time in epoch ms
        end: End time in epoch ms (can be omitted if duration is provided)
        duration: Duration in milliseconds (can be omitted if start/end are provided)

    Examples:
        TimeEntryCreateInput(team_id="team_1", task_id="task_123", description="Implementation work", duration=3600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "team_1",
                    "task_id": "task_123",
                    "description": "Implementation work",
                    "duration": 3600000,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "tsk_abc"])
    description: Optional[str] = Field(
        None, description="Description of the time entry.", examples=["Implementation work", "Bug fix"]
    )
    start: Optional[int] = Field(
        None, description="Start time in epoch ms.", examples=[1702080000000]
    )
    end: Optional[int] = Field(
        None, description="End time in epoch ms.", examples=[1702083600000]
    )
    duration: Optional[int] = Field(
        None, ge=0, description="Duration in milliseconds.", examples=[3600000, 7200000]
    )


class TimeEntryGetInput(BaseModel):
    """
    Get a time entry by ID. HTTP: GET /team/{team_id}/time_entries/{time_entry_id}

    When to use: Retrieve details of a specific time entry.

    Attributes:
        team_id: Team/workspace ID
        time_entry_id: Time entry ID

    Examples:
        TimeEntryGetInput(team_id="team_1", time_entry_id="entry_123")
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"team_id": "team_1", "time_entry_id": "entry_123"}]}
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    time_entry_id: str = Field(
        ..., min_length=1, description="Time entry ID.", examples=["entry_123", "ent_abc"]
    )


class TimeEntryUpdateInput(BaseModel):
    """
    Update a time entry. HTTP: PUT /team/{team_id}/time_entries/{time_entry_id}

    When to use: Modify time entry details like description, start, end, or duration.

    Constraints:
        - `duration` must be positive if provided
        - Time fields are epoch milliseconds

    Attributes:
        team_id: Team/workspace ID
        time_entry_id: Time entry ID
        description: New description
        start: New start time in epoch ms
        end: New end time in epoch ms
        duration: New duration in milliseconds

    Examples:
        TimeEntryUpdateInput(team_id="team_1", time_entry_id="entry_123", duration=7200000)
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"team_id": "team_1", "time_entry_id": "entry_123", "duration": 7200000}]}
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    time_entry_id: str = Field(
        ..., min_length=1, description="Time entry ID.", examples=["entry_123", "ent_abc"]
    )
    description: Optional[str] = Field(
        None, description="New description.", examples=["Updated description"]
    )
    start: Optional[int] = Field(
        None, description="New start time in epoch ms.", examples=[1702080000000]
    )
    end: Optional[int] = Field(
        None, description="New end time in epoch ms.", examples=[1702087200000]
    )
    duration: Optional[int] = Field(
        None, ge=0, description="New duration in milliseconds.", examples=[7200000]
    )


class TimeEntryDeleteInput(BaseModel):
    """
    Delete a time entry. HTTP: DELETE /team/{team_id}/time_entries/{time_entry_id}

    When to use: Remove a time entry permanently.

    Attributes:
        team_id: Team/workspace ID
        time_entry_id: Time entry ID

    Examples:
        TimeEntryDeleteInput(team_id="team_1", time_entry_id="entry_123")
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"team_id": "team_1", "time_entry_id": "entry_123"}]}
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    time_entry_id: str = Field(
        ..., min_length=1, description="Time entry ID.", examples=["entry_123", "ent_abc"]
    )


class TimeEntryListInput(BaseModel):
    """
    List time entries with filters. HTTP: GET /team/{team_id}/time_entries

    When to use: Retrieve time entries with optional filtering by task, user, date range.

    Constraints:
        - `limit` ≤ 100 per API

    Attributes:
        team_id: Team/workspace ID
        task_id: Filter by task ID
        assignee: Filter by user ID
        start_date: Filter by start date (epoch ms)
        end_date: Filter by end date (epoch ms)
        page: Page number (0-indexed)
        limit: Page size (cap 100)

    Examples:
        TimeEntryListInput(team_id="team_1", task_id="task_123", limit=50)
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"team_id": "team_1", "task_id": "task_123", "limit": 50}]}
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    task_id: Optional[str] = Field(
        None, description="Filter by task ID.", examples=["task_123", "tsk_abc"]
    )
    assignee: Optional[str] = Field(
        None, description="Filter by user ID.", examples=["user_123", "usr_abc"]
    )
    start_date: Optional[int] = Field(
        None, description="Filter by start date (epoch ms).", examples=[1702080000000]
    )
    end_date: Optional[int] = Field(
        None, description="Filter by end date (epoch ms).", examples=[1702166400000]
    )
    page: int = Field(0, ge=0, description="Page number (0-indexed).", examples=[0, 1, 2])
    limit: int = Field(100, ge=1, le=100, description="Page size (cap 100).", examples=[25, 50, 100])


class TimeTrackingGetInput(BaseModel):
    """
    Get time tracking status for a task. HTTP: GET /task/{task_id}/time_tracking

    When to use: Check if time tracking is currently active for a task.

    Attributes:
        task_id: Task ID

    Examples:
        TimeTrackingGetInput(task_id="task_123")
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"task_id": "task_123"}]}
    )

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "tsk_abc"])


class TimeTrackingStartInput(BaseModel):
    """
    Start time tracking for a task. HTTP: POST /task/{task_id}/time_tracking/start

    When to use: Begin tracking time on a task.

    Attributes:
        task_id: Task ID

    Examples:
        TimeTrackingStartInput(task_id="task_123")
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"task_id": "task_123"}]}
    )

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "tsk_abc"])


class TimeTrackingStopInput(BaseModel):
    """
    Stop time tracking for a task. HTTP: POST /task/{task_id}/time_tracking/stop

    When to use: End the current time tracking session on a task.

    Attributes:
        task_id: Task ID
        description: Optional description for the time entry

    Examples:
        TimeTrackingStopInput(task_id="task_123", description="Completed implementation")
    """

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"task_id": "task_123", "description": "Completed implementation"}]}
    )

    task_id: str = Field(..., min_length=1, description="Task ID.", examples=["task_123", "tsk_abc"])
    description: Optional[str] = Field(
        None, description="Description for the time entry.", examples=["Completed implementation"]
    )
