"""MCP output models for analytics operations.

These models define the structure for analytics results returned by MCP tools.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class TaskAnalyticsResult(BaseModel):
    """Result for task analytics operations."""

    id: str = Field(description="Analytics ID")
    team_id: str = Field(description="Team/workspace ID")
    list_id: Optional[str] = Field(default=None, description="List ID for filtered analytics")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    in_progress_tasks: int = Field(default=0, description="Number of tasks in progress")
    blocked_tasks: int = Field(default=0, description="Number of blocked tasks")
    average_completion_time: Optional[int] = Field(default=None, description="Average completion time in milliseconds")
    assignee_metrics: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Metrics per assignee")
    status_metrics: Dict[str, int] = Field(default_factory=dict, description="Metrics per status")


class TeamAnalyticsResult(BaseModel):
    """Result for team analytics operations."""

    id: str = Field(description="Analytics ID")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks across the team")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_lists: int = Field(default=0, description="Number of lists in the team")
    active_users: int = Field(default=0, description="Number of active users")
    average_task_completion_time: Optional[int] = Field(
        default=None, description="Average task completion time in milliseconds"
    )


class ListAnalyticsResult(BaseModel):
    """Result for list analytics operations."""

    id: str = Field(description="Analytics ID")
    list_id: str = Field(description="List ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks in the list")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    overdue_tasks: int = Field(default=0, description="Number of overdue tasks")
    average_completion_time: Optional[int] = Field(
        default=None, description="Average task completion time in milliseconds"
    )


class SpaceAnalyticsResult(BaseModel):
    """Result for space analytics operations."""

    id: str = Field(description="Analytics ID")
    space_id: str = Field(description="Space ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_tasks: int = Field(default=0, description="Total number of tasks in the space")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_lists: int = Field(default=0, description="Number of lists in the space")
    total_folders: int = Field(default=0, description="Number of folders in the space")
