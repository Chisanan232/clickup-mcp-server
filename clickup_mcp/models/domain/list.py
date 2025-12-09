"""
Domain model for ClickUp List.

Represents a List aggregate and enforces invariants while referencing
related aggregates by identity only (no nested hydration).

A List is a container for organizing Tasks within a Folder or Space. In ClickUp's hierarchy:
- Team (workspace) → Space → Folder → List → Task

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., name validation, date validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Maintains a neutral representation independent of API specifics

Usage Examples:
    # Python - Create a list domain entity
    from clickup_mcp.models.domain.list import ClickUpList

    lst = ClickUpList(
        id="list_123",
        name="Q4 Tasks",
        folder_id="folder_456",
        space_id="space_789"
    )

    # Python - Use domain behaviors
    lst.rename("Q4 2024 Tasks")
    lst.assign_to("user_111")
    lst.schedule(1702080000000)  # Set due date

    # Python - Access list properties
    print(lst.name)  # "Q4 2024 Tasks"
    print(lst.assignee_id)  # "user_111"
"""

from pydantic import Field

from .base import BaseDomainModel


class ListStatus(BaseDomainModel):
    """
    Domain value object for a List status definition.

    Represents a status that can be applied to tasks within a list.
    This is a value object that encapsulates status configuration.

    Attributes:
        name: Status name as configured on the list
        type: Status type (open/closed/active/done)
        color: UI color for display (hex or token)
        orderindex: Ordering index on the list

    Usage Examples:
        # Python - Create a status
        from clickup_mcp.models.domain.list import ListStatus

        status = ListStatus(
            name="In Progress",
            type="active",
            color="#FF6B6B",
            orderindex=1
        )

        # Python - Access status properties
        print(status.name)  # "In Progress"
        print(status.type)  # "active"
    """

    name: str = Field(description="Status name as configured on the list")
    type: str | None = Field(default=None, description="Status type (open/closed/active/done)")
    color: str | None = Field(default=None, description="UI color (hex or token)")
    orderindex: int | None = Field(default=None, description="Ordering index on the list")


