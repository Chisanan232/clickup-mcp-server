"""MCP input models for bottleneck detection operations.

These inputs are LLM-friendly contracts used by FastMCP tools. They map to
Domain entities first, then DTOs for ClickUp wire format.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BottleneckDetectionInput(BaseModel):
    """
    Detect bottlenecks in team workflows. HTTP: GET /team/{team_id}/analytics/bottleneck

    When to use: Identify process bottlenecks in task workflows and team productivity.

    Constraints:
        - `start_date` and `end_date` must be epoch milliseconds
        - `threshold` must be a positive number

    Attributes:
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        list_id: Optional list ID for filtered detection
        threshold: Threshold value for bottleneck detection
        bottleneck_type: Type of bottleneck to detect (e.g., status_stuck, assignee_overload, list_backlog)

    Examples:
        BottleneckDetectionInput(team_id="123", start_date=1640995200000, end_date=1643673600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "123",
                    "start_date": 1640995200000,
                    "end_date": 1643673600000,
                    "threshold": 0.5,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["123", "team_1"])
    start_date: int = Field(..., description="Start date in epoch milliseconds.", examples=[1640995200000])
    end_date: int = Field(..., description="End date in epoch milliseconds.", examples=[1643673600000])
    list_id: Optional[str] = Field(None, description="Filter by list ID.", examples=["list_123"])
    threshold: Optional[float] = Field(
        None, gt=0, description="Threshold value for bottleneck detection.", examples=[0.5, 0.7]
    )
    bottleneck_type: Optional[str] = Field(
        None,
        description="Type of bottleneck to detect.",
        examples=["status_stuck", "assignee_overload", "list_backlog"],
    )
