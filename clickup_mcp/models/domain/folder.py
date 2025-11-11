"""
Domain model for ClickUp Folder.

Represents a Folder aggregate and enforces invariants while referencing
related aggregates by identity only (no nested hydration).
"""

from pydantic import Field

from .base import BaseDomainModel


class ClickUpFolder(BaseDomainModel):
    """Domain model for a ClickUp Folder.

    Notes:
    - References parent aggregate by identity only via ``space_id``.
    - Does not embed List objects; lists are separate aggregates.
    """

    folder_id: str = Field(alias="id", description="The unique identifier for the folder")
    name: str = Field(description="Folder name")
    space_id: str | None = Field(default=None, description="The space ID this folder belongs to")
    override_statuses: bool = Field(default=False, description="Whether this folder overrides statuses")
    hidden: bool = Field(default=False, description="Whether the folder is hidden")

    @property
    def id(self) -> str:
        """Backward compatibility identifier alias."""
        return self.folder_id

    # Behavior
    def rename(self, new_name: str) -> None:
        """Rename the folder.

        Raises ValueError if the name is empty or whitespace.
        """
        if not new_name or not new_name.strip():
            raise ValueError("Folder name cannot be empty")
        self.name = new_name

    def move_to_space(self, space_id: str) -> None:
        """Attach/move this folder to a different space by ID."""
        if not space_id:
            raise ValueError("space_id must be provided")
        self.space_id = space_id


# Backwards compatibility alias
Folder = ClickUpFolder
