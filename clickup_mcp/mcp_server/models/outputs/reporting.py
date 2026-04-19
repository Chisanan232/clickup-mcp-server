"""
Result models for Time Report tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.

Usage Examples:
    # Python - Single time report result
    from clickup_mcp.mcp_server.models.outputs.reporting import TimeReportResult

    t = TimeReportResult(
        id="report_1",
        team_id="team_789",
        start_date=1702080000000,
        end_date=1702166400000,
        total_duration=3600000
    )

    # Python - List result
    lr = TimeReportListResult(items=[TimeReportListItem(id="report_1", team_id="team_789", start_date=1702080000000, end_date=1702166400000, total_duration=3600000)])
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TimeReportResult(BaseModel):
    """Concise time report detail; normalized units."""

    id: str = Field(..., description="Time report ID", examples=["report_1", "rpt_123"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    start_date: int = Field(..., ge=0, description="Start date in epoch milliseconds", examples=[1702080000000])
    end_date: int = Field(..., ge=0, description="End date in epoch milliseconds", examples=[1702166400000])
    total_duration: Optional[int] = Field(None, ge=0, description="Total duration in milliseconds", examples=[3600000])
    user_id: Optional[str] = Field(None, description="Filter by user ID", examples=["user_456"])
    task_id: Optional[str] = Field(None, description="Filter by task ID", examples=["task_123"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "report_1",
                    "team_id": "team_789",
                    "start_date": 1702080000000,
                    "end_date": 1702166400000,
                    "total_duration": 3600000,
                }
            ]
        }
    }


class TimeReportListItem(BaseModel):
    """
    Item shape for time report summaries returned by MCP tools.

    Attributes:
        id: Time report ID
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_duration: Total duration in milliseconds
    """

    id: str = Field(..., description="Time report ID", examples=["report_1", "rpt_123"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    start_date: int = Field(..., ge=0, description="Start date in epoch milliseconds", examples=[1702080000000])
    end_date: int = Field(..., ge=0, description="End date in epoch milliseconds", examples=[1702166400000])
    total_duration: Optional[int] = Field(None, ge=0, description="Total duration in milliseconds", examples=[3600000])


class TimeReportListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[TimeReportListItem] = Field(
        default_factory=list,
        examples=[
            [
                {
                    "id": "report_1",
                    "team_id": "team_789",
                    "start_date": 1702080000000,
                    "end_date": 1702166400000,
                    "total_duration": 3600000,
                }
            ]
        ],
    )
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)", examples=["page=2"])
    truncated: bool = Field(False, description="True if items were trimmed to budget", examples=[False])
