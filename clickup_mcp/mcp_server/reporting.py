"""MCP tools for ClickUp Time Reports.

Tools:
- report.create
- report.list
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.reporting import (
    TimeReportCreateInput,
    TimeReportListInput,
)
from clickup_mcp.mcp_server.models.outputs.reporting import (
    TimeReportListResult,
)
from clickup_mcp.models.dto.reporting import TimeReportListQuery
from clickup_mcp.models.mapping.reporting_mapper import ReportingMapper

from .app import mcp


@mcp.tool(
    title="Create Time Report",
    name="report.create",
    description=(
        "Create a time report for a team with date range filters. "
        "Time fields are epoch milliseconds. HTTP: POST /team/{team_id}/time_tracking."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def report_create(input: TimeReportCreateInput) -> TimeReportListResult:
    """
    Create a time report for a team.

    API:
        POST /team/{team_id}/time_tracking

    Args:
        input: TimeReportCreateInput with team_id, start_date, end_date, and optional assignee, task_id

    Returns:
        TimeReportListResult: List of time entries matching the report criteria

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await report_create(TimeReportCreateInput(team_id="team_1", start_date=1702080000000, end_date=1702166400000))
        if response.ok:
            for item in response.result.items:
                print(item.id)
    """
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO

    domain = ReportingMapper.from_create_input(input)
    dto = ReportingMapper.to_create_dto(domain)
    async with client:
        resp = await client.reporting.create(input.team_id, dto)
    if not resp:
        raise ClickUpAPIError("Create time report failed")
    items = [ReportingMapper.to_time_report_list_item_output(ReportingMapper.to_domain(entry)) for entry in resp.items]
    return TimeReportListResult(items=items, next_cursor=resp.next_page, truncated=False)


@mcp.tool(
    title="List Time Reports",
    name="report.list",
    description=(
        "List time entries for a team with filters. Constraints: `limit` ≤ 100. "
        "HTTP: GET /team/{team_id}/time_tracking."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def report_list(input: TimeReportListInput) -> TimeReportListResult:
    """
    List time entries for a team with filters.

    API:
        GET /team/{team_id}/time_tracking

    Args:
        input: TimeReportListInput with team_id, optional assignee, task_id, start_date, end_date, page, limit

    Returns:
        TimeReportListResult: Page of time entry list items

    Error Handling:
        Decorated with `@handle_tool_errors`, returns a ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await report_list(TimeReportListInput(team_id="team_1", start_date=1702080000000, end_date=1702166400000, limit=50))
        if response.ok:
            for it in response.result.items:
                print(it.id)
    """
    client = ClickUpAPIClientFactory.get()
    query = TimeReportListQuery(
        assignee=input.assignee,
        task_id=input.task_id,
        start_date=input.start_date,
        end_date=input.end_date,
        page=input.page,
        limit=input.limit,
    )
    async with client:
        resp = await client.reporting.list(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("List time reports failed")
    items = [ReportingMapper.to_time_report_list_item_output(ReportingMapper.to_domain(entry)) for entry in resp.items]
    return TimeReportListResult(items=items, next_cursor=resp.next_page, truncated=False)
