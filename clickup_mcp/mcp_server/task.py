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
    name="task.create",
    description=(
        "Create a task in a specific list; set `parent` to create a subtask in the same list. "
        "If you don’t know `list_id`, call `workspace.list` → `space.list` → `list.list_in_*` first. "
        "Constraints: `priority` 1..4; due/estimate are epoch ms. HTTP: POST /list/{list_id}/task. "
        "Note: Custom fields are set via `task.set_custom_field`, not `task.update`."
    ),
)
@handle_tool_errors
async def task_create(input: TaskCreateInput) -> TaskResult | None:
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
    name="task.get",
    description=(
        "Get a task by ID. For custom task IDs, set `custom_task_ids=true` and include `team_id`. "
        "HTTP: GET /task/{task_id}."
    ),
)
@handle_tool_errors
async def task_get(input: TaskGetInput) -> TaskResult | None:
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
    name="task.list_in_list",
    description=(
        "List tasks in a list with pagination and filters. Constraints: `limit` ≤ 100; set `include_timl` to include multi-list tasks. "
        "If you don’t know `list_id`, discover via `workspace.list` → `space.list` → `list.list_in_*`. "
        "HTTP: GET /list/{list_id}/task."
    ),
)
@handle_tool_errors
async def task_list_in_list(input: TaskListInListInput) -> TaskListResult:
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
    name="task.update",
    description=(
        "Update core task fields (name/status/priority/assignees/due/estimate). "
        "Does not modify custom fields—use `task.set_custom_field`. HTTP: PUT /task/{task_id}."
    ),
)
@handle_tool_errors
async def task_update(input: TaskUpdateInput) -> TaskResult | None:
    client = ClickUpAPIClientFactory.get()
    domain = TaskMapper.from_update_input(input)
    dto = TaskMapper.to_update_dto(domain)
    async with client:
        resp = await client.task.update(input.task_id, dto)
    if not resp:
        return None
    return _taskresp_to_result(resp)


@mcp.tool(
    name="task.set_custom_field",
    description=(
        'Set a single custom field value on a task. Body is always {"value": ...}. '
        "HTTP: POST /task/{task_id}/field/{field_id}."
    ),
)
@handle_tool_errors
async def task_set_custom_field(input: TaskSetCustomFieldInput) -> OperationResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.set_custom_field(input.task_id, input.field_id, input.value)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    name="task.clear_custom_field",
    description=("Clear a custom field value from a task. HTTP: DELETE /task/{task_id}/field/{field_id}."),
)
@handle_tool_errors
async def task_clear_custom_field(input: TaskClearCustomFieldInput) -> OperationResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.clear_custom_field(input.task_id, input.field_id)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    name="task.add_dependency",
    description=("Add a dependency between tasks (e.g., waiting_on/blocking). HTTP: POST /task/{task_id}/dependency."),
)
@handle_tool_errors
async def task_add_dependency(input: TaskAddDependencyInput) -> OperationResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.task.add_dependency(input.task_id, input.depends_on, input.dependency_type)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    name="task.delete",
    description=("Delete a task by ID. Irreversible and permission-scoped. HTTP: DELETE /task/{task_id}."),
)
@handle_tool_errors
async def task_delete(task_id: str) -> DeletionResult:
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
