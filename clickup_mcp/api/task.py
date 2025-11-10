"""
Task API resource manager.

This module provides a resource manager for interacting with ClickUp Tasks.
It follows the Resource Manager pattern described in the project documentation.
"""

from typing import TYPE_CHECKING, Any, Optional

from clickup_mcp.models.dto.task import TaskCreate, TaskListQuery, TaskResp, TaskUpdate

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient


class TaskAPI:
    """Task API resource manager.

    This class provides methods for interacting with ClickUp Tasks through
    the ClickUp API. It follows the Resource Manager pattern, receiving
    a shared HTTP client instance and providing domain-specific methods.
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the TaskAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, list_id: str, task_create: TaskCreate) -> Optional[TaskResp]:
        """Create a new task.

        POST /list/{list_id}/task
        https://developer.clickup.com/reference/createtask

        Supports creating subtasks by specifying parent task ID.

        Args:
            list_id: The ID of the list
            task_create: TaskCreate DTO with task details

        Returns:
            TaskResp DTO representing the created task, or None if creation failed.
        """
        response = await self._client.post(f"/list/{list_id}/task", data=task_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TaskResp(**response.data)

    async def get(
        self, task_id: str, *, subtasks: bool | None = None, custom_task_ids: bool = False, team_id: str | None = None
    ) -> Optional[TaskResp]:
        """Get a task by ID.

        GET /task/{task_id}
        https://developer.clickup.com/reference/gettask

        Args:
            task_id: The ID of the task to retrieve
            subtasks: Whether to include subtasks (True/False/None for default)
            custom_task_ids: Whether using custom task IDs
            team_id: Team ID (required when using custom_task_ids=True)

        Returns:
            TaskResp DTO representing the task, or None if not found.
        """
        params: dict[str, Any] = {}

        if subtasks is not None:
            params["subtasks"] = str(subtasks).lower()

        if custom_task_ids:
            params["custom_task_ids"] = "true"
            if team_id:
                params["team_id"] = team_id

        response = await self._client.get(f"/task/{task_id}", params=params if params else None)

        if not response.success or response.status_code == 404:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TaskResp(**response.data)

    async def list_in_list(self, list_id: str, query: TaskListQuery) -> list[TaskResp]:
        """Get all tasks in a list with pagination and filtering.

        GET /list/{list_id}/task
        https://developer.clickup.com/reference/gettasks

        Supports pagination (max 100 per page) and TIML (Tasks in Multiple Lists).

        Args:
            list_id: The ID of the list
            query: TaskListQuery DTO with query parameters

        Returns:
            List of TaskResp DTOs representing tasks in the list.
        """
        all_tasks: list[TaskResp] = []
        page = query.page

        while True:
            # Create a copy of the query with current page
            current_query = TaskListQuery(
                page=page,
                limit=query.limit,
                include_closed=query.include_closed,
                include_timl=query.include_timl,
                statuses=query.statuses,
                assignees=query.assignees,
            )

            params = current_query.to_query()
            response = await self._client.get(f"/list/{list_id}/task", params=params)

            if not response.success or response.status_code != 200:
                break

            if response.data is None or not isinstance(response.data, dict):
                break

            tasks_data = response.data.get("tasks", [])
            if not isinstance(tasks_data, list) or len(tasks_data) == 0:
                break

            # Convert to TaskResp DTOs
            for task_data in tasks_data:
                all_tasks.append(TaskResp(**task_data))

            # Check if we have more pages
            if len(tasks_data) < current_query.limit:
                break

            page += 1

        return all_tasks

    async def update(self, task_id: str, task_update: TaskUpdate) -> Optional[TaskResp]:
        """Update a task.

        PUT /task/{task_id}
        https://developer.clickup.com/reference/updatetask

        Note: Custom fields cannot be updated via this endpoint.
        Use set_custom_field() instead.

        Args:
            task_id: The ID of the task to update
            task_update: TaskUpdate DTO with updated task details

        Returns:
            TaskResp DTO representing the updated task, or None if update failed.
        """
        response = await self._client.put(f"/task/{task_id}", data=task_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TaskResp(**response.data)

    async def set_custom_field(self, task_id: str, field_id: str, value: Any) -> bool:
        """Set a custom field value on a task.

        POST /task/{task_id}/field/{field_id}
        https://developer.clickup.com/reference/setcustomfieldvalue

        The request body is always {"value": ...} where value type depends on field type.

        Args:
            task_id: The ID of the task
            field_id: The ID of the custom field
            value: The value to set (type depends on field type)

        Returns:
            True if custom field was successfully set, False otherwise.
        """
        data = {"value": value}
        response = await self._client.post(f"/task/{task_id}/field/{field_id}", data=data)
        return response.success and response.status_code in (200, 204)

    async def clear_custom_field(self, task_id: str, field_id: str) -> bool:
        """Clear a custom field value on a task.

        DELETE /task/{task_id}/field/{field_id}

        Args:
            task_id: The ID of the task
            field_id: The ID of the custom field

        Returns:
            True if custom field was successfully cleared, False otherwise.
        """
        response = await self._client.delete(f"/task/{task_id}/field/{field_id}")
        return response.success and response.status_code in (200, 204)

    async def add_dependency(
        self, task_id: str, depends_on: str, dependency_type: str = "waiting_on"
    ) -> bool:
        """Add a dependency to a task.

        POST /task/{task_id}/dependency

        Args:
            task_id: The ID of the task
            depends_on: The ID of the task this task depends on
            dependency_type: Type of dependency (default: "waiting_on")

        Returns:
            True if dependency was successfully added, False otherwise.
        """
        data = {"depends_on": depends_on, "dependency_type": dependency_type}
        response = await self._client.post(f"/task/{task_id}/dependency", data=data)
        return response.success and response.status_code in (200, 204)

    async def delete(self, task_id: str) -> bool:
        """Delete a task.

        DELETE /task/{task_id}

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        response = await self._client.delete(f"/task/{task_id}")
        return response.success and response.status_code in (200, 204)
