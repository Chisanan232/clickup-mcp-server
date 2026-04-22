"""MCP tools for ClickUp Insights Generation.

Tools:
- insights.generate
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.insights import InsightsGenerationInput
from clickup_mcp.mcp_server.models.outputs.insights import InsightsGenerationResult
from clickup_mcp.models.dto.insights import InsightsGenerationQuery

from .app import mcp


@mcp.tool(
    title="Generate Insights",
    name="insights.generate",
    description=(
        "Generate insights from analytics data with date range and insight type. "
        "HTTP: GET /team/{team_id}/analytics/insights."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def insights_generate(input: InsightsGenerationInput) -> InsightsGenerationResult:
    """
    Generate insights from analytics data.

    API:
        GET /team/{team_id}/analytics/insights

    Args:
        input: InsightsGenerationInput with team_id, start_date, end_date, and insight_type

    Returns:
        InsightsGenerationResult: The insights generation data

    Error Handling:
        Decorated with `@handle_tool_errors` and returns a ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await insights_generate(
            InsightsGenerationInput(team_id="team_1", start_date=1640995200000, end_date=1643673600000, insight_type="productivity")
        )
        if response.ok:
            print(response.result.recommendations)
    """
    client = ClickUpAPIClientFactory.get()
    query = InsightsGenerationQuery(
        start_date=input.start_date,
        end_date=input.end_date,
        insight_type=input.insight_type,
    )
    async with client:
        resp = await client.insights.generate(input.team_id, query)
    if not resp:
        raise ClickUpAPIError("Generate insights failed")
    return InsightsGenerationResult(
        id=resp.id,
        team_id=resp.team_id,
        start_date=resp.start_date,
        end_date=resp.end_date,
        insight_type=resp.insight_type,
        priority=resp.priority,
        recommendations=resp.recommendations,
        metrics=resp.metrics,
        confidence_score=resp.confidence_score,
        date_generated=resp.date_generated,
    )
