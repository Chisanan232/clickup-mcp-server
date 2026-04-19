"""
Domain model for ClickUp Key Result.

Represents a Key Result aggregate with business behaviors and invariants.
References related aggregates by identity only (goal_id);
does not embed nested aggregates to maintain loose coupling.

A Key Result represents a measurable outcome that tracks progress toward a goal.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., target validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses vendor-agnostic types

Usage Examples:
    # Python - Create a key result domain entity
    from clickup_mcp.models.domain.key_result import KeyResult

    kr = KeyResult(
        id="kr_123",
        goal_id="goal_456",
        name="Increase MRR",
        type="currency",
        target=1000000,
        current=500000,
        unit="$"
    )

    # Python - Use domain behaviors
    kr.update_current(750000)
    kr.set_target(2000000)
"""

from pydantic import Field

from .base import BaseDomainModel


class KeyResult(BaseDomainModel):
    """
    Domain model for a ClickUp Key Result with core behaviors and invariants.

    This model represents a key result in ClickUp and includes all relevant fields
    from the ClickUp API. A Key Result tracks measurable progress toward a goal.

    In ClickUp's hierarchy:
    - Goal → Key Result

    Attributes:
        key_result_id: The unique identifier for the key result (aliased as 'id' for compatibility)
        goal_id: The ID of the goal this key result belongs to
        name: Key result name
        type: Key result type (e.g., "number", "currency", "boolean")
        target: Target value for the key result
        current: Current value for the key result
        unit: Unit of measurement
        description: Description of the key result
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns key_result_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.key_result import KeyResult

        kr = KeyResult(
            id="kr_123",
            goal_id="goal_456",
            name="Increase MRR",
            type="currency",
            target=1000000,
            current=500000,
            unit="$"
        )

        # Python - Use domain behaviors
        kr.update_current(750000)
        kr.set_target(2000000)

        # Python - Access key result properties
        print(kr.current)  # 750000
        print(kr.target)  # 2000000
    """

    key_result_id: str = Field(alias="id", description="The unique identifier for the key result")
    goal_id: str = Field(description="Goal ID this key result belongs to")
    name: str = Field(description="Key result name")
    type: str = Field(default="number", description="Key result type (e.g., 'number', 'currency', 'boolean')")
    target: float = Field(description="Target value for the key result")
    current: float = Field(default=0.0, description="Current value for the key result")
    unit: str | None = Field(default=None, description="Unit of measurement")
    description: str | None = Field(default=None, description="Description of the key result")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")

    @property
    def id(self) -> str:
        """
        Get the key result ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the key result ID via the 'id' property, even though the field is
        named 'key_result_id'.

        Returns:
            str: The key result ID (same as key_result_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000)
            print(kr.id)  # "kr_123"
            print(kr.key_result_id)  # "kr_123" (same value)
        """
        return self.key_result_id

    # Behaviors / Invariants
    def update_name(self, name: str) -> None:
        """
        Update the key result name.

        Updates the name to a new value. Validates that the name is not empty.

        Args:
            name: The new key result name

        Raises:
            ValueError: If name is an empty string

        Usage Examples:
            # Python - Update name
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000)
            kr.update_name("Updated Key Result Name")
            print(kr.name)  # "Updated Key Result Name"
        """
        if not name.strip():
            raise ValueError("name cannot be empty string")
        self.name = name

    def set_target(self, target: float) -> None:
        """
        Set the target value of the key result.

        Updates the target value. Validates that the target is non-negative.

        Args:
            target: Target value

        Raises:
            ValueError: If target is negative

        Usage Examples:
            # Python - Set target
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000)
            kr.set_target(2000000)
            print(kr.target)  # 2000000
        """
        if target < 0:
            raise ValueError("target must be non-negative")
        self.target = target

    def update_current(self, current: float) -> None:
        """
        Update the current value of the key result.

        Updates the current value. Validates that the current value is non-negative.

        Args:
            current: Current value

        Raises:
            ValueError: If current is negative

        Usage Examples:
            # Python - Update current value
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000)
            kr.update_current(750000)
            print(kr.current)  # 750000
        """
        if current < 0:
            raise ValueError("current must be non-negative")
        self.current = current

    def update_description(self, description: str | None) -> None:
        """
        Update the key result description.

        Updates the description to a new value. Accepts None to clear the description.

        Args:
            description: The new description or None to clear

        Usage Examples:
            # Python - Update description
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000)
            kr.update_description("Updated description")
            print(kr.description)  # "Updated description"
        """
        self.description = description

    def set_unit(self, unit: str | None) -> None:
        """
        Set the unit of measurement for the key result.

        Updates the unit of measurement.

        Args:
            unit: Unit of measurement or None to clear

        Usage Examples:
            # Python - Set unit
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000)
            kr.set_unit("$")
            print(kr.unit)  # "$"
        """
        self.unit = unit

    def get_progress_percentage(self) -> float:
        """
        Calculate the progress percentage toward the target.

        Returns:
            float: Progress percentage (0-100)

        Usage Examples:
            # Python - Calculate progress
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000, current=500000)
            progress = kr.get_progress_percentage()
            print(progress)  # 50.0
        """
        if self.target == 0:
            return 0.0
        progress = (self.current / self.target) * 100
        return min(progress, 100.0)

    def is_completed(self) -> bool:
        """
        Check if the key result is completed (current >= target).

        Returns:
            bool: True if the key result is completed

        Usage Examples:
            # Python - Check if completed
            kr = KeyResult(id="kr_123", goal_id="goal_456", name="Increase MRR", target=1000000, current=1000000)
            print(kr.is_completed())  # True
        """
        return self.current >= self.target
