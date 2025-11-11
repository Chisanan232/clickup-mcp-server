"""
Domain model for ClickUp Task.

Represents a Task aggregate with business behaviors. References related
aggregates by identity only (list_id, folder_id, space_id); does not embed
nested aggregates.
"""

from typing import List

from pydantic import Field

from .base import BaseDomainModel


class ClickUpTask(BaseDomainModel):
    """Domain model for a ClickUp Task with core behaviors and invariants."""

    task_id: str = Field(alias="id", description="The unique identifier for the task")
    name: str = Field(description="Task name")

    # Simple, vendor-agnostic attributes
    status: str | None = Field(default=None, description="Task status label")
    priority: int | None = Field(default=None, description="Priority level (1-4)")

    # Relationships by identity only
    list_id: str | None = Field(default=None)
    folder_id: str | None = Field(default=None)
    space_id: str | None = Field(default=None)
    parent_id: str | None = Field(default=None)

    assignee_ids: List[int | str] = Field(default_factory=list)

    # Time fields in epoch ms
    due_date: int | None = Field(default=None)
    time_estimate: int | None = Field(default=None)

    # Neutral representation; mapping layer will translate to DTO shapes
    custom_fields: list[dict] = Field(default_factory=list)

    @property
    def id(self) -> str:
        """Backward compatibility identifier alias."""
        return self.task_id

    # Behaviors / Invariants
    def change_status(self, new_status: str | None) -> None:
        """Change task status. Accepts None to clear status."""
        if new_status is not None and not new_status.strip():
            raise ValueError("status cannot be empty string")
        self.status = new_status

    def attach_to_list(self, list_id: str) -> None:
        if not list_id:
            raise ValueError("list_id must be provided")
        self.list_id = list_id

    def set_estimate(self, ms: int | None) -> None:
        if ms is not None and ms < 0:
            raise ValueError("estimate must be non-negative epoch ms")
        self.time_estimate = ms

    def schedule(self, due_ms: int | None, include_time: bool | None = None) -> None:
        if due_ms is not None and due_ms < 0:
            raise ValueError("due date must be non-negative epoch ms")
        self.due_date = due_ms
        # include_time is relevant to transport; domain stores due_date only

    def set_priority(self, value: int | None) -> None:
        if value is not None and (value < 1 or value > 4):
            raise ValueError("priority must be between 1 and 4")
        self.priority = value

    def assign(self, *user_ids: int | str) -> None:
        # Replace existing assignees with provided
        self.assignee_ids = list(user_ids)


# Backwards compatibility alias
Task = ClickUpTask
