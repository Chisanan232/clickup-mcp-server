"""MCP tools for ClickUp Time Entries and Time Tracking.

Tools:
- time_entry.create|get|update|delete
- time_entry.list
- time_tracking.start|stop|get_status
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError, ResourceNotFoundError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.time import (
    TimeEntryCreateInput,
    TimeEntryDeleteInput,
    TimeEntryGetInput,
    TimeEntryListInput,
    TimeEntryUpdateInput,
    TimeTrackingGetInput,
    TimeTrackingStartInput,
    TimeTrackingStopInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult, OperationResult
from clickup_mcp.mcp_server.models.outputs.time import (
    TimeEntryListResult,
    TimeEntryResult,
    TimeTrackingStatus,
)
from clickup_mcp.models.dto.time import TimeEntryListQuery
from clickup_mcp.models.mapping.time_mapper import TimeMapper

from .app import mcp


@mcp.tool(
    title="Create Time Entry",
    name="time_entry.create",
    description=(
        "Create a time entry for a task. Requires either duration or both start and end times. "
        "Time fields are epoch milliseconds. HTTP: POST /team/{team_id}/time_entries."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_entry_create(input: TimeEntryCreateInput) -> TimeEntryResult | None:
    """
    Create a time entry for a task.

    API:
        POST /team/{team_id}/time_entries

    Args:
        input: TimeEntryCreateInput with team_id, task_id, and optional description, start, end, duration

    Returns:
        TimeEntryResult | None: Created time entry projection, or None if creation failed

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await time_entry_create(TimeEntryCreateInput(team_id="team_1", task_id="task_123", duration=3600000))
        if response.ok and response.result:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO

    domain = TimeMapper.from_create_input(input)
    dto = TimeMapper.to_create_dto(domain)
    async with client:
        resp = await client.time.create(input.team_id, dto)
    if not resp:
        raise ClickUpAPIError("Create time entry failed")
    return TimeMapper.to_time_entry_result_output(TimeMapper.to_domain(resp))


