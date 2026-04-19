"""
Domain model for ClickUp Time Report.

Represents a Time Report aggregate with business behaviors and invariants.
References related aggregates by identity only (task_id, user_id, team_id);
does not embed nested aggregates to maintain loose coupling.

A Time Report represents aggregated time tracking data for a team over a date range,
including total time tracked and breakdown by user or task.

Usage Examples:
    # Python - Create a time report domain entity
    from clickup_mcp.models.domain.reporting import TimeReport

    report = TimeReport(
        id="report_123",
        team_id="team_001",
        start_date=1702080000000,
        end_date=1702166400000,
        total_duration=3600000,
        user_id="user_789"
    )

    # Python - Use domain behaviors
    report.update_date_range(1702087200000, 1702173600000)
    report.set_total_duration(7200000)
"""

from typing import Optional

from pydantic import Field

from .base import BaseDomainModel


class TimeReport(BaseDomainModel):
    """
    Domain model for a ClickUp Time Report with core behaviors and invariants.

    This model represents a time report in ClickUp and includes all relevant fields
    from the ClickUp API. A Time Report aggregates time tracking data for a team
    over a date range.

    In ClickUp's hierarchy:
    - Team (workspace) → Time Report

    Attributes:
        report_id: The unique identifier for the time report (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        total_duration: Total duration in milliseconds
        user_id: Filter by user ID (if applicable)
        task_id: Filter by task ID (if applicable)

    Key Design Features:
    - Backward-compatible 'id' property that returns report_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for date fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.reporting import TimeReport

        report = TimeReport(
            id="report_123",
            team_id="team_001",
            start_date=1702080000000,
            end_date=1702166400000,
            total_duration=3600000,
            user_id="user_789"
        )

        # Python - Use domain behaviors
        report.update_date_range(1702087200000, 1702173600000)
        report.set_total_duration(7200000)

        # Python - Access report properties
        print(report.total_duration)  # 7200000
    """

    report_id: str = Field(alias="id", description="The unique identifier for the time report")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    total_duration: int | None = Field(default=None, description="Total duration in milliseconds")
    user_id: str | None = Field(default=None, description="Filter by user ID")
    task_id: str | None = Field(default=None, description="Filter by task ID")

    @property
    def id(self) -> str:
        """
        Get the time report ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the report ID via the 'id' property, even though the field is
        named 'report_id'.

        Returns:
            str: The time report ID (same as report_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            report = TimeReport(id="report_123", team_id="team_001", start_date=1702080000000, end_date=1702166400000)
            print(report.id)  # "report_123"
            print(report.report_id)  # "report_123" (same value)
        """
        return self.report_id

    # Behaviors / Invariants
    def update_date_range(self, start_date: int, end_date: int) -> None:
        """
        Update the date range of the time report.

        Updates the start and end dates in epoch milliseconds. Validates that
        the dates are non-negative and that end is not before start.

        Args:
            start_date: New start date in epoch milliseconds
            end_date: New end date in epoch milliseconds

        Raises:
            ValueError: If start_date or end_date is negative, or if end is before start

        Usage Examples:
            # Python - Update date range
            report = TimeReport(id="report_123", team_id="team_001", start_date=1702080000000, end_date=1702166400000)
            report.update_date_range(1702087200000, 1702173600000)
            print(report.start_date)  # 1702087200000
            print(report.end_date)  # 1702173600000

            # Python - Error on end before start
            try:
                report.update_date_range(1702173600000, 1702087200000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if start_date < 0:
            raise ValueError("start_date must be non-negative epoch ms")
        if end_date < 0:
            raise ValueError("end_date must be non-negative epoch ms")
        if end_date < start_date:
            raise ValueError("end_date cannot be before start_date")

        self.start_date = start_date
        self.end_date = end_date

    def set_total_duration(self, duration_ms: int | None) -> None:
        """
        Set the total duration of the time report.

        Updates the total duration in epoch milliseconds. Validates that
        the duration is non-negative.

        Args:
            duration_ms: Total duration in milliseconds, or None to clear

        Raises:
            ValueError: If duration_ms is negative

        Usage Examples:
            # Python - Set total duration
            report = TimeReport(id="report_123", team_id="team_001", start_date=1702080000000, end_date=1702166400000)
            report.set_total_duration(7200000)  # 2 hours
            print(report.total_duration)  # 7200000

            # Python - Clear duration
            report.set_total_duration(None)
            print(report.total_duration)  # None

            # Python - Error on negative value
            try:
                report.set_total_duration(-1000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if duration_ms is not None and duration_ms < 0:
            raise ValueError("duration_ms must be non-negative epoch ms")
        self.total_duration = duration_ms

    def set_user_filter(self, user_id: str | None) -> None:
        """
        Set the user filter for the time report.

        Updates the user ID filter. Use None to remove the filter.

        Args:
            user_id: User ID to filter by, or None to remove filter

        Usage Examples:
            # Python - Set user filter
            report = TimeReport(id="report_123", team_id="team_001", start_date=1702080000000, end_date=1702166400000)
            report.set_user_filter("user_789")
            print(report.user_id)  # "user_789"

            # Python - Remove filter
            report.set_user_filter(None)
            print(report.user_id)  # None
        """
        self.user_id = user_id

    def set_task_filter(self, task_id: str | None) -> None:
        """
        Set the task filter for the time report.

        Updates the task ID filter. Use None to remove the filter.

        Args:
            task_id: Task ID to filter by, or None to remove filter

        Usage Examples:
            # Python - Set task filter
            report = TimeReport(id="report_123", team_id="team_001", start_date=1702080000000, end_date=1702166400000)
            report.set_task_filter("task_456")
            print(report.task_id)  # "task_456"

            # Python - Remove filter
            report.set_task_filter(None)
            print(report.task_id)  # None
        """
        self.task_id = task_id
