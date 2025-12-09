"""
Task DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Task
operations, including create, update, and list queries. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create task payload
    from clickup_mcp.models.dto.task import TaskCreate

    payload = TaskCreate(
        name="Ship v1.2",
        description="Cut RC",
        priority=2,
        assignees=[12345],
    ).to_payload()
    # => {"name": "Ship v1.2", "description": "Cut RC", "priority": 2, "assignees": [12345]}

    # Python - Build task list query
    from clickup_mcp.models.dto.task import TaskListQuery

    query = TaskListQuery(limit=50, include_closed=False).to_query()
    # => {"page": 0, "limit": 50, "include_closed": "false", "include_timl": "false"}
"""

import builtins
from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO
from .common import EpochMs, Priority, TaskStatus, UserId
from .custom_fields import CustomField, cf_to_create_payload

PROPERTY_NAME_DESCRIPTION: str = "The name of the task"
PROPERTY_TASK_DESCRIPTION_DESCRIPTION: str = "Task description"
PROPERTY_STATUS_DESCRIPTION: str = "Task status"
PROPERTY_DUE_DATE_DESCRIPTION: str = "Due date in milliseconds"
PROPERTY_DUE_DATE_TIME_DESCRIPTION: str = "Whether due date includes time"
PROPERTY_TIME_ESTIMATE_DESCRIPTION: str = "Time estimate in milliseconds"


class TaskCreate(BaseRequestDTO):
    """
    DTO for creating a new task.

    API:
        POST /list/{list_id}/task
        Docs: https://developer.clickup.com/reference/createtask

    Notes:
        Supports creating subtasks by specifying a parent task ID.

    Attributes:
        name: Task name
        description: Optional description
        status: Initial task status (string or TaskStatus)
        priority: Priority level (1..4 or Priority enum)
        assignees: List of user IDs to assign
        due_date: Due timestamp in epoch ms
        due_date_time: Whether due date includes time
        time_estimate: Time estimate in milliseconds
        parent: Parent task ID for subtasks
        custom_fields: List of custom field values (either CF* DTOs or legacy {id,value} dicts)

    Examples:
        # Python - payload build with custom fields
        TaskCreate(
            name="Ship v1.2",
            priority=2,
            assignees=[123],
            custom_fields=[{"id": "fld_text", "value": "hello"}],
        ).to_payload()
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    description: str | None = Field(default=None, description=PROPERTY_TASK_DESCRIPTION_DESCRIPTION)
    status: TaskStatus | str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)
    priority: Priority | int | None = Field(default=None, description="Priority level (1-4)")
    assignees: List[UserId] = Field(default_factory=list, description="List of user IDs to assign")
    due_date: EpochMs | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    time_estimate: EpochMs | None = Field(default=None, description=PROPERTY_TIME_ESTIMATE_DESCRIPTION)
    parent: str | None = Field(default=None, description="Parent task ID for subtasks")
    # Backward compatible: allow either CustomField union instances or legacy {id,value} dicts
    custom_fields: List[CustomField | Dict[str, Any]] = Field(default_factory=list, description="Custom field values")

    def to_payload(self) -> dict[str, Any]:
        """
        Convert the DTO into a ClickUp create-task request body.

        Returns:
            dict[str, Any]: JSON-serializable payload with None values removed. Custom fields
            are normalized to a list of {"id", "value"} dicts.

        Examples:
            TaskCreate(name="X", custom_fields=[{"id": "fld", "value": 1}]).to_payload()
        """
        payload = super().to_payload()
        # Map CustomField union or legacy dicts to list of {id, value}
        if "custom_fields" in payload and self.custom_fields:
            mapped: list[dict[str, Any]] = []
            for cf in self.custom_fields:
                if isinstance(cf, dict):
                    # assume already in correct shape
                    if "id" in cf and "value" in cf:
                        mapped.append({"id": cf["id"], "value": cf["value"]})
                else:
                    mapped.append(cf_to_create_payload(cf))
            payload["custom_fields"] = mapped
        return payload


class TaskUpdate(BaseRequestDTO):
    """
    DTO for updating an existing task.

    API:
        PUT /task/{task_id}
        Docs: https://developer.clickup.com/reference/updatetask

    Notes:
        Custom fields cannot be updated via this endpoint; use `task.set_custom_field`.

    Attributes:
        name: New task name
        description: New description
        status: New status
        priority: New priority (1..4 or Priority)
        assignees: New list of assignee IDs (replaces existing)
        due_date: New due date (epoch ms)
        due_date_time: Whether due date includes time
        time_estimate: New time estimate in ms
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    description: str | None = Field(default=None, description=PROPERTY_TASK_DESCRIPTION_DESCRIPTION)
    status: TaskStatus | str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)
    priority: Priority | int | None = Field(default=None, description="Priority level (1-4)")
    assignees: List[UserId] | None = Field(default=None, description="List of user IDs to assign")
    due_date: EpochMs | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    time_estimate: EpochMs | None = Field(default=None, description=PROPERTY_TIME_ESTIMATE_DESCRIPTION)


