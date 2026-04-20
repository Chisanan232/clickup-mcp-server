"""MCP input models for analytics operations.

These inputs are LLM-friendly contracts used by FastMCP tools. They map to
Domain entities first, then DTOs for ClickUp wire format.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskAnalyticsInput(BaseModel):
    """
    Get task analytics. HTTP: GET /team/{team_id}/analytics/task

    When to use: Retrieve analytics data for tasks within a team/workspace.

    Constraints:
        - `start_date` and `end_date` must be epoch milliseconds
        - `limit` ≤ 100 per API

    Attributes:
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        assignee_id: Filter by assignee
        status: Filter by status
        limit: Page size (cap 100)

    Examples:
        TaskAnalyticsInput(team_id="123", start_date=1640995200000, end_date=1643673600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "123",
                    "start_date": 1640995200000,
                    "end_date": 1643673600000,
                    "limit": 50,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["123", "team_1"])
    start_date: int = Field(..., description="Start date in epoch milliseconds.", examples=[1640995200000])
    end_date: int = Field(..., description="End date in epoch milliseconds.", examples=[1643673600000])
    assignee_id: Optional[str] = Field(None, description="Filter by assignee ID.", examples=["user_123"])
    status: Optional[str] = Field(None, description="Filter by status.", examples=["done", "in_progress"])
    limit: int = Field(100, ge=1, le=100, description="Page size (cap 100 by API).", examples=[25, 50, 100])


class TeamAnalyticsInput(BaseModel):
    """
    Get team analytics. HTTP: GET /team/{team_id}/analytics/team

    When to use: Retrieve overall analytics data for a team/workspace.

    Constraints:
        - `start_date` and `end_date` must be epoch milliseconds

    Attributes:
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds

    Examples:
        TeamAnalyticsInput(team_id="123", start_date=1640995200000, end_date=1643673600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "123",
                    "start_date": 1640995200000,
                    "end_date": 1643673600000,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["123", "team_1"])
    start_date: int = Field(..., description="Start date in epoch milliseconds.", examples=[1640995200000])
    end_date: int = Field(..., description="End date in epoch milliseconds.", examples=[1643673600000])


class ListAnalyticsInput(BaseModel):
    """
    Get list analytics. HTTP: GET /list/{list_id}/analytics

    When to use: Retrieve analytics data for a specific list.

    Constraints:
        - `start_date` and `end_date` must be epoch milliseconds

    Attributes:
        list_id: List ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds

    Examples:
        ListAnalyticsInput(list_id="456", start_date=1640995200000, end_date=1643673600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "list_id": "456",
                    "start_date": 1640995200000,
                    "end_date": 1643673600000,
                }
            ]
        }
    )

    list_id: str = Field(..., min_length=1, description="List ID.", examples=["456", "list_1"])
    start_date: int = Field(..., description="Start date in epoch milliseconds.", examples=[1640995200000])
    end_date: int = Field(..., description="End date in epoch milliseconds.", examples=[1643673600000])


class SpaceAnalyticsInput(BaseModel):
    """
    Get space analytics. HTTP: GET /space/{space_id}/analytics

    When to use: Retrieve analytics data for a specific space.

    Constraints:
        - `start_date` and `end_date` must be epoch milliseconds

    Attributes:
        space_id: Space ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds

    Examples:
        SpaceAnalyticsInput(space_id="789", start_date=1640995200000, end_date=1643673600000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "space_id": "789",
                    "start_date": 1640995200000,
                    "end_date": 1643673600000,
                }
            ]
        }
    )

    space_id: str = Field(..., min_length=1, description="Space ID.", examples=["789", "space_1"])
    start_date: int = Field(..., description="Start date in epoch milliseconds.", examples=[1640995200000])
    end_date: int = Field(..., description="End date in epoch milliseconds.", examples=[1643673600000])
