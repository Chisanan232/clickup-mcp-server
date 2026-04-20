"""MCP tools for ClickUp Bottleneck Detection.

Tools:
- bottleneck.detect
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.bottleneck import BottleneckDetectionInput
from clickup_mcp.mcp_server.models.outputs.bottleneck import BottleneckDetectionResult
from clickup_mcp.models.dto.bottleneck import BottleneckDetectionQuery
from clickup_mcp.models.mapping.analytics_mapper import AnalyticsMapper

from .app import mcp


@mcp.tool(
    title="Detect Bottlenecks",
    name="bottleneck.detect",
    description=(
        "Detect bottlenecks in team workflows with date range and optional filters. "
        "HTTP: GET /team/{team_id}/analytics/bottleneck."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def bottleneck_detect(input: BottleneckDetectionInput) -> BottleneckDetectionResult:
    """
    Detect bottlenecks in team workflows.

    API:
        GET /team/{team_id}/analytics/bottleneck

    Args:
        input: BottleneckDetectionInput with team_id, start_date, end_date, and optional list_id, threshold, bottleneck_type

    Returns:
        BottleneckDetectionResult: The bottleneck detection data

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await bottleneck_detect(
            BottleneckDetectionInput(team_id="team_1", start_date=1640995200000, end_date=1643673600000)
        )
        if response.ok:
            print(response.result.bottleneck_type)
    """
    client = ClickUpAPIClientFactory.get()
    query = BottleneckDetectionQuery(
        start_date=input.start_date,
        end_date=input.end_date,
        list_id=input.list_id,
        threshold=input.threshold,
        bottleneck_type=input.bottleneck_type,
    )
    async with client:
        resp = await client.bottleneck.detect(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("Detect bottlenecks failed")
    return BottleneckDetectionResult(
        id=resp.id,
        team_id=resp.team_id,
        list_id=resp.list_id,
        start_date=resp.start_date,
        end_date=resp.end_date,
        bottleneck_type=resp.bottleneck_type,
        severity=resp.severity,
        affected_tasks=resp.affected_tasks,
        threshold=resp.threshold,
        current_value=resp.current_value,
        recommendations=resp.recommendations,
        date_detected=resp.date_detected,
        date_resolved=resp.date_resolved,
    )
