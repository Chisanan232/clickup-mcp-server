"""MCP input models for insights generation operations.

These inputs are LLM-friendly contracts used by FastMCP tools. They map to
Domain entities first, then DTOs for ClickUp wire format.
"""

from pydantic import BaseModel, ConfigDict, Field


class InsightsGenerationInput(BaseModel):
    """
    Generate insights from analytics data. HTTP: GET /team/{team_id}/analytics/insights

    When to use: Generate actionable recommendations based on analytics data.

    Constraints:
        - `start_date` and `end_date` must be epoch milliseconds
        - `insight_type` must be one of: productivity, efficiency, workload

    Attributes:
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        insight_type: Type of insight to generate (e.g., productivity, efficiency, workload)

    Examples:
        InsightsGenerationInput(team_id="123", start_date=1640995200000, end_date=1643673600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "123",
                    "start_date": 1640995200000,
                    "end_date": 1643673600000,
                    "insight_type": "productivity",
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["123", "team_1"])
    start_date: int = Field(..., description="Start date in epoch milliseconds.", examples=[1640995200000])
    end_date: int = Field(..., description="End date in epoch milliseconds.", examples=[1643673600000])
    insight_type: str = Field(
        ...,
        description="Type of insight to generate.",
        examples=["productivity", "efficiency", "workload"],
    )
