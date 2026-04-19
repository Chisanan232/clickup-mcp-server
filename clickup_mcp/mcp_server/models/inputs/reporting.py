"""MCP input models for time reporting operations.

High-signal schemas for FastMCP with constraints and examples.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TimeReportGetInput(BaseModel):
    """
    Get a time report by ID. HTTP: GET /team/{team_id}/time_tracking/{report_id}

    When to use: Retrieve details of a specific time report.

    Attributes:
        team_id: Team/workspace ID
        report_id: Time report ID

    Examples:
        TimeReportGetInput(team_id="team_1", report_id="report_123")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"team_id": "team_1", "report_id": "report_123"}]})

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    report_id: str = Field(..., min_length=1, description="Time report ID.", examples=["report_123", "rpt_abc"])


class TimeReportCreateInput(BaseModel):
    """
    Create a time report for a team. HTTP: POST /team/{team_id}/time_tracking

    When to use: Generate a time report for a team with optional filters.

    Constraints:
        - `start_date` and `end_date` are required
        - Time fields are epoch milliseconds

    Attributes:
        team_id: Team/workspace ID
        start_date: Start date in epoch ms
        end_date: End date in epoch ms
        assignee: Filter by user ID
        task_id: Filter by task ID

    Examples:
        TimeReportCreateInput(team_id="team_1", start_date=1702080000000, end_date=1702166400000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "team_1",
                    "start_date": 1702080000000,
                    "end_date": 1702166400000,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    start_date: int = Field(..., description="Start date in epoch ms.", examples=[1702080000000])
    end_date: int = Field(..., description="End date in epoch ms.", examples=[1702166400000])
    assignee: Optional[str] = Field(None, description="Filter by user ID.", examples=["user_123", "usr_abc"])
    task_id: Optional[str] = Field(None, description="Filter by task ID.", examples=["task_123", "tsk_abc"])


class TimeReportListInput(BaseModel):
    """
    List time reports for a team. HTTP: GET /team/{team_id}/time_tracking

    When to use: Retrieve available time reports with optional filters.

    Constraints:
        - `limit` ≤ 100 per API

    Attributes:
        team_id: Team/workspace ID
        assignee: Filter by user ID
        task_id: Filter by task ID
        start_date: Filter by start date (epoch ms)
        end_date: Filter by end date (epoch ms)
        page: Page number (0-indexed)
        limit: Page size (cap 100)

    Examples:
        TimeReportListInput(team_id="team_1", limit=50)
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"team_id": "team_1", "limit": 50}]})

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    assignee: Optional[str] = Field(None, description="Filter by user ID.", examples=["user_123", "usr_abc"])
    task_id: Optional[str] = Field(None, description="Filter by task ID.", examples=["task_123", "tsk_abc"])
    start_date: Optional[int] = Field(None, description="Filter by start date (epoch ms).", examples=[1702080000000])
    end_date: Optional[int] = Field(None, description="Filter by end date (epoch ms).", examples=[1702166400000])
    page: int = Field(0, ge=0, description="Page number (0-indexed).", examples=[0, 1, 2])
    limit: int = Field(100, ge=1, le=100, description="Page size (cap 100).", examples=[25, 50, 100])
