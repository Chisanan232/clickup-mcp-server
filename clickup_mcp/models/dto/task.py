"""
Task DTOs for ClickUp API requests and responses.

These DTOs handle serialization/deserialization of Task data
for API interactions.
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class TaskCreate(BaseRequestDTO):
    """DTO for creating a new task.

    POST /list/{list_id}/task
    https://developer.clickup.com/reference/createtask

    Supports creating subtasks by specifying parent task ID.
    """

    name: str = Field(description="The name of the task")
    description: str | None = Field(default=None, description="Task description")
    status: str | None = Field(default=None, description="Task status")
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignees: List[int] = Field(default_factory=list, description="List of user IDs to assign")
    due_date: int | None = Field(default=None, description="Due date in milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    time_estimate: int | None = Field(default=None, description="Time estimate in milliseconds")
    parent: str | None = Field(default=None, description="Parent task ID for subtasks")
    custom_fields: List[Dict[str, Any]] = Field(default_factory=list, description="Custom field values")


class TaskUpdate(BaseRequestDTO):
    """DTO for updating an existing task.

    PUT /task/{task_id}
    https://developer.clickup.com/reference/updatetask

    Note: Custom fields cannot be updated via this endpoint.
    Use set_custom_field() instead.
    """

    name: str | None = Field(default=None, description="The name of the task")
    description: str | None = Field(default=None, description="Task description")
    status: str | None = Field(default=None, description="Task status")
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignees: List[int] | None = Field(default=None, description="List of user IDs to assign")
    due_date: int | None = Field(default=None, description="Due date in milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    time_estimate: int | None = Field(default=None, description="Time estimate in milliseconds")


class TaskListQuery(BaseRequestDTO):
    """DTO for querying tasks in a list.

    GET /list/{list_id}/task
    https://developer.clickup.com/reference/gettasks
    """

    page: int = Field(default=0, description="Page number (0-indexed)")
    limit: int = Field(default=100, description="Number of tasks per page (max 100)")
    include_closed: bool = Field(default=False, description="Include closed tasks")
    include_timl: bool = Field(default=False, description="Include tasks from other lists (TIML)")
    statuses: List[str] | None = Field(default=None, description="Filter by statuses")
    assignees: List[int] | None = Field(default=None, description="Filter by assignees")

    def to_query(self) -> dict[str, Any]:
        """Convert to query parameters for API request.

        Returns:
            Dictionary of query parameters with proper formatting.
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
    """DTO for task API responses.

    Represents a task returned from the ClickUp API.
    """

    id: str = Field(description="The unique identifier for the task")
    custom_id: str | None = Field(default=None, description="Custom task ID")
    name: str = Field(description="The name of the task")
    text_content: str | None = Field(default=None, description="Task description")
    description: str | None = Field(default=None, description="Task description (alternate field)")
    status: Dict[str, Any] | None = Field(default=None, description="Task status")
    orderindex: str | None = Field(default=None, description="Order index")
    date_created: str | None = Field(default=None, description="Creation timestamp")
    date_updated: str | None = Field(default=None, description="Last update timestamp")
    date_closed: str | None = Field(default=None, description="Closure timestamp")
    due_date: int | None = Field(default=None, description="Due date in milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    time_estimate: int | None = Field(default=None, description="Time estimate in milliseconds")
    time_spent: int | None = Field(default=None, description="Time spent in milliseconds")
    priority: Dict[str, Any] | None = Field(default=None, description="Priority information")
    points: int | None = Field(default=None, description="Story points")
    team_id: str | None = Field(default=None, description="Team ID")
    project_id: str | None = Field(default=None, description="Project ID")
    folder: Dict[str, Any] | None = Field(default=None, description="Folder information")
    list: Dict[str, Any] | None = Field(default=None, description="List information")
    space: Dict[str, Any] | None = Field(default=None, description="Space information")
    url: str | None = Field(default=None, description="Task URL")
    permission_level: str | None = Field(default=None, description="Permission level")
    tags: List[dict[str, Any]] = Field(default_factory=list, description="Tags")
    parent: str | None = Field(default=None, description="Parent task ID")
    priority_id: str | None = Field(default=None, description="Priority ID")
    watchers: List[Dict[str, Any]] = Field(default_factory=list, description="Watchers")
    assignees: List[Dict[str, Any]] = Field(default_factory=list, description="Assigned users")
    checklists: List[Dict[str, Any]] = Field(default_factory=list, description="Checklists")
    custom_fields: List[Dict[str, Any]] = Field(default_factory=list, description="Custom field values")
    dependencies: List[Dict[str, Any]] | None = Field(default=None, description="Task dependencies")
    subtasks: List[Dict[str, Any]] | None = Field(default=None, description="Subtasks")
