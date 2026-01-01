"""MCP tools for ClickUp Tasks and Subtasks.

Tools:
- task.create|get|update|delete
- task.list_in_list
- task.set_custom_field / task.clear_custom_field
- task.add_dependency
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError, ResourceNotFoundError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.task import (
    TaskAddDependencyInput,
    TaskClearCustomFieldInput,
    TaskCreateInput,
    TaskGetInput,
    TaskListInListInput,
    TaskSetCustomFieldInput,
    TaskUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult, OperationResult
from clickup_mcp.mcp_server.models.outputs.task import (
    TaskListItem,
    TaskListResult,
    TaskResult,
)
from clickup_mcp.models.dto.task import TaskListQuery, TaskResp
from clickup_mcp.models.mapping.task_mapper import TaskMapper

from .app import mcp


@mcp.tool(
    title="Create Task",
    name="task.create",
    description=(
        "Create a task in a specific list; set `parent` to create a subtask in the same list. "
        "If you don’t know `list_id`, call `workspace.list` → `space.list` → `list.list_in_*` first. "
        "Constraints: `priority` 1..4; due/estimate are epoch ms. HTTP: POST /list/{list_id}/task. "
        "Note: Custom fields are set via `task.set_custom_field`, not `task.update`."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_create(input: TaskCreateInput) -> TaskResult | None:
    """
    Create a task in a list; set `parent` to create a subtask.

    API:
        POST /list/{list_id}/task

    Args:
        input: TaskCreateInput with `list_id` and fields (name, status, priority, assignees, parent,
            due_date_ms, estimate_ms, etc.)

    Returns:
        TaskResult | None: Created task projection, or None if creation failed

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await task_create(TaskCreateInput(list_id="L1", name="Ship v1.2"))
        if response.ok and response.result:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO

    domain = TaskMapper.from_create_input(input)
    dto = TaskMapper.to_create_dto(domain)
    async with client:
        resp = await client.task.create(input.list_id, dto)
    if not resp:
        raise ClickUpAPIError("Create task failed")
    return _taskresp_to_result(resp)


