"""
Factory for creating Goal domain entities with validation.

Provides factory methods to create Goal instances with business rule validation.
This separates the creation logic from the domain model itself, following
the Factory pattern.
"""

from typing import Optional

from .goal import Goal


class GoalFactory:
    """
    Factory for creating Goal domain entities with validation.

    Provides static methods to create Goal instances with business rule validation.
    This ensures that all Goal instances are created with valid data according
    to domain rules.

    Usage Examples:
        # Python - Create a goal with factory
        from clickup_mcp.models.domain.goal_factory import GoalFactory

        goal = GoalFactory.create(
            goal_id="goal_123",
            team_id="team_001",
            name="Q1 Revenue Goal",
            due_date=1702080000000
        )
    """

    @staticmethod
    def create(
        goal_id: str,
        team_id: str,
        name: str,
        description: Optional[str] = None,
        due_date: Optional[int] = None,
        status: str = "active",
        key_results: Optional[list[str]] = None,
        owners: Optional[list[str]] = None,
        multiple_owners: bool = False,
        date_created: Optional[int] = None,
        date_updated: Optional[int] = None,
    ) -> Goal:
        """
        Create a Goal instance with validation.

        Creates a Goal domain entity after validating the input data according
        to business rules.

        Args:
            goal_id: The unique identifier for the goal
            team_id: Team/workspace ID this goal belongs to
            name: Goal name/title
            description: Description of the goal
            due_date: Due date in epoch milliseconds
            status: Goal status (default: "active")
            key_results: List of key result names
            owners: List of user IDs who own this goal
            multiple_owners: Whether multiple users can own this goal
            date_created: Creation date in epoch milliseconds
            date_updated: Last update date in epoch milliseconds

        Returns:
            Goal: A validated Goal domain entity

        Raises:
            ValueError: If validation fails

        Usage Examples:
            # Python - Create a goal with factory
            goal = GoalFactory.create(
                goal_id="goal_123",
                team_id="team_001",
                name="Q1 Revenue Goal",
                due_date=1702080000000
            )
        """
        # Validate required fields
        if not goal_id.strip():
            raise ValueError("goal_id cannot be empty string")
        if not team_id.strip():
            raise ValueError("team_id cannot be empty string")
        if not name.strip():
            raise ValueError("name cannot be empty string")

        # Validate status
        valid_statuses = {"active", "completed", "paused", "archived"}
        if status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")

        # Validate due_date
        if due_date is not None and due_date < 0:
            raise ValueError("due_date must be non-negative epoch ms")

        # Validate multiple_owners constraint
        if not multiple_owners and owners and len(owners) > 1:
            raise ValueError("cannot have multiple owners when multiple_owners is False")

        # Validate no duplicate owners
        if owners:
            unique_owners = set(owners)
            if len(unique_owners) != len(owners):
                raise ValueError("owners must be unique")

        # Validate no duplicate key results
        if key_results:
            unique_krs = set(key_results)
            if len(unique_krs) != len(key_results):
                raise ValueError("key_results must be unique")

        # Create and return the Goal instance
        return Goal(
            id=goal_id,
            team_id=team_id,
            name=name,
            description=description,
            due_date=due_date,
            status=status,
            key_results=key_results or [],
            owners=owners or [],
            multiple_owners=multiple_owners,
            date_created=date_created,
            date_updated=date_updated,
        )

    @staticmethod
    def from_dict(data: dict) -> Goal:
        """
        Create a Goal instance from a dictionary.

        Creates a Goal domain entity from a dictionary, typically from API responses.

        Args:
            data: Dictionary containing goal data

        Returns:
            Goal: A validated Goal domain entity

        Raises:
            ValueError: If validation fails or required fields are missing

        Usage Examples:
            # Python - Create from dictionary
            data = {
                "id": "goal_123",
                "team_id": "team_001",
                "name": "Q1 Revenue Goal",
                "due_date": 1702080000000
            }
            goal = GoalFactory.from_dict(data)
        """
        # Extract and validate required fields
        goal_id = data.get("id") or data.get("goal_id")
        if not goal_id:
            raise ValueError("goal_id is required")

        team_id = data.get("team_id")
        if not team_id:
            raise ValueError("team_id is required")

        name = data.get("name")
        if not name:
            raise ValueError("name is required")

        # Create the Goal instance
        return GoalFactory.create(
            goal_id=goal_id,
            team_id=team_id,
            name=name,
            description=data.get("description"),
            due_date=data.get("due_date"),
            status=data.get("status", "active"),
            key_results=data.get("key_results", []),
            owners=data.get("owners", []),
            multiple_owners=data.get("multiple_owners", False),
            date_created=data.get("date_created"),
            date_updated=data.get("date_updated"),
        )
