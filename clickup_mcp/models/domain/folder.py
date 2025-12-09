"""
Domain model for ClickUp Folder.

Represents a Folder aggregate and enforces invariants while referencing
related aggregates by identity only (no nested hydration).

A Folder is a container for organizing Lists within a Space. In ClickUp's hierarchy:
- Team (workspace) → Space → Folder → List → Task

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., name validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Maintains a neutral representation independent of API specifics

Usage Examples:
    # Python - Create a folder domain entity
    from clickup_mcp.models.domain.folder import ClickUpFolder

    folder = ClickUpFolder(
        id="folder_123",
        name="Q4 Planning",
        space_id="space_456",
        override_statuses=True
    )

    # Python - Use domain behaviors
    folder.rename("Q4 2024 Planning")
    folder.move_to_space("space_789")

    # Python - Access folder properties
    print(folder.name)  # "Q4 2024 Planning"
    print(folder.space_id)  # "space_789"
"""

from pydantic import Field

from .base import BaseDomainModel


class ClickUpFolder(BaseDomainModel):
    """
    Domain model for a ClickUp Folder.

    This model represents a Folder in ClickUp and includes all relevant fields
    from the ClickUp API. A Folder is a container for organizing Lists within
    a Space, providing an additional level of hierarchy.

    In ClickUp's hierarchy:
    - Team (workspace) → Space → Folder → List → Task

    Attributes:
        folder_id: The unique identifier for the folder (aliased as 'id' for compatibility)
        name: The name of the folder
        space_id: The ID of the space this folder belongs to
        override_statuses: Whether this folder overrides space-level statuses
        hidden: Whether the folder is hidden from view

    Key Design Features:
    - Backward-compatible 'id' property that returns folder_id
    - Behavior methods that enforce domain invariants
    - References parent space by ID only (no nested objects)
    - Immutable once created (inherited from BaseDomainModel)
    - Flexible field population for API compatibility

    Notes:
    - References parent aggregate by identity only via ``space_id``.
    - Does not embed List objects; lists are separate aggregates.

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.folder import ClickUpFolder

        folder = ClickUpFolder(
            id="folder_123",
            name="Q4 Planning",
            space_id="space_456",
            override_statuses=True,
            hidden=False
        )

        # Python - Use domain behaviors
        folder.rename("Q4 2024 Planning")
        folder.move_to_space("space_789")

        # Python - Access folder properties
        print(folder.name)  # "Q4 2024 Planning"
        print(folder.space_id)  # "space_789"
        print(folder.id)  # "folder_123" (backward-compatible access)
    """

    folder_id: str = Field(alias="id", description="The unique identifier for the folder")
    name: str = Field(description="Folder name")
    space_id: str | None = Field(default=None, description="The space ID this folder belongs to")
    override_statuses: bool = Field(default=False, description="Whether this folder overrides statuses")
    hidden: bool = Field(default=False, description="Whether the folder is hidden")

    @property
    def id(self) -> str:
        """
        Get the folder ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the folder ID via the 'id' property, even though the field is
        named 'folder_id'.

        Returns:
            str: The folder ID (same as folder_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            folder = ClickUpFolder(id="folder_123", name="My Folder")
            print(folder.id)  # "folder_123"
            print(folder.folder_id)  # "folder_123" (same value)
        """
        return self.folder_id

    # Behavior
    def rename(self, new_name: str) -> None:
        """
        Rename the folder with validation.

        Updates the folder name to a new value. Validates that the name
        is not empty or whitespace-only.

        Args:
            new_name: The new name for the folder

        Raises:
            ValueError: If new_name is empty or contains only whitespace

        Usage Examples:
            # Python - Rename folder
            folder = ClickUpFolder(id="folder_123", name="Old Name")
            folder.rename("New Name")
            print(folder.name)  # "New Name"

            # Python - Error on empty name
            try:
                folder.rename("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not new_name or not new_name.strip():
            raise ValueError("Folder name cannot be empty")
        self.name = new_name

    def move_to_space(self, space_id: str) -> None:
        """
        Move folder to a different space.

        Attaches/moves this folder to a different space by updating the space_id.
        Validates that the space_id is not empty.

        Args:
            space_id: The ID of the space to move this folder to

        Raises:
            ValueError: If space_id is empty or None

        Usage Examples:
            # Python - Move folder to different space
            folder = ClickUpFolder(id="folder_123", name="My Folder", space_id="space_456")
            folder.move_to_space("space_789")
            print(folder.space_id)  # "space_789"

            # Python - Error on empty space_id
            try:
                folder.move_to_space("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not space_id:
            raise ValueError("space_id must be provided")
        self.space_id = space_id


# Backwards compatibility alias
Folder = ClickUpFolder