@mcp.tool(
    title="Get Task",
    name="task.get",
    description=(
        "Get a task by ID. For custom task IDs, set `custom_task_ids=true` and include `team_id`. "
        "HTTP: GET /task/{task_id}."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_get(input: TaskGetInput) -> TaskResult | None:
    """
    Get a task by ID.

    API:
        GET /task/{task_id}

    Args:
        input: TaskGetInput with `task_id`. For custom task IDs, set `custom_task_ids=true` and provide `team_id`.
            Use `subtasks=true` to include subtasks.

    Returns:
        TaskResult | None: Task projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await task_get(TaskGetInput(task_id="tsk_1"))
        if response.ok and response.result:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.task.get(
            input.task_id,
            subtasks=input.subtasks,
            custom_task_ids=input.custom_task_ids,
            team_id=input.team_id,
        )
    if not resp:
        raise ResourceNotFoundError("Task not found")
    return _taskresp_to_result(resp)


@mcp.tool(
    title="List Tasks in List",
    name="task.list_in_list",
    description=(
        "List tasks in a list with pagination and filters. Constraints: `limit` ≤ 100; set `include_timl` to include multi-list tasks. "
        "If you don’t know `list_id`, discover via `workspace.list` → `space.list` → `list.list_in_*`. "
        "HTTP: GET /list/{list_id}/task."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_list_in_list(input: TaskListInListInput) -> TaskListResult:
    """
    List tasks in a list with pagination and filters.

    API:
        GET /list/{list_id}/task

    Args:
        input: TaskListInListInput with `list_id`, `page`, `limit` (≤100), `statuses`, `assignees`,
            `include_closed`, and `include_timl` (multi-list tasks)

    Returns:
        TaskListResult: Page of task list items; `truncated=True` when results exceed `limit`

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await task_list_in_list(TaskListInListInput(list_id="L1", page=0, limit=50))
        if response.ok:
            for it in response.result.items:
                print(it.id, it.name)
    """
    client = ClickUpAPIClientFactory.get()
    query = TaskListQuery(
        page=input.page,
        limit=input.limit,
        include_closed=input.include_closed,
        include_timl=input.include_timl,
        statuses=input.statuses,
        assignees=input.assignees,
    )
    async with client:
        tasks = await client.task.list_in_list(input.list_id, query)
    # Cap to requested page size. Our client currently fetches all pages, so we
    # cannot reliably expose a server-side cursor; we mark truncated when we trim.
    page_items = tasks[: input.limit]
    items = [_taskresp_to_list_item(t) for t in page_items]
    truncated = len(tasks) > len(page_items)
    return TaskListResult(items=items, next_cursor=None, truncated=truncated)


@mcp.tool(
    title="Update Task",
    name="task.update",
    description=(
        "Update core task fields (name/status/priority/assignees/due/estimate). "
        "Does not modify custom fields—use `task.set_custom_field`. HTTP: PUT /task/{task_id}."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_update(input: TaskUpdateInput) -> TaskResult | None:
    """
    Update core task fields (name/status/priority/assignees/due/estimate).

    API:
        PUT /task/{task_id}

    Notes:
        Does not modify custom fields—use `task.set_custom_field`.

    Args:
        input: TaskUpdateInput with `task_id` and fields to update

    Returns:
        TaskResult | None: Updated task projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, VALIDATION_ERROR, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await task_update(TaskUpdateInput(task_id="tsk_1", status="in progress"))
        if response.ok and response.result:
            print(response.result.status)
    """
    client = ClickUpAPIClientFactory.get()
    domain = TaskMapper.from_update_input(input)
    dto = TaskMapper.to_update_dto(domain)
    async with client:
        resp = await client.task.update(input.task_id, dto)
    if not resp:
        return None
    return _taskresp_to_result(resp)


@mcp.tool(
    title="Set Custom Field",
    name="task.set_custom_field",
    description=(
        'Set a single custom field value on a task. Body is always {"value": ...}. '
        "HTTP: POST /task/{task_id}/field/{field_id}."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_set_custom_field(input: TaskSetCustomFieldInput) -> OperationResult:
    """
    Set a single custom field value on a task.

    API:
        POST /task/{task_id}/field/{field_id}

    Args:
        input: TaskSetCustomFieldInput with `task_id`, `field_id`, and `value`

    Returns:
        OperationResult: `ok=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await task_set_custom_field(TaskSetCustomFieldInput(task_id="tsk_1", field_id="fld_1", value={"value": "X"}))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.set_custom_field(input.task_id, input.field_id, input.value)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    title="Clear Custom Field",
    name="task.clear_custom_field",
    description=("Clear a custom field value from a task. HTTP: DELETE /task/{task_id}/field/{field_id}."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_clear_custom_field(input: TaskClearCustomFieldInput) -> OperationResult:
    """
    Clear a custom field value from a task.

    API:
        DELETE /task/{task_id}/field/{field_id}

    Args:
        input: TaskClearCustomFieldInput with `task_id` and `field_id`

    Returns:
        OperationResult: `ok=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await task_clear_custom_field(TaskClearCustomFieldInput(task_id="tsk_1", field_id="fld_1"))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.clear_custom_field(input.task_id, input.field_id)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    title="Add Task Dependency",
    name="task.add_dependency",
    description=("Add a dependency between tasks (e.g., waiting_on/blocking). HTTP: POST /task/{task_id}/dependency."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_add_dependency(input: TaskAddDependencyInput) -> OperationResult:
    """
    Add a dependency between tasks (e.g., waiting_on or blocking).

    API:
        POST /task/{task_id}/dependency

    Args:
        input: TaskAddDependencyInput with `task_id`, `depends_on`, and `dependency_type`

    Returns:
        OperationResult: `ok=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await task_add_dependency(TaskAddDependencyInput(task_id="tsk_1", depends_on="tsk_0", dependency_type="waiting_on"))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.add_dependency(input.task_id, input.depends_on, input.dependency_type)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    title="Delete Task",
    name="task.delete",
    description=("Delete a task by ID. Irreversible and permission-scoped. HTTP: DELETE /task/{task_id}."),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def task_delete(task_id: str) -> DeletionResult:
    """
    Delete a task by ID.

    API:
        DELETE /task/{task_id}

    Args:
        task_id: The ID of the task to delete

    Returns:
        DeletionResult: `deleted=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await task_delete("tsk_1")
        print(response.ok)
    """
    if not task_id:
        raise ValueError("Task ID is required")
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.delete(task_id)
    return DeletionResult(deleted=bool(ok))


def _taskresp_to_result(resp: TaskResp) -> TaskResult:
    # DTO -> Domain
    dom = TaskMapper.to_domain(resp)
    # Domain -> Output (pass url from DTO)
    return TaskMapper.to_task_result_output(dom, url=resp.url)


def _taskresp_to_list_item(resp: TaskResp) -> TaskListItem:
    dom = TaskMapper.to_domain(resp)
    return TaskMapper.to_task_list_item_output(dom, url=resp.url)