class TaskListQuery(BaseRequestDTO):
    """
    DTO for querying tasks in a list.

    API:
        GET /list/{list_id}/task
        Docs: https://developer.clickup.com/reference/gettasks

    Attributes:
        page: Page number (0-indexed)
        limit: Page size (max 100)
        include_closed: Whether to include closed tasks
        include_timl: Include tasks in multiple lists (TIML)
        statuses: Optional status filters
        assignees: Optional assignee filters
    """

    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Number of tasks per page (max 100)")
    include_closed: bool = Field(default=False, description="Include closed tasks")
    include_timl: bool = Field(default=False, description="Include tasks from other lists (TIML)")
    statuses: List[TaskStatus | str] | None = Field(default=None, description="Filter by statuses")
    assignees: List[UserId] | None = Field(default=None, description="Filter by assignees")

    def to_query(self) -> dict[str, Any]:
        """
        Convert to query parameters for API request.

        Returns:
            dict[str, Any]: Query parameters with booleans normalized to lowercase strings and
            `limit` capped at 100.

        Examples:
            TaskListQuery(limit=150, include_closed=True).to_query()
            # {"page": 0, "limit": 100, "include_closed": "true", "include_timl": "false"}
        """
        query = {
            "page": self.page,
            "limit": min(self.limit, 100),  # Cap at 100
            "include_closed": str(self.include_closed).lower(),
            "include_timl": str(self.include_timl).lower(),
        }

        if self.statuses:
            query["statuses"] = self.statuses

        if self.assignees:
            query["assignees"] = self.assignees

        return query


