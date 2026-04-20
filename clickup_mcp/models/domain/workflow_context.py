"""
Domain model for ClickUp Workflow Context.

Represents a Workflow Context aggregate with business behaviors and invariants.
References related aggregates by identity only (workflow_id);
does not embed nested aggregates to maintain loose coupling.

A Workflow Context provides additional context information for workflow execution,
such as variables, conditions, and execution state.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., variable validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create a workflow context domain entity
    from clickup_mcp.models.domain.workflow_context import WorkflowContext

    context = WorkflowContext(
        id="ctx_123",
        workflow_id="wf_456",
        name="Production Context",
        variables={"priority": "high", "assignee": "user_789"}
    )

    # Python - Use domain behaviors
    context.set_variable("priority", "urgent")
    context.remove_variable("assignee")
"""

from typing import Dict

from pydantic import Field

from .base import BaseDomainModel


class WorkflowContext(BaseDomainModel):
    """
    Domain model for a ClickUp Workflow Context with core behaviors and invariants.

    This model represents a workflow context in ClickUp and includes all relevant fields
    from the ClickUp API. A Workflow Context provides additional context information
    for workflow execution.

    In ClickUp's hierarchy:
    - Team (workspace) → Workflow Automation → Context

    Attributes:
        context_id: The unique identifier for the context (aliased as 'id' for compatibility)
        workflow_id: The ID of the workflow this context belongs to
        name: Context name
        description: Description of the context
        variables: Dictionary of context variables
        conditions: List of execution conditions
        is_active: Whether the context is active
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns context_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.workflow_context import WorkflowContext

        context = WorkflowContext(
            id="ctx_123",
            workflow_id="wf_456",
            name="Production Context",
            variables={"priority": "high", "assignee": "user_789"},
            is_active=True
        )

        # Python - Use domain behaviors
        context.set_variable("priority", "urgent")
        context.remove_variable("assignee")
    """

    context_id: str = Field(alias="id", description="The unique identifier for the context")
    workflow_id: str = Field(description="Workflow ID this context belongs to")
    name: str = Field(description="Context name")
    description: str | None = Field(default=None, description="Description of the context")
    variables: Dict[str, str] = Field(default_factory=dict, description="Dictionary of context variables")
    conditions: list = Field(default_factory=list, description="List of execution conditions")
    is_active: bool = Field(default=True, description="Whether the context is active")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")

    @property
    def id(self) -> str:
        """
        Get the context ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the context ID via the 'id' property, even though the field is
        named 'context_id'.

        Returns:
            str: The context ID (same as context_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production")
            print(context.id)  # "ctx_123"
            print(context.context_id)  # "ctx_123" (same value)
        """
        return self.context_id

    # Behaviors / Invariants
    def update_name(self, name: str) -> None:
        """
        Update the context name.

        Updates the name to a new value. Validates that the name is not empty.

        Args:
            name: The new context name

        Raises:
            ValueError: If name is an empty string

        Usage Examples:
            # Python - Update name
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production")
            context.update_name("Staging Context")
            print(context.name)  # "Staging Context"
        """
        if not name.strip():
            raise ValueError("name cannot be empty string")
        self.name = name

    def update_description(self, description: str | None) -> None:
        """
        Update the context description.

        Updates the description to a new value. Accepts None to clear the description.

        Args:
            description: The new description or None to clear

        Usage Examples:
            # Python - Update description
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production")
            context.update_description("Updated description")
            print(context.description)  # "Updated description"
        """
        self.description = description

    def set_variable(self, key: str, value: str) -> None:
        """
        Set a context variable.

        Adds or updates a context variable.

        Args:
            key: Variable key
            value: Variable value

        Raises:
            ValueError: If key is empty

        Usage Examples:
            # Python - Set variable
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production")
            context.set_variable("priority", "urgent")
            print(context.variables)  # {"priority": "urgent"}
        """
        if not key.strip():
            raise ValueError("variable key cannot be empty")
        self.variables[key] = value

    def remove_variable(self, key: str) -> None:
        """
        Remove a context variable.

        Removes a context variable if it exists.

        Args:
            key: Variable key to remove

        Raises:
            ValueError: If key does not exist

        Usage Examples:
            # Python - Remove variable
            context = WorkflowContext(
                id="ctx_123",
                workflow_id="wf_456",
                name="Production",
                variables={"priority": "urgent"}
            )
            context.remove_variable("priority")
            print(context.variables)  # {}
        """
        if key not in self.variables:
            raise ValueError(f"variable '{key}' not found")
        del self.variables[key]

    def set_variables(self, variables: Dict[str, str]) -> None:
        """
        Set all context variables.

        Replaces all variables with the provided dictionary.

        Args:
            variables: New variables dictionary

        Usage Examples:
            # Python - Set all variables
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production")
            context.set_variables({"priority": "urgent", "assignee": "user_789"})
            print(context.variables)  # {"priority": "urgent", "assignee": "user_789"}
        """
        self.variables = variables

    def add_condition(self, condition: str) -> None:
        """
        Add an execution condition.

        Adds a condition to the conditions list.

        Args:
            condition: Condition to add

        Raises:
            ValueError: If condition is empty or already exists

        Usage Examples:
            # Python - Add condition
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production")
            context.add_condition("status == 'open'")
            print(context.conditions)  # ["status == 'open'"]
        """
        if not condition:
            raise ValueError("condition cannot be empty")
        if condition in self.conditions:
            raise ValueError(f"condition '{condition}' already exists")
        self.conditions.append(condition)

    def remove_condition(self, condition: str) -> None:
        """
        Remove an execution condition.

        Removes a condition from the conditions list.

        Args:
            condition: Condition to remove

        Raises:
            ValueError: If condition is not in the list

        Usage Examples:
            # Python - Remove condition
            context = WorkflowContext(
                id="ctx_123",
                workflow_id="wf_456",
                name="Production",
                conditions=["status == 'open'"]
            )
            context.remove_condition("status == 'open'")
            print(context.conditions)  # []
        """
        if condition not in self.conditions:
            raise ValueError(f"condition '{condition}' not found")
        self.conditions.remove(condition)

    def activate(self) -> None:
        """
        Activate the context.

        Sets the context to active status.

        Usage Examples:
            # Python - Activate context
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production", is_active=False)
            context.activate()
            print(context.is_active)  # True
        """
        self.is_active = True

    def deactivate(self) -> None:
        """
        Deactivate the context.

        Sets the context to inactive status.

        Usage Examples:
            # Python - Deactivate context
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production", is_active=True)
            context.deactivate()
            print(context.is_active)  # False
        """
        self.is_active = False

    def is_active_context(self) -> bool:
        """
        Check if the context is active.

        Returns:
            bool: True if the context is active

        Usage Examples:
            # Python - Check if active
            context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Production", is_active=True)
            print(context.is_active_context())  # True
        """
        return self.is_active
