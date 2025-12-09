"""
Domain model for ClickUp Task.

Represents a Task aggregate with business behaviors and invariants.
References related aggregates by identity only (list_id, folder_id, space_id);
does not embed nested aggregates to maintain loose coupling.

A Task is the fundamental unit of work in ClickUp. Tasks can be organized
into Lists, which are contained in Folders, which are contained in Spaces.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., priority validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)
- Maintains a neutral representation for custom fields

Usage Examples:
    # Python - Create a task domain entity
    from clickup_mcp.models.domain.task import ClickUpTask

    task = ClickUpTask(
        id="task_123",
        name="Implement feature",
        status="In Progress",
        priority=2,
        list_id="list_456",
        assignee_ids=["user_789"]
    )

    # Python - Use domain behaviors
    task.change_status("Done")
    task.set_priority(1)
    task.assign("user_789", "user_790")

    # Python - Access task properties
    print(task.name)  # "Implement feature"
    print(task.priority)  # 1
    print(task.assignee_ids)  # ["user_789", "user_790"]
"""

from typing import List

from pydantic import Field

from .base import BaseDomainModel


class ClickUpTask(BaseDomainModel):
    """
    Domain model for a ClickUp Task with core behaviors and invariants.

    This model represents a Task in ClickUp and includes all relevant fields
    from the ClickUp API. A Task is the fundamental unit of work, containing
    details about what needs to be done, who should do it, and when.

    In ClickUp's hierarchy:
    - Team (workspace) → Space → Folder → List → Task

    Attributes:
        task_id: The unique identifier for the task (aliased as 'id' for compatibility)
        name: The name/title of the task
        status: The current status label (e.g., "Open", "In Progress", "Done")
        priority: Priority level (1-4, where 1 is highest)
        list_id: The ID of the list this task belongs to
        folder_id: The ID of the folder containing the list
        space_id: The ID of the space containing the folder
        parent_id: The ID of the parent task (for subtasks)
        assignee_ids: List of user IDs assigned to this task
        due_date: Due date in epoch milliseconds
        time_estimate: Time estimate in epoch milliseconds
        custom_fields: List of custom field values

    Key Design Features:
    - Backward-compatible 'id' property that returns task_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Neutral representation for custom fields (mapping layer handles DTO conversion)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.task import ClickUpTask

        task = ClickUpTask(
            id="task_123",
            name="Implement authentication",
            status="In Progress",
            priority=2,
            list_id="list_456",
            space_id="space_789",
            assignee_ids=["user_111"],
            due_date=1702080000000,  # epoch ms
            time_estimate=3600000  # 1 hour in ms
        )

        # Python - Use domain behaviors
        task.change_status("Done")
        task.set_priority(1)
        task.assign("user_111", "user_222")
        task.set_estimate(7200000)  # 2 hours
        task.schedule(1702166400000)  # Set due date

        # Python - Access task properties
        print(task.name)  # "Implement authentication"
        print(task.priority)  # 1
        print(task.status)  # "Done"
        print(task.assignee_ids)  # ["user_111", "user_222"]
    """

    task_id: str = Field(alias="id", description="The unique identifier for the task")
    name: str = Field(description="Task name")

    # Simple, vendor-agnostic attributes
    status: str | None = Field(default=None, description="Task status label")
    priority: int | None = Field(default=None, description="Priority level (1-4)")

    # Relationships by identity only
    list_id: str | None = Field(default=None, description="The list this task belongs to")
    folder_id: str | None = Field(default=None, description="The folder containing the list")
    space_id: str | None = Field(default=None, description="The space containing the folder")
    parent_id: str | None = Field(default=None, description="Parent task ID (for subtasks)")

    assignee_ids: List[int | str] = Field(default_factory=list, description="User IDs assigned to this task")

    # Time fields in epoch ms
    due_date: int | None = Field(default=None, description="Due date in epoch milliseconds")
    time_estimate: int | None = Field(default=None, description="Time estimate in epoch milliseconds")

    # Neutral representation; mapping layer will translate to DTO shapes
    custom_fields: list[dict] = Field(default_factory=list, description="Custom field values")

    @property
    def id(self) -> str:
        """
        Get the task ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the task ID via the 'id' property, even though the field is
        named 'task_id'.

        Returns:
            str: The task ID (same as task_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            task = ClickUpTask(id="task_123", name="My Task")
            print(task.id)  # "task_123"
            print(task.task_id)  # "task_123" (same value)
        """
        return self.task_id

    # Behaviors / Invariants
    def change_status(self, new_status: str | None) -> None:
        """
        Change task status with validation.

        Updates the task status to a new value. Accepts None to clear the status.
        Validates that non-None status values are not empty strings.

        Args:
            new_status: The new status label (e.g., "Open", "In Progress", "Done")
                       or None to clear the status

        Raises:
            ValueError: If new_status is an empty string

        Usage Examples:
            # Python - Change task status
            task = ClickUpTask(id="task_123", name="My Task")
            task.change_status("In Progress")
            print(task.status)  # "In Progress"

            # Python - Clear status
            task.change_status(None)
            print(task.status)  # None

            # Python - Error on empty string
            try:
                task.change_status("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if new_status is not None and not new_status.strip():
            raise ValueError("status cannot be empty string")
        self.status = new_status

    def attach_to_list(self, list_id: str) -> None:
        """
        Attach task to a list.

        Sets the list_id for this task, establishing the relationship to a list.
        Validates that the list_id is not empty.

        Args:
            list_id: The ID of the list to attach this task to

        Raises:
            ValueError: If list_id is empty or None

        Usage Examples:
            # Python - Attach task to a list
            task = ClickUpTask(id="task_123", name="My Task")
            task.attach_to_list("list_456")
            print(task.list_id)  # "list_456"

            # Python - Error on empty list_id
            try:
                task.attach_to_list("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not list_id:
            raise ValueError("list_id must be provided")
        self.list_id = list_id

    def set_estimate(self, ms: int | None) -> None:
        """
        Set time estimate for the task.

        Updates the time estimate in epoch milliseconds. Validates that
        the estimate is non-negative.

        Args:
            ms: Time estimate in milliseconds, or None to clear the estimate

        Raises:
            ValueError: If ms is negative

        Usage Examples:
            # Python - Set time estimate
            task = ClickUpTask(id="task_123", name="My Task")
            task.set_estimate(3600000)  # 1 hour
            print(task.time_estimate)  # 3600000

            # Python - Clear estimate
            task.set_estimate(None)
            print(task.time_estimate)  # None

            # Python - Error on negative value
            try:
                task.set_estimate(-1000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if ms is not None and ms < 0:
            raise ValueError("estimate must be non-negative epoch ms")
        self.time_estimate = ms

    def schedule(self, due_ms: int | None, include_time: bool | None = None) -> None:
        """
        Schedule task with a due date.

        Sets the due date in epoch milliseconds. Validates that the due date
        is non-negative. The include_time parameter is transport-specific and
        not stored in the domain model.

        Args:
            due_ms: Due date in epoch milliseconds, or None to clear the due date
            include_time: Whether to include time in the due date (transport-specific,
                         not stored in domain model)

        Raises:
            ValueError: If due_ms is negative

        Usage Examples:
            # Python - Schedule task with due date
            task = ClickUpTask(id="task_123", name="My Task")
            task.schedule(1702080000000)  # Set due date
            print(task.due_date)  # 1702080000000

            # Python - Clear due date
            task.schedule(None)
            print(task.due_date)  # None

            # Python - Error on negative value
            try:
                task.schedule(-1000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if due_ms is not None and due_ms < 0:
            raise ValueError("due date must be non-negative epoch ms")
        self.due_date = due_ms
        # include_time is relevant to transport; domain stores due_date only

    def set_priority(self, value: int | None) -> None:
        """
        Set task priority with validation.

        Updates the task priority to a value between 1 and 4 (1 is highest).
        Accepts None to clear the priority.

        Args:
            value: Priority level (1-4) or None to clear priority

        Raises:
            ValueError: If value is not in range 1-4 (when not None)

        Usage Examples:
            # Python - Set task priority
            task = ClickUpTask(id="task_123", name="My Task")
            task.set_priority(1)  # Highest priority
            print(task.priority)  # 1

            # Python - Clear priority
            task.set_priority(None)
            print(task.priority)  # None

            # Python - Error on invalid priority
            try:
                task.set_priority(5)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if value is not None and (value < 1 or value > 4):
            raise ValueError("priority must be between 1 and 4")
        self.priority = value

    def assign(self, *user_ids: int | str) -> None:
        """
        Assign task to one or more users.

        Replaces the existing assignees with the provided user IDs.
        Accepts variable number of user IDs.

        Args:
            *user_ids: Variable number of user IDs to assign to this task

        Usage Examples:
            # Python - Assign to single user
            task = ClickUpTask(id="task_123", name="My Task")
            task.assign("user_789")
            print(task.assignee_ids)  # ["user_789"]

            # Python - Assign to multiple users
            task.assign("user_789", "user_790", "user_791")
            print(task.assignee_ids)  # ["user_789", "user_790", "user_791"]

            # Python - Clear assignments
            task.assign()  # No arguments
            print(task.assignee_ids)  # []

            # Python - Replace existing assignments
            task.assign("user_111")  # Replaces previous assignments
            print(task.assignee_ids)  # ["user_111"]
        """
        # Replace existing assignees with provided
        self.assignee_ids = list(user_ids)


# Backwards compatibility alias
Task = ClickUpTask