class TaskResp(BaseResponseDTO):
    """
    DTO for task API responses.

    Represents a task returned from the ClickUp API with typed substructures for
    status, priority, entity references, tags, users, checklists, custom fields, and dependencies.

    Attributes:
        id: Task ID
        custom_id: Custom task ID (if enabled)
        name: Task name
        text_content: Text-only content
        description: Rich description
        status: Status info (id/name/type/color)
        orderindex: Order index string
        date_created: Creation timestamp (string)
        date_updated: Last update timestamp (string)
        date_closed: Closure timestamp (string)
        due_date: Due epoch ms
        due_date_time: Whether due date includes time
        time_estimate: Time estimate in ms
        time_spent: Time spent in ms
        priority: Priority info
        points: Story points
        team_id: Workspace/team id
        project_id: Project id (if present)
        folder: Folder reference
        list: List reference
        space: Space reference
        url: Canonical task URL
        permission_level: User's permission level
        tags: Task tags
        parent: Parent task ID (for subtasks)
        priority_id: Raw priority id
        watchers: User refs watching the task
        assignees: Assigned users
        checklists: Checklist summaries
        custom_fields: Custom field value summaries
        dependencies: Task dependencies
        subtasks: Subtask summaries

    Examples:
        # Python - Deserialize from API JSON
        TaskResp.deserialize({"id": "t1", "name": "Ship"})
    """

    id: str = Field(description="The unique identifier for the task")
    custom_id: str | None = Field(default=None, description="Custom task ID")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    text_content: str | None = Field(default=None, description=PROPERTY_TASK_DESCRIPTION_DESCRIPTION)
    description: str | None = Field(default=None, description="Task description (alternate field)")

    # Typed status/priority entries while allowing extra fields
    class TaskStatusInfo(BaseResponseDTO):
        id: str | None = Field(default=None)
        status: str | None = Field(default=None)
        type: str | None = Field(default=None)
        color: str | None = Field(default=None)
        orderindex: int | str | None = Field(default=None)

    class TaskPriorityInfo(BaseResponseDTO):
        id: str | None = Field(default=None)
        priority: str | None = Field(default=None)
        color: str | None = Field(default=None)

    status: TaskStatusInfo | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)
    orderindex: str | None = Field(default=None, description="Order index")
    date_created: str | None = Field(default=None, description="Creation timestamp")
    date_updated: str | None = Field(default=None, description="Last update timestamp")
    date_closed: str | None = Field(default=None, description="Closure timestamp")
    due_date: int | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    time_estimate: int | None = Field(default=None, description=PROPERTY_TIME_ESTIMATE_DESCRIPTION)
    time_spent: int | None = Field(default=None, description="Time spent in milliseconds")
    priority: TaskPriorityInfo | None = Field(default=None, description="Priority information")
    points: int | None = Field(default=None, description="Story points")
    team_id: str | None = Field(default=None, description="Team ID")
    project_id: str | None = Field(default=None, description="Project ID")

    class EntityRef(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)

    folder: EntityRef | None = Field(default=None, description="Folder information")
    list: EntityRef | None = Field(default=None, description="List information")
    space: EntityRef | None = Field(default=None, description="Space information")
    url: str | None = Field(default=None, description="Task URL")
    permission_level: str | None = Field(default=None, description="Permission level")

    class TaskTag(BaseResponseDTO):
        name: str | None = Field(default=None)
        tag_fg: str | None = Field(default=None)
        tag_bg: str | None = Field(default=None)

    tags: List[TaskTag] = Field(default_factory=builtins.list, description="Tags")
    parent: str | None = Field(default=None, description="Parent task ID")
    priority_id: str | None = Field(default=None, description="Priority ID")

    class UserRef(BaseResponseDTO):
        id: int | str | None = Field(default=None)
        username: str | None = Field(default=None)

    watchers: List[UserRef] = Field(default_factory=builtins.list, description="Watchers")
    assignees: List[UserRef] = Field(default_factory=builtins.list, description="Assigned users")

    class ChecklistSummary(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)
        resolved: bool | None = Field(default=None)

    checklists: List[ChecklistSummary] = Field(default_factory=builtins.list, description="Checklists")

    # More descriptive shapes for remaining collections while allowing extras
    class CustomFieldValueResp(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)
        type: str | None = Field(default=None)
        value: Any | None = Field(default=None)

    class TaskDependency(BaseResponseDTO):
        task_id: str | None = Field(default=None)
        depends_on: str | None = Field(default=None)
        dependency_type: str | None = Field(default=None)
        type: int | None = Field(default=None)
        date_created: EpochMs | None = Field(default=None)
        userid: str | None = Field(default=None)
        workspace_id: str | None = Field(default=None)
        chain_id: str | None = Field(default=None)

    class SubtaskSummary(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)

    custom_fields: List[CustomFieldValueResp] = Field(default_factory=builtins.list, description="Custom field values")
    dependencies: List[TaskDependency] | None = Field(default=None, description="Task dependencies")
    subtasks: List[SubtaskSummary] | None = Field(default=None, description="Subtasks")