@mcp.tool(
    title="Get Time Entry",
    name="time_entry.get",
    description=("Get a time entry by ID. HTTP: GET /team/{team_id}/time_entries/{time_entry_id}."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_entry_get(input: TimeEntryGetInput) -> TimeEntryResult | None:
    """
    Get a time entry by ID.

    API:
        GET /team/{team_id}/time_entries/{time_entry_id}

    Args:
        input: TimeEntryGetInput with team_id and time_entry_id

    Returns:
        TimeEntryResult | None: Time entry projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await time_entry_get(TimeEntryGetInput(team_id="team_1", time_entry_id="entry_123"))
        if response.ok and response.result:
            print(response.result.description)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.time.get(input.team_id, input.time_entry_id)
    if not resp:
        raise ResourceNotFoundError("Time entry not found")
    return TimeMapper.to_time_entry_result_output(TimeMapper.to_domain(resp))


@mcp.tool(
    title="List Time Entries",
    name="time_entry.list",
    description=(
        "List time entries with filters. Constraints: `limit` ≤ 100. " "HTTP: GET /team/{team_id}/time_entries."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_entry_list(input: TimeEntryListInput) -> TimeEntryListResult:
    """
    List time entries with filters.

    API:
        GET /team/{team_id}/time_entries

    Args:
        input: TimeEntryListInput with team_id, optional task_id, assignee, start_date, end_date, page, limit

    Returns:
        TimeEntryListResult: Page of time entry list items

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await time_entry_list(TimeEntryListInput(team_id="team_1", task_id="task_123", limit=50))
        if response.ok:
            for it in response.result.items:
                print(it.id, it.description)
    """
    client = ClickUpAPIClientFactory.get()
    query = TimeEntryListQuery(
        task_id=input.task_id,
        assignee=input.assignee,
        start_date=input.start_date,
        end_date=input.end_date,
        page=input.page,
        limit=input.limit,
    )
    async with client:
        resp = await client.time.list(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("List time entries failed")
    items = [TimeMapper.to_time_entry_list_item_output(TimeMapper.to_domain(entry)) for entry in resp.items]
    return TimeEntryListResult(items=items, next_cursor=resp.next_page, truncated=False)


@mcp.tool(
    title="Update Time Entry",
    name="time_entry.update",
    description=(
        "Update a time entry. Only include fields that need to be updated. "
        "HTTP: PUT /team/{team_id}/time_entries/{time_entry_id}."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_entry_update(input: TimeEntryUpdateInput) -> TimeEntryResult | None:
    """
    Update a time entry.

    API:
        PUT /team/{team_id}/time_entries/{time_entry_id}

    Args:
        input: TimeEntryUpdateInput with team_id, time_entry_id, and optional description, start, end, duration

    Returns:
        TimeEntryResult | None: Updated time entry projection, or None if update failed

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await time_entry_update(TimeEntryUpdateInput(team_id="team_1", time_entry_id="entry_123", duration=7200000))
        if response.ok and response.result:
            print(response.result.duration)
    """
    client = ClickUpAPIClientFactory.get()
    domain = TimeMapper.from_update_input(input)
    dto = TimeMapper.to_update_dto(domain)
    async with client:
        resp = await client.time.update(input.team_id, input.time_entry_id, dto)
    if not resp:
        raise ResourceNotFoundError("Time entry not found")
    return TimeMapper.to_time_entry_result_output(TimeMapper.to_domain(resp))


@mcp.tool(
    title="Delete Time Entry",
    name="time_entry.delete",
    description=("Delete a time entry permanently. HTTP: DELETE /team/{team_id}/time_entries/{time_entry_id}."),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_entry_delete(input: TimeEntryDeleteInput) -> DeletionResult:
    """
    Delete a time entry.

    API:
        DELETE /team/{team_id}/time_entries/{time_entry_id}

    Args:
        input: TimeEntryDeleteInput with team_id and time_entry_id

    Returns:
        DeletionResult: Operation result with success status

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await time_entry_delete(TimeEntryDeleteInput(team_id="team_1", time_entry_id="entry_123"))
        if response.ok:
            print("Deleted successfully")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        success = await client.time.delete(input.team_id, input.time_entry_id)
    if not success:
        raise ResourceNotFoundError("Time entry not found")
    return DeletionResult(success=True)


@mcp.tool(
    title="Start Time Tracking",
    name="time_tracking.start",
    description=("Start time tracking for a task. HTTP: POST /task/{task_id}/time_tracking/start."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_tracking_start(input: TimeTrackingStartInput) -> OperationResult:
    """
    Start time tracking for a task.

    API:
        POST /task/{task_id}/time_tracking/start

    Args:
        input: TimeTrackingStartInput with task_id

    Returns:
        OperationResult: Operation result with success status

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await time_tracking_start(TimeTrackingStartInput(task_id="task_123"))
        if response.ok:
            print("Tracking started")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        success = await client.time.start_tracking(input.task_id)
    if not success:
        raise ClickUpAPIError("Start time tracking failed")
    return OperationResult(success=True)


@mcp.tool(
    title="Stop Time Tracking",
    name="time_tracking.stop",
    description=(
        "Stop time tracking for a task. Optionally provide a description for the time entry. "
        "HTTP: POST /task/{task_id}/time_tracking/stop."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_tracking_stop(input: TimeTrackingStopInput) -> OperationResult:
    """
    Stop time tracking for a task.

    API:
        POST /task/{task_id}/time_tracking/stop

    Args:
        input: TimeTrackingStopInput with task_id and optional description

    Returns:
        OperationResult: Operation result with success status

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await time_tracking_stop(TimeTrackingStopInput(task_id="task_123", description="Completed work"))
        if response.ok:
            print("Tracking stopped")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        success = await client.time.stop_tracking(input.task_id, input.description)
    if not success:
        raise ClickUpAPIError("Stop time tracking failed")
    return OperationResult(success=True)


@mcp.tool(
    title="Get Time Tracking Status",
    name="time_tracking.get_status",
    description=("Get time tracking status for a task. HTTP: GET /task/{task_id}/time_tracking."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def time_tracking_get_status(input: TimeTrackingGetInput) -> TimeTrackingStatus:
    """
    Get time tracking status for a task.

    API:
        GET /task/{task_id}/time_tracking

    Args:
        input: TimeTrackingGetInput with task_id

    Returns:
        TimeTrackingStatus: Tracking status with active flag, start time, and task ID

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await time_tracking_get_status(TimeTrackingGetInput(task_id="task_123"))
        if response.ok:
            print(f"Active: {response.result.active}")
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.time.get_tracking_status(input.task_id)
    if not resp:
        raise ResourceNotFoundError("Task not found")
    return TimeTrackingStatus(
        active=resp.active,
        start=resp.start,
        task_id=resp.task_id,
    )
