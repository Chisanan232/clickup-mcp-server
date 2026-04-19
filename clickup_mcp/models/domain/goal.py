"""
Domain model for ClickUp Goal.

Represents a Goal aggregate with business behaviors and invariants.
References related aggregates by identity only (team_id, owner_id);
does not embed nested aggregates to maintain loose coupling.

A Goal represents a high-level objective that can be tracked with key results.
Goals are part of ClickUp's OKR (Objectives and Key Results) framework.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., due date validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create a goal domain entity
    from clickup_mcp.models.domain.goal import Goal

    goal = Goal(
        id="goal_123",
        team_id="team_001",
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
        status="active"
    )

    # Python - Use domain behaviors
    goal.update_name("Updated Goal Name")
    goal.set_status("completed")
    goal.set_due_date(1702166400000)
"""

from pydantic import Field

from .base import BaseDomainModel


class Goal(BaseDomainModel):
    """
    Domain model for a ClickUp Goal with core behaviors and invariants.

    This model represents a goal in ClickUp and includes all relevant fields
    from the ClickUp API. A Goal tracks high-level objectives that can be
    measured with key results.

    In ClickUp's hierarchy:
    - Team (workspace) → Goal

    Attributes:
        goal_id: The unique identifier for the goal (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace this goal belongs to
        name: Goal name/title
        description: Description of the goal
        due_date: Due date in epoch milliseconds
        status: Goal status (e.g., "active", "completed", "paused")
        key_results: List of key result names
        owners: List of user IDs who own this goal
        multiple_owners: Whether multiple users can own this goal
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns goal_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.goal import Goal

        goal = Goal(
            id="goal_123",
            team_id="team_001",
            name="Q1 Revenue Goal",
            description="Achieve $1M in revenue",
            due_date=1702080000000,
            status="active"
        )

        # Python - Use domain behaviors
        goal.update_name("Updated Goal Name")
        goal.set_status("completed")
        goal.set_due_date(1702166400000)

        # Python - Access goal properties
        print(goal.name)  # "Updated Goal Name"
        print(goal.status)  # "completed"
    """

    goal_id: str = Field(alias="id", description="The unique identifier for the goal")
    team_id: str = Field(description="Team/workspace ID this goal belongs to")
    name: str = Field(description="Goal name/title")
    description: str | None = Field(default=None, description="Description of the goal")
    due_date: int | None = Field(default=None, description="Due date in epoch milliseconds")
    status: str = Field(default="active", description="Goal status (e.g., 'active', 'completed', 'paused')")
    key_results: list[str] = Field(default_factory=list, description="List of key result names")
    owners: list[str] = Field(default_factory=list, description="List of user IDs who own this goal")
    multiple_owners: bool = Field(default=False, description="Whether multiple users can own this goal")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")

    @property
    def id(self) -> str:
        """
        Get the goal ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the goal ID via the 'id' property, even though the field is
        named 'goal_id'.

        Returns:
            str: The goal ID (same as goal_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            print(goal.id)  # "goal_123"
            print(goal.goal_id)  # "goal_123" (same value)
        """
        return self.goal_id

    # Behaviors / Invariants
    def update_name(self, name: str) -> None:
        """
        Update the goal name.

        Updates the name to a new value. Validates that the name is not empty.

        Args:
            name: The new goal name

        Raises:
            ValueError: If name is an empty string

        Usage Examples:
            # Python - Update name
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.update_name("Updated Goal Name")
            print(goal.name)  # "Updated Goal Name"

            # Python - Error on empty string
            try:
                goal.update_name("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not name.strip():
            raise ValueError("name cannot be empty string")
        self.name = name

    def update_description(self, description: str | None) -> None:
        """
        Update the goal description.

        Updates the description to a new value. Accepts None to clear the description.
        Validates that non-None description values are not empty strings.

        Args:
            description: The new description or None to clear

        Raises:
            ValueError: If description is an empty string

        Usage Examples:
            # Python - Update description
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.update_description("Updated description")
            print(goal.description)  # "Updated description"

            # Python - Clear description
            goal.update_description(None)
            print(goal.description)  # None
        """
        if description is not None and not description.strip():
            raise ValueError("description cannot be empty string")
        self.description = description

    def set_status(self, status: str) -> None:
        """
        Set the goal status.

        Updates the goal status. Validates that the status is one of the valid values.

        Args:
            status: The new status (e.g., "active", "completed", "paused")

        Raises:
            ValueError: If status is not a valid value

        Usage Examples:
            # Python - Set status
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.set_status("completed")
            print(goal.status)  # "completed"
        """
        valid_statuses = {"active", "completed", "paused", "archived"}
        if status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
        self.status = status

    def set_due_date(self, due_date: int | None) -> None:
        """
        Set the due date of the goal.

        Updates the due date in epoch milliseconds. Validates that
        the due date is non-negative.

        Args:
            due_date: Due date in epoch milliseconds, or None to clear

        Raises:
            ValueError: If due_date is negative

        Usage Examples:
            # Python - Set due date
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.set_due_date(1702080000000)
            print(goal.due_date)  # 1702080000000

            # Python - Clear due date
            goal.set_due_date(None)
            print(goal.due_date)  # None

            # Python - Error on negative value
            try:
                goal.set_due_date(-1000)  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if due_date is not None and due_date < 0:
            raise ValueError("due_date must be non-negative epoch ms")
        self.due_date = due_date

    def add_key_result(self, key_result: str) -> None:
        """
        Add a key result to the goal.

        Adds a new key result to the goal's key results list.

        Args:
            key_result: The key result name to add

        Raises:
            ValueError: If key_result is an empty string or already exists

        Usage Examples:
            # Python - Add key result
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.add_key_result("Increase MRR by 20%")
            print(goal.key_results)  # ["Increase MRR by 20%"]
        """
        if not key_result.strip():
            raise ValueError("key_result cannot be empty string")
        if key_result in self.key_results:
            raise ValueError(f"key_result '{key_result}' already exists")
        self.key_results.append(key_result)

    def remove_key_result(self, key_result: str) -> None:
        """
        Remove a key result from the goal.

        Removes a key result from the goal's key results list.

        Args:
            key_result: The key result name to remove

        Raises:
            ValueError: If key_result is not in the list

        Usage Examples:
            # Python - Remove key result
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.add_key_result("Increase MRR by 20%")
            goal.remove_key_result("Increase MRR by 20%")
            print(goal.key_results)  # []
        """
        if key_result not in self.key_results:
            raise ValueError(f"key_result '{key_result}' not found")
        self.key_results.remove(key_result)

    def add_owner(self, owner_id: str) -> None:
        """
        Add an owner to the goal.

        Adds a new owner to the goal's owners list.

        Args:
            owner_id: The user ID to add as an owner

        Raises:
            ValueError: If owner_id is an empty string or already exists

        Usage Examples:
            # Python - Add owner
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.add_owner("user_123")
            print(goal.owners)  # ["user_123"]
        """
        if not owner_id.strip():
            raise ValueError("owner_id cannot be empty string")
        if owner_id in self.owners:
            raise ValueError(f"owner_id '{owner_id}' already exists")
        if not self.multiple_owners and self.owners:
            raise ValueError("cannot add multiple owners when multiple_owners is False")
        self.owners.append(owner_id)

    def remove_owner(self, owner_id: str) -> None:
        """
        Remove an owner from the goal.

        Removes an owner from the goal's owners list.

        Args:
            owner_id: The user ID to remove

        Raises:
            ValueError: If owner_id is not in the list

        Usage Examples:
            # Python - Remove owner
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal")
            goal.add_owner("user_123")
            goal.remove_owner("user_123")
            print(goal.owners)  # []
        """
        if owner_id not in self.owners:
            raise ValueError(f"owner_id '{owner_id}' not found")
        self.owners.remove(owner_id)

    def is_active(self) -> bool:
        """
        Check if the goal is currently active.

        Returns:
            bool: True if the goal status is "active"

        Usage Examples:
            # Python - Check if active
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal", status="active")
            print(goal.is_active())  # True

            goal.set_status("completed")
            print(goal.is_active())  # False
        """
        return self.status == "active"

    def is_completed(self) -> bool:
        """
        Check if the goal is completed.

        Returns:
            bool: True if the goal status is "completed"

        Usage Examples:
            # Python - Check if completed
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal", status="completed")
            print(goal.is_completed())  # True

            goal.set_status("active")
            print(goal.is_completed())  # False
        """
        return self.status == "completed"

    def is_overdue(self) -> bool:
        """
        Check if the goal is overdue (past due date and not completed).

        Returns:
            bool: True if the goal is overdue

        Usage Examples:
            # Python - Check if overdue
            import time
            goal = Goal(id="goal_123", team_id="team_001", name="Q1 Revenue Goal", due_date=int(time.time() * 1000) - 100000)
            print(goal.is_overdue())  # True (if due date is in the past and not completed)
        """
        if self.due_date is None or self.status == "completed":
            return False
        import time

        return self.due_date < int(time.time() * 1000)