class ClickUpList(BaseDomainModel):
    """
    Domain model for a ClickUp List.

    This model represents a List in ClickUp and includes all relevant fields
    from the ClickUp API. A List is a container for organizing Tasks within
    a Folder or directly within a Space.

    In ClickUp's hierarchy:
    - Team (workspace) → Space → Folder → List → Task

    Attributes:
        list_id: The unique identifier for the list (aliased as 'id' for compatibility)
        name: The name of the list
        content: The description/content of the list
        folder_id: The ID of the folder containing this list (if any)
        space_id: The ID of the space containing this list
        status: Current status label for the list
        priority: Priority level for the list
        assignee_id: User ID assigned to manage the list
        due_date: Due date in epoch milliseconds
        due_date_time: Whether the due date includes time
        statuses: List of available status definitions for tasks in this list

    Key Design Features:
    - Backward-compatible 'id' property that returns list_id
    - Behavior methods that enforce domain invariants
    - References parent aggregates by ID only (no nested objects)
    - Immutable once created (inherited from BaseDomainModel)
    - Flexible field population for API compatibility

    Notes:
    - References parent aggregates by identity only via ``folder_id`` and ``space_id``.
    - Does not embed Task objects; tasks are separate aggregates.

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.list import ClickUpList

        lst = ClickUpList(
            id="list_123",
            name="Q4 Tasks",
            content="Tasks for Q4 planning",
            folder_id="folder_456",
            space_id="space_789",
            priority=2
        )

        # Python - Use domain behaviors
        lst.rename("Q4 2024 Tasks")
        lst.attach_to_folder("folder_999")
        lst.assign_to("user_111")
        lst.schedule(1702080000000)  # Set due date

        # Python - Access list properties
        print(lst.name)  # "Q4 2024 Tasks"
        print(lst.folder_id)  # "folder_999"
        print(lst.assignee_id)  # "user_111"
    """

    list_id: str = Field(alias="id", description="The unique identifier for the list")
    name: str = Field(description="List name")
    content: str | None = Field(default=None, description="List description")

    # Relationships by ID only
    folder_id: str | None = Field(default=None, description="The folder containing this list")
    space_id: str | None = Field(default=None, description="The space containing this list")

    # Lightweight planning fields
    status: str | None = Field(default=None, description="Current status label")
    priority: int | None = Field(default=None, description="Priority level")
    assignee_id: int | str | None = Field(default=None, description="User ID assigned to manage list")
    due_date: int | None = Field(default=None, description="Due date in epoch milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    # Effective statuses for this list (if fetched via GET /list/{list_id})
    statuses: list[ListStatus] | None = Field(default=None, description="Available status definitions")

    @property
    def id(self) -> str:
        """
        Get the list ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the list ID via the 'id' property, even though the field is
        named 'list_id'.

        Returns:
            str: The list ID (same as list_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            lst = ClickUpList(id="list_123", name="My List")
            print(lst.id)  # "list_123"
            print(lst.list_id)  # "list_123" (same value)
        """
        return self.list_id

    # Behavior
    def rename(self, new_name: str) -> None:
        """
        Rename the list with validation.

        Updates the list name to a new value. Validates that the name
        is not empty or whitespace-only.

        Args:
            new_name: The new name for the list

        Raises:
            ValueError: If new_name is empty or contains only whitespace

        Usage Examples:
            # Python - Rename list
            lst = ClickUpList(id="list_123", name="Old Name")
            lst.rename("New Name")
            print(lst.name)  # "New Name"

            # Python - Error on empty name
            try:
                lst.rename("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not new_name or not new_name.strip():
            raise ValueError("List name cannot be empty")
        self.name = new_name

    def attach_to_folder(self, folder_id: str) -> None:
        """
        Attach list to a folder.

        Sets the folder_id for this list, establishing the relationship to a folder.
        Validates that the folder_id is not empty.

        Args:
            folder_id: The ID of the folder to attach this list to

        Raises:
            ValueError: If folder_id is empty or None

        Usage Examples:
            # Python - Attach list to folder
            lst = ClickUpList(id="list_123", name="My List")
            lst.attach_to_folder("folder_456")
            print(lst.folder_id)  # "folder_456"

            # Python - Error on empty folder_id
            try:
                lst.attach_to_folder("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not folder_id:
            raise ValueError("folder_id must be provided")
        self.folder_id = folder_id

    def attach_to_space(self, space_id: str) -> None:
        """
        Attach list to a space (for folderless lists).

        Sets the space_id for this list, establishing the relationship to a space.
        Validates that the space_id is not empty.

        Args:
            space_id: The ID of the space to attach this list to

        Raises:
            ValueError: If space_id is empty or None

        Usage Examples:
            # Python - Attach list to space
            lst = ClickUpList(id="list_123", name="My List")
            lst.attach_to_space("space_789")
            print(lst.space_id)  # "space_789"

            # Python - Error on empty space_id
            try:
                lst.attach_to_space("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not space_id:
            raise ValueError("space_id must be provided")
        self.space_id = space_id

    def assign_to(self, user_id: int | str | None) -> None:
        """
        Assign list to a user.

        Sets the assignee for this list. Accepts None to clear the assignment.

        Args:
            user_id: The user ID to assign to, or None to clear assignment

        Usage Examples:
            # Python - Assign list to user
            lst = ClickUpList(id="list_123", name="My List")
            lst.assign_to("user_456")
            print(lst.assignee_id)  # "user_456"

            # Python - Clear assignment
            lst.assign_to(None)
            print(lst.assignee_id)  # None

            # Python - Assign with integer ID
            lst.assign_to(123)
            print(lst.assignee_id)  # 123
        """
        self.assignee_id = user_id

    def schedule(self, due_ms: int, include_time: bool | None = None) -> None:
        """
        Schedule list with a due date.

        Sets the due date in epoch milliseconds. Validates that the due date
        is non-negative. The include_time parameter indicates whether time
        is included in the due date.

        Args:
            due_ms: Due date in epoch milliseconds
            include_time: Whether to include time in the due date (optional)

        Raises:
            ValueError: If due_ms is negative

        Usage Examples:
            # Python - Schedule list with due date
            lst = ClickUpList(id="list_123", name="My List")
            lst.schedule(1702080000000)  # Set due date
            print(lst.due_date)  # 1702080000000

            # Python - Schedule with time
            lst.schedule(1702080000000, include_time=True)
            print(lst.due_date_time)  # True

            # Python - Error on negative value
            try:
                lst.schedule(-1000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if due_ms < 0:
            raise ValueError("due date must be non-negative epoch ms")
        self.due_date = due_ms
        if include_time is not None:
            self.due_date_time = include_time


# Backwards compatibility alias
List = ClickUpList
