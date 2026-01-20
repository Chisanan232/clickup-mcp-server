"""
Task API resource manager.

This module provides a resource manager for interacting with ClickUp Tasks.
It follows the Resource Manager pattern described in the project documentation.

Capabilities:
- Create tasks in a list (including subtasks)
- Retrieve task by ID (with options for subtasks and custom task IDs)
- List tasks in a list with pagination and filters
- Update task properties (non-custom-fields)
- Set or clear custom field values
- Add dependencies between tasks
- Delete tasks

Authentication:
- All requests require the ClickUp API token in the `Authorization` header: `Authorization: pk_...`

Quick Examples:
    # Python (async)
    from clickup_mcp.client import ClickUpAPIClient
    from clickup_mcp.models.dto.task import TaskCreate

    async with ClickUpAPIClient(api_token="pk_...") as client:
        task_api = client.task
        task = await task_api.create(
            list_id="123",
            task_create=TaskCreate(name="My Task", description="Demo")
        )

    # curl - Get a task
    # GET /task/{task_id}
    curl -H "Authorization: pk_..." \
         https://api.clickup.com/api/v2/task/abc123

    # wget - List tasks in a list
    # GET /list/{list_id}/task?limit=10&page=0
    wget --header="Authorization: pk_..." \
         "https://api.clickup.com/api/v2/list/123/task?limit=10&page=0"
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from clickup_mcp.models.dto.task import TaskCreate, TaskListQuery, TaskResp, TaskUpdate
from clickup_mcp.types import ClickUpListID, ClickUpTaskID

if TYPE_CHECKING:
    from clickup_mcp.client import ClickUpAPIClient

logger = logging.getLogger(__name__)


class TaskAPI:
    """
    Task API resource manager.

    Provides domain-specific methods to interact with ClickUp Tasks using a shared
    HTTP client. Methods return DTOs (e.g., `TaskResp`) or booleans for write ops.

    Usage Examples:
        # Python (async) - Initialize
        from clickup_mcp.client import ClickUpAPIClient
        from clickup_mcp.models.dto.task import TaskCreate

        async with ClickUpAPIClient(api_token="pk_...") as client:
            task_api = client.task
            # Create
            created = await task_api.create("123", TaskCreate(name="My Task"))
            # Get
            fetched = await task_api.get("abc123", subtasks=True)
            # List
            from clickup_mcp.models.dto.task import TaskListQuery
            tasks = await task_api.list_in_list("123", TaskListQuery(limit=10))
            # Update
            from clickup_mcp.models.dto.task import TaskUpdate
            updated = await task_api.update("abc123", TaskUpdate(name="New Name"))
            # Custom field
            ok = await task_api.set_custom_field("abc123", "fld_1", "value")
            # Dependency
            ok = await task_api.add_dependency("abc123", depends_on="xyz789")
            # Delete
            ok = await task_api.delete("abc123")
    """

    def __init__(self, client: "ClickUpAPIClient"):
        """Initialize the TaskAPI.

        Args:
            client: The ClickUpAPIClient instance to use for API requests.
        """
        self._client = client

    async def create(self, list_id: ClickUpListID, task_create: TaskCreate) -> Optional[TaskResp]:
        """
        Create a new task in a list (supports subtasks).

        API:
            POST /list/{list_id}/task
            Docs: https://developer.clickup.com/reference/createtask

        Notes:
            - Supports creating subtasks by specifying a parent task ID in the DTO.
            - Returns None on non-200 responses or unexpected payloads.

        Args:
            list_id: The ID of the list to create the task in
            task_create: TaskCreate DTO with task details

        Returns:
            TaskResp | None: The created task, or None if creation failed

        Examples:
            # Python (async)
            created = await task_api.create("123", TaskCreate(name="My Task"))

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"My Task","description":"Demo"}' \
              https://api.clickup.com/api/v2/list/123/task

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"My Task"}' \
              https://api.clickup.com/api/v2/list/123/task
        """
        response = await self._client.post(f"/list/{list_id}/task", data=task_create.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TaskResp(**response.data)

    async def get(
        self,
        task_id: ClickUpTaskID,
        *,
        subtasks: bool | None = None,
        custom_task_ids: bool = False,
        team_id: str | None = None,
    ) -> Optional[TaskResp]:
        """
        Get a task by ID.

        API:
            GET /task/{task_id}
            Docs: https://developer.clickup.com/reference/gettask

        Args:
            task_id: The ID of the task to retrieve
            subtasks: Whether to include subtasks (True/False/None for default)
            custom_task_ids: Whether using custom task IDs
            team_id: Team ID (required when using custom_task_ids=True)

        Returns:
            TaskResp | None: The task if found, otherwise None

        Examples:
            # Python (async)
            task = await task_api.get("abc123", subtasks=True)

            # curl
            curl -H "Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/task/abc123?subtasks=true"

            # wget
            wget --header="Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/task/abc123?subtasks=true"
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

        logger.debug(f"Task API response: {response.data}")
        return TaskResp(**response.data)

    async def list_in_list(self, list_id: str, query: TaskListQuery) -> list[TaskResp]:
        """
        Get all tasks in a list with pagination and filtering.

        API:
            GET /list/{list_id}/task
            Docs: https://developer.clickup.com/reference/gettasks

        Supports pagination (max 100 per page) and TIML (Tasks in Multiple Lists).

        Args:
            list_id: The ID of the list
            query: TaskListQuery DTO with query parameters

        Returns:
            list[TaskResp]: Tasks in the list (aggregated across pages)

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.task import TaskListQuery
            tasks = await task_api.list_in_list("123", TaskListQuery(limit=10, page=0))

            # curl
            curl -H "Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/list/123/task?limit=10&page=0"

            # wget
            wget --header="Authorization: pk_..." \
                 "https://api.clickup.com/api/v2/list/123/task?limit=10&page=0"
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

            logger.debug(f"List task API response: {response.data}")
            # Convert to TaskResp DTOs
            for task_data in tasks_data:
                all_tasks.append(TaskResp(**task_data))

            # Check if we have more pages
            if len(tasks_data) < current_query.limit:
                break

            page += 1

        return all_tasks

    async def update(self, task_id: ClickUpTaskID, task_update: TaskUpdate) -> Optional[TaskResp]:
        """
        Update a task's properties (non-custom-fields).

        API:
            PUT /task/{task_id}
            Docs: https://developer.clickup.com/reference/updatetask

        Notes:
            - Custom fields cannot be updated via this endpoint. Use `set_custom_field()`.
            - Returns None on non-200 responses or unexpected payloads.

        Args:
            task_id: The ID of the task to update
            task_update: TaskUpdate DTO with updated task details

        Returns:
            TaskResp | None: The updated task, or None if update failed

        Examples:
            # Python (async)
            from clickup_mcp.models.dto.task import TaskUpdate
            updated = await task_api.update("abc123", TaskUpdate(name="New Name"))

            # curl
            curl -X PUT \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"name":"New Name"}' \
              https://api.clickup.com/api/v2/task/abc123

            # wget
            wget --method=PUT \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"name":"New Name"}' \
              https://api.clickup.com/api/v2/task/abc123
        """
        response = await self._client.put(f"/task/{task_id}", data=task_update.serialize())

        if not response.success or response.status_code != 200:
            return None

        if response.data is None or not isinstance(response.data, dict):
            return None

        return TaskResp(**response.data)

    async def set_custom_field(self, task_id: str, field_id: str, value: Any) -> bool:
        """
        Set a custom field value on a task.

        API:
            POST /task/{task_id}/field/{field_id}
            Docs: https://developer.clickup.com/reference/setcustomfieldvalue

        Notes:
            The request body is always {"value": ...}; the value type depends on field type.

        Args:
            task_id: The ID of the task
            field_id: The ID of the custom field
            value: The value to set (type depends on field type)

        Returns:
            bool: True if custom field was successfully set, otherwise False

        Examples:
            # Python (async)
            ok = await task_api.set_custom_field("abc123", "fld_1", 42)

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"value": 42}' \
              https://api.clickup.com/api/v2/task/abc123/field/fld_1

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"value": 42}' \
              https://api.clickup.com/api/v2/task/abc123/field/fld_1
        """
        data = {"value": value}
        response = await self._client.post(f"/task/{task_id}/field/{field_id}", data=data)
        return response.success and response.status_code in (200, 204)

    async def clear_custom_field(self, task_id: str, field_id: str) -> bool:
        """
        Clear a custom field value on a task.

        API:
            DELETE /task/{task_id}/field/{field_id}

        Args:
            task_id: The ID of the task
            field_id: The ID of the custom field

        Returns:
            bool: True if the field was cleared, otherwise False

        Examples:
            # Python (async)
            ok = await task_api.clear_custom_field("abc123", "fld_1")

            # curl
            curl -X DELETE -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/task/abc123/field/fld_1

            # wget
            wget --method=DELETE \
              --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/task/abc123/field/fld_1
        """
        response = await self._client.delete(f"/task/{task_id}/field/{field_id}")
        return response.success and response.status_code in (200, 204)

    async def add_dependency(self, task_id: str, depends_on: str, dependency_type: str = "waiting_on") -> bool:
        """
        Add a dependency to a task.

        API:
            POST /task/{task_id}/dependency

        Args:
            task_id: The ID of the task
            depends_on: The ID of the task this task depends on
            dependency_type: Type of dependency (default: "waiting_on")

        Returns:
            bool: True if dependency was successfully added, otherwise False

        Examples:
            # Python (async)
            ok = await task_api.add_dependency("abc123", depends_on="xyz789")

            # curl
            curl -X POST \
              -H "Authorization: pk_..." \
              -H "Content-Type: application/json" \
              -d '{"depends_on":"xyz789","dependency_type":"waiting_on"}' \
              https://api.clickup.com/api/v2/task/abc123/dependency

            # wget
            wget --method=POST \
              --header="Authorization: pk_..." \
              --header="Content-Type: application/json" \
              --body-data='{"depends_on":"xyz789","dependency_type":"waiting_on"}' \
              https://api.clickup.com/api/v2/task/abc123/dependency
        """
        data = {"depends_on": depends_on, "dependency_type": dependency_type}
        response = await self._client.post(f"/task/{task_id}/dependency", data=data)
        return response.success and response.status_code in (200, 204)

    async def delete(self, task_id: ClickUpTaskID) -> bool:
        """
        Delete a task.

        API:
            DELETE /task/{task_id}

        Args:
            task_id: The ID of the task to delete

        Returns:
            bool: True if deletion was successful, otherwise False

        Examples:
            # Python (async)
            ok = await task_api.delete("abc123")

            # curl
            curl -X DELETE -H "Authorization: pk_..." \
              https://api.clickup.com/api/v2/task/abc123

            # wget
            wget --method=DELETE \
              --header="Authorization: pk_..." \
              https://api.clickup.com/api/v2/task/abc123
        """
        response = await self._client.delete(f"/task/{task_id}")
        return response.success and response.status_code in (200, 204)
