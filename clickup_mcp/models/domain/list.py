"""
Domain model for ClickUp List.

Represents a List aggregate and enforces invariants while referencing
related aggregates by identity only (no nested hydration).
"""

from pydantic import Field

from .base import BaseDomainModel


class ClickUpList(BaseDomainModel):
    """Domain model for a ClickUp List.

    Notes:
    - References parent aggregates by identity only via ``folder_id`` and ``space_id``.
    - Does not embed Task objects; tasks are separate aggregates.
    """

    list_id: str = Field(alias="id", description="The unique identifier for the list")
    name: str = Field(description="List name")
    content: str | None = Field(default=None, description="List description")

    # Relationships by ID only
    folder_id: str | None = Field(default=None)
    space_id: str | None = Field(default=None)

    # Lightweight planning fields
    status: str | None = Field(default=None)
    priority: int | None = Field(default=None)
    assignee_id: int | str | None = Field(default=None)
    due_date: int | None = Field(default=None)
    due_date_time: bool | None = Field(default=None)

    @property
    def id(self) -> str:
        """Backward compatibility identifier alias."""
        return self.list_id

    # Behavior
    def rename(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise ValueError("List name cannot be empty")
        self.name = new_name

    def attach_to_folder(self, folder_id: str) -> None:
        if not folder_id:
            raise ValueError("folder_id must be provided")
        self.folder_id = folder_id

    def attach_to_space(self, space_id: str) -> None:
        if not space_id:
            raise ValueError("space_id must be provided")
        self.space_id = space_id

    def assign_to(self, user_id: int | str | None) -> None:
        self.assignee_id = user_id

    def schedule(self, due_ms: int, include_time: bool | None = None) -> None:
        if due_ms < 0:
            raise ValueError("due date must be non-negative epoch ms")
        self.due_date = due_ms
        if include_time is not None:
            self.due_date_time = include_time


# Backwards compatibility alias
List = ClickUpList
