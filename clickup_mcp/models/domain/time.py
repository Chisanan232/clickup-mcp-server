"""
Domain model for ClickUp Time Entry.

Represents a Time Entry aggregate with business behaviors and invariants.
References related aggregates by identity only (task_id, user_id, team_id);
does not embed nested aggregates to maintain loose coupling.

A Time Entry represents logged time spent on a task, including duration,
description, and timing information.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., duration validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create a time entry domain entity
    from clickup_mcp.models.domain.time import TimeEntry

    entry = TimeEntry(
        id="entry_123",
        task_id="task_456",
        user_id="user_789",
        team_id="team_001",
        description="Implementation work",
        duration=3600000,  # 1 hour in ms
        start=1702080000000,
        end=1702083600000
    )

    # Python - Use domain behaviors
    entry.update_description("Updated description")
    entry.set_duration(7200000)  # 2 hours
    entry.adjust_timing(1702087200000, 1702090800000)
"""

from typing import Optional

from pydantic import Field

from .base import BaseDomainModel


class TimeEntry(BaseDomainModel):
    """
    Domain model for a ClickUp Time Entry with core behaviors and invariants.

    This model represents a time entry in ClickUp and includes all relevant fields
    from the ClickUp API. A Time Entry tracks time spent on a task, including
    duration, description, and timing information.

    In ClickUp's hierarchy:
    - Team (workspace) → Task → Time Entry

    Attributes:
        entry_id: The unique identifier for the time entry (aliased as 'id' for compatibility)
        task_id: The ID of the task this time entry belongs to
        user_id: The ID of the user who logged the time
        team_id: The ID of the team/workspace
        description: Description of the work done
        start: Start time in epoch milliseconds
        end: End time in epoch milliseconds
        duration: Duration in milliseconds
        billable: Whether the time entry is billable

    Key Design Features:
    - Backward-compatible 'id' property that returns entry_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.time import TimeEntry

        entry = TimeEntry(
            id="entry_123",
            task_id="task_456",
            user_id="user_789",
            team_id="team_001",
            description="Implementation work",
            duration=3600000,
            start=1702080000000,
            end=1702083600000
        )

        # Python - Use domain behaviors
        entry.update_description("Updated description")
        entry.set_duration(7200000)
        entry.adjust_timing(1702087200000, 1702090800000)

        # Python - Access entry properties
        print(entry.description)  # "Updated description"
        print(entry.duration)  # 7200000
    """

    entry_id: str = Field(alias="id", description="The unique identifier for the time entry")
    task_id: str = Field(description="Task ID this time entry belongs to")
    user_id: str = Field(description="User ID who logged the time")
    team_id: str = Field(description="Team/workspace ID")
    description: str | None = Field(default=None, description="Description of the work done")
    start: int | None = Field(default=None, description="Start time in epoch milliseconds")
    end: int | None = Field(default=None, description="End time in epoch milliseconds")
    duration: int | None = Field(default=None, description="Duration in milliseconds")
    billable: bool = Field(default=False, description="Whether the time entry is billable")

    @property
    def id(self) -> str:
        """
        Get the time entry ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the entry ID via the 'id' property, even though the field is
        named 'entry_id'.

        Returns:
            str: The time entry ID (same as entry_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            entry = TimeEntry(id="entry_123", task_id="task_456", user_id="user_789", team_id="team_001")
            print(entry.id)  # "entry_123"
            print(entry.entry_id)  # "entry_123" (same value)
        """
        return self.entry_id

    # Behaviors / Invariants
    def update_description(self, description: str | None) -> None:
        """
        Update the time entry description.

        Updates the description to a new value. Accepts None to clear the description.
        Validates that non-None description values are not empty strings.

        Args:
            description: The new description or None to clear

        Raises:
            ValueError: If description is an empty string

        Usage Examples:
            # Python - Update description
            entry = TimeEntry(id="entry_123", task_id="task_456", user_id="user_789", team_id="team_001")
            entry.update_description("Updated description")
            print(entry.description)  # "Updated description"

            # Python - Clear description
            entry.update_description(None)
            print(entry.description)  # None

            # Python - Error on empty string
            try:
                entry.update_description("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if description is not None and not description.strip():
            raise ValueError("description cannot be empty string")
        self.description = description

    def set_duration(self, duration_ms: int | None) -> None:
        """
        Set the duration of the time entry.

        Updates the duration in epoch milliseconds. Validates that
        the duration is non-negative.

        Args:
            duration_ms: Duration in milliseconds, or None to clear

        Raises:
            ValueError: If duration_ms is negative

        Usage Examples:
            # Python - Set duration
            entry = TimeEntry(id="entry_123", task_id="task_456", user_id="user_789", team_id="team_001")
            entry.set_duration(3600000)  # 1 hour
            print(entry.duration)  # 3600000

            # Python - Clear duration
            entry.set_duration(None)
            print(entry.duration)  # None

            # Python - Error on negative value
            try:
                entry.set_duration(-1000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if duration_ms is not None and duration_ms < 0:
            raise ValueError("duration must be non-negative epoch ms")
        self.duration = duration_ms

    def adjust_timing(self, start: int | None, end: int | None) -> None:
        """
        Adjust the start and end times of the time entry.

        Sets the start and end times in epoch milliseconds. Validates that
        the times are non-negative and that end is not before start (if both provided).

        Args:
            start: Start time in epoch milliseconds, or None to clear
            end: End time in epoch milliseconds, or None to clear

        Raises:
            ValueError: If start or end is negative, or if end is before start

        Usage Examples:
            # Python - Adjust timing
            entry = TimeEntry(id="entry_123", task_id="task_456", user_id="user_789", team_id="team_001")
            entry.adjust_timing(1702080000000, 1702083600000)
            print(entry.start)  # 1702080000000
            print(entry.end)  # 1702083600000

            # Python - Clear timing
            entry.adjust_timing(None, None)
            print(entry.start)  # None
            print(entry.end)  # None

            # Python - Error on end before start
            try:
                entry.adjust_timing(1702083600000, 1702080000000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if start is not None and start < 0:
            raise ValueError("start time must be non-negative epoch ms")
        if end is not None and end < 0:
            raise ValueError("end time must be non-negative epoch ms")
        if start is not None and end is not None and end < start:
            raise ValueError("end time cannot be before start time")

        self.start = start
        self.end = end

        # Auto-calculate duration if both start and end are provided
        if start is not None and end is not None:
            self.duration = end - start

    def set_billable(self, billable: bool) -> None:
        """
        Set whether the time entry is billable.

        Updates the billable status of the time entry.

        Args:
            billable: Whether the time entry should be marked as billable

        Usage Examples:
            # Python - Mark as billable
            entry = TimeEntry(id="entry_123", task_id="task_456", user_id="user_789", team_id="team_001")
            entry.set_billable(True)
            print(entry.billable)  # True

            # Python - Mark as non-billable
            entry.set_billable(False)
            print(entry.billable)  # False
        """
        self.billable = billable

    def is_active(self) -> bool:
        """
        Check if the time entry is currently active (has start time but no end time).

        Returns:
            bool: True if the time entry is active (started but not ended)

        Usage Examples:
            # Python - Check if active
            entry = TimeEntry(id="entry_123", task_id="task_456", user_id="user_789", team_id="team_001", start=1702080000000)
            print(entry.is_active())  # True

            entry.adjust_timing(1702080000000, 1702083600000)
            print(entry.is_active())  # False
        """
        return self.start is not None and self.end is None


# Backwards compatibility alias
TimeTrackingEntry = TimeEntry
