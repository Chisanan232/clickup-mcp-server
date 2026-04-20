"""MCP tools for ClickUp Analytics.

Tools:
- analytics.get_task_analytics
- analytics.get_team_analytics
- analytics.get_list_analytics
- analytics.get_space_analytics
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.analytics import (
    ListAnalyticsInput,
    SpaceAnalyticsInput,
    TaskAnalyticsInput,
    TeamAnalyticsInput,
)
from clickup_mcp.mcp_server.models.outputs.analytics import (
    ListAnalyticsResult,
    SpaceAnalyticsResult,
    TaskAnalyticsResult,
    TeamAnalyticsResult,
)
from clickup_mcp.models.dto.analytics import (
    ListAnalyticsQuery,
    SpaceAnalyticsQuery,
    TaskAnalyticsQuery,
    TeamAnalyticsQuery,
)
from clickup_mcp.models.mapping.analytics_mapper import AnalyticsMapper

from .app import mcp


@mcp.tool(
    title="Get Task Analytics",
    name="analytics.get_task_analytics",
    description=(
        "Get task analytics for a team with date range and optional filters. "
        "HTTP: GET /team/{team_id}/analytics/task."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def analytics_get_task_analytics(input: TaskAnalyticsInput) -> TaskAnalyticsResult:
    """
    Get task analytics for a team.

    API:
        GET /team/{team_id}/analytics/task

    Args:
        input: TaskAnalyticsInput with team_id, start_date, end_date, and optional assignee_id, status, limit

    Returns:
        TaskAnalyticsResult: The task analytics data

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await analytics_get_task_analytics(
            TaskAnalyticsInput(team_id="team_1", start_date=1640995200000, end_date=1643673600000)
        )
        if response.ok:
            print(response.result.total_tasks)
    """
    client = ClickUpAPIClientFactory.get()
    query = TaskAnalyticsQuery(
        start_date=input.start_date,
        end_date=input.end_date,
        assignee_id=input.assignee_id,
        status=input.status,
        limit=input.limit,
    )
    async with client:
        resp = await client.analytics.get_task_analytics(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("Get task analytics failed")
    domain = AnalyticsMapper.task_analytics_to_domain(resp)
    return TaskAnalyticsResult(**AnalyticsMapper.task_analytics_to_output(domain))


@mcp.tool(
    title="Get Team Analytics",
    name="analytics.get_team_analytics",
    description=(
        "Get team analytics with date range. HTTP: GET /team/{team_id}/analytics/team."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def analytics_get_team_analytics(input: TeamAnalyticsInput) -> TeamAnalyticsResult:
    """
    Get team analytics.

    API:
        GET /team/{team_id}/analytics/team

    Args:
        input: TeamAnalyticsInput with team_id, start_date, end_date

    Returns:
        TeamAnalyticsResult: The team analytics data

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await analytics_get_team_analytics(
            TeamAnalyticsInput(team_id="team_1", start_date=1640995200000, end_date=1643673600000)
        )
        if response.ok:
            print(response.result.total_tasks)
    """
    client = ClickUpAPIClientFactory.get()
    query = TeamAnalyticsQuery(start_date=input.start_date, end_date=input.end_date)
    async with client:
        resp = await client.analytics.get_team_analytics(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("Get team analytics failed")
    domain = AnalyticsMapper.team_analytics_to_domain(resp)
    return TeamAnalyticsResult(**AnalyticsMapper.team_analytics_to_output(domain))


@mcp.tool(
    title="Get List Analytics",
    name="analytics.get_list_analytics",
    description=(
        "Get list analytics with date range. HTTP: GET /list/{list_id}/analytics."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def analytics_get_list_analytics(input: ListAnalyticsInput) -> ListAnalyticsResult:
    """
    Get list analytics.

    API:
        GET /list/{list_id}/analytics

    Args:
        input: ListAnalyticsInput with list_id, start_date, end_date

    Returns:
        ListAnalyticsResult: The list analytics data

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await analytics_get_list_analytics(
            ListAnalyticsInput(list_id="list_1", start_date=1640995200000, end_date=1643673600000)
        )
        if response.ok:
            print(response.result.total_tasks)
    """
    client = ClickUpAPIClientFactory.get()
    query = ListAnalyticsQuery(start_date=input.start_date, end_date=input.end_date)
    async with client:
        resp = await client.analytics.get_list_analytics(input.list_id, query)
    if not resp:
        raise ClickUpAPIError("Get list analytics failed")
    domain = AnalyticsMapper.list_analytics_to_domain(resp)
    return ListAnalyticsResult(**AnalyticsMapper.list_analytics_to_output(domain))


@mcp.tool(
    title="Get Space Analytics",
    name="analytics.get_space_analytics",
    description=(
        "Get space analytics with date range. HTTP: GET /space/{space_id}/analytics."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def analytics_get_space_analytics(input: SpaceAnalyticsInput) -> SpaceAnalyticsResult:
    """
    Get space analytics.

    API:
        GET /space/{space_id}/analytics

    Args:
        input: SpaceAnalyticsInput with space_id, start_date, end_date

    Returns:
        SpaceAnalyticsResult: The space analytics data

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await analytics_get_space_analytics(
            SpaceAnalyticsInput(space_id="space_1", start_date=1640995200000, end_date=1643673600000)
        )
        if response.ok:
            print(response.result.total_tasks)
    """
    client = ClickUpAPIClientFactory.get()
    query = SpaceAnalyticsQuery(start_date=input.start_date, end_date=input.end_date)
    async with client:
        resp = await client.analytics.get_space_analytics(input.space_id, query)
    if not resp:
        raise ClickUpAPIError("Get space analytics failed")
    domain = AnalyticsMapper.space_analytics_to_domain(resp)
    return SpaceAnalyticsResult(**AnalyticsMapper.space_analytics_to_output(domain))
