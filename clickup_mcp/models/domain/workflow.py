"""
Domain model for ClickUp Workflow Automation.

Represents a Workflow Automation aggregate with business behaviors and invariants.
References related aggregates by identity only (team_id);
does not embed nested aggregates to maintain loose coupling.

A Workflow Automation is a rule that triggers actions based on events in ClickUp.
It allows for automating repetitive tasks and maintaining consistent processes.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., trigger validation)
- References other aggregates by ID only (no embedded objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create a workflow domain entity
    from clickup_mcp.models.domain.workflow import Workflow

    workflow = Workflow(
        id="wf_123",
        team_id="team_001",
        name="Auto-assign on create",
        trigger_type="task_created",
        trigger_config={"list_id": "456"},
        actions=[{"type": "assign", "user_id": "789"}]
    )

    # Python - Use domain behaviors
    workflow.activate()
    workflow.deactivate()
    workflow.update_name("Updated name")
"""

from typing import List

from pydantic import Field

from .base import BaseDomainModel


class Workflow(BaseDomainModel):
    """
    Domain model for a ClickUp Workflow Automation with core behaviors and invariants.

    This model represents a workflow automation in ClickUp and includes all relevant fields
    from the ClickUp API. A Workflow Automation is a rule that triggers actions based on events.

    In ClickUp's hierarchy:
    - Team (workspace) → Workflow Automation

    Attributes:
        workflow_id: The unique identifier for the workflow (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace this workflow belongs to
        name: Workflow automation name
        description: Description of the automation
        trigger_type: Type of trigger (e.g., task_created, status_changed)
        trigger_config: Configuration for the trigger
        actions: List of actions to execute
        is_active: Whether the workflow is active
        priority: Execution priority
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns workflow_id
    - Behavior methods that enforce domain invariants
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.workflow import Workflow

        workflow = Workflow(
            id="wf_123",
            team_id="team_001",
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "456"},
            actions=[{"type": "assign", "user_id": "789"}],
            is_active=True
        )

        # Python - Use domain behaviors
        workflow.activate()
        workflow.deactivate()
        workflow.update_name("Updated name")
    """

    workflow_id: str = Field(alias="id", description="The unique identifier for the workflow")
    team_id: str = Field(description="Team/workspace ID this workflow belongs to")
    name: str = Field(description="Workflow automation name")
    description: str | None = Field(default=None, description="Description of the automation")
    trigger_type: str = Field(description="Type of trigger (e.g., 'task_created', 'status_changed')")
    trigger_config: dict = Field(default_factory=dict, description="Configuration for the trigger")
    actions: List[dict] = Field(default_factory=list, description="List of actions to execute")
    is_active: bool = Field(default=True, description="Whether the workflow is active")
    priority: int | None = Field(default=None, description="Execution priority")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")

    @property
    def id(self) -> str:
        """
        Get the workflow ID for backward compatibility.

        This property provides backward compatibility by allowing access
        to the workflow ID via the 'id' property, even though the field is
        named 'workflow_id'.

        Returns:
            str: The workflow ID (same as workflow_id)

        Usage Examples:
            # Python - Access via backward-compatible id property
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            print(workflow.id)  # "wf_123"
            print(workflow.workflow_id)  # "wf_123" (same value)
        """
        return self.workflow_id

    # Behaviors / Invariants
    def update_name(self, name: str) -> None:
        """
        Update the workflow name.

        Updates the name to a new value. Validates that the name is not empty.

        Args:
            name: The new workflow name

        Raises:
            ValueError: If name is an empty string

        Usage Examples:
            # Python - Update name
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.update_name("Updated Workflow Name")
            print(workflow.name)  # "Updated Workflow Name"

            # Python - Error on empty string
            try:
                workflow.update_name("")  # Raises ValueError
            except ValueError as e:
                print(f"Error: {e}")
        """
        if not name.strip():
            raise ValueError("name cannot be empty string")
        self.name = name

    def update_description(self, description: str | None) -> None:
        """
        Update the workflow description.

        Updates the description to a new value. Accepts None to clear the description.
        Validates that non-None description values are not empty strings.

        Args:
            description: The new description or None to clear

        Raises:
            ValueError: If description is an empty string

        Usage Examples:
            # Python - Update description
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.update_description("Updated description")
            print(workflow.description)  # "Updated description"

            # Python - Clear description
            workflow.update_description(None)
            print(workflow.description)  # None
        """
        if description is not None and not description.strip():
            raise ValueError("description cannot be empty string")
        self.description = description

    def set_trigger_type(self, trigger_type: str) -> None:
        """
        Set the trigger type.

        Updates the trigger type. Validates that the trigger type is one of the valid values.

        Args:
            trigger_type: The new trigger type (e.g., "task_created", "status_changed")

        Raises:
            ValueError: If trigger_type is an empty string

        Usage Examples:
            # Python - Set trigger type
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.set_trigger_type("status_changed")
            print(workflow.trigger_type)  # "status_changed"
        """
        if not trigger_type.strip():
            raise ValueError("trigger_type cannot be empty string")
        self.trigger_type = trigger_type

    def set_trigger_config(self, trigger_config: dict) -> None:
        """
        Set the trigger configuration.

        Updates the trigger configuration.

        Args:
            trigger_config: The new trigger configuration

        Usage Examples:
            # Python - Set trigger config
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.set_trigger_config({"list_id": "456"})
            print(workflow.trigger_config)  # {"list_id": "456"}
        """
        self.trigger_config = trigger_config

    def set_actions(self, actions: List[dict]) -> None:
        """
        Set the actions to execute.

        Updates the list of actions to execute when the workflow triggers.

        Args:
            actions: The new list of actions

        Usage Examples:
            # Python - Set actions
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.set_actions([{"type": "assign", "user_id": "789"}])
            print(workflow.actions)  # [{"type": "assign", "user_id": "789"}]
        """
        self.actions = actions

    def add_action(self, action: dict) -> None:
        """
        Add an action to the workflow.

        Adds a new action to the workflow's actions list.

        Args:
            action: The action to add

        Raises:
            ValueError: If action is empty or already exists

        Usage Examples:
            # Python - Add action
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.add_action({"type": "assign", "user_id": "789"})
            print(workflow.actions)  # [{"type": "assign", "user_id": "789"}]
        """
        if not action:
            raise ValueError("action cannot be empty")
        if action in self.actions:
            raise ValueError(f"action '{action}' already exists")
        self.actions.append(action)

    def remove_action(self, action: dict) -> None:
        """
        Remove an action from the workflow.

        Removes an action from the workflow's actions list.

        Args:
            action: The action to remove

        Raises:
            ValueError: If action is not in the list

        Usage Examples:
            # Python - Remove action
            workflow = Workflow(
                id="wf_123",
                team_id="team_001",
                name="Auto-assign",
                actions=[{"type": "assign", "user_id": "789"}]
            )
            workflow.remove_action({"type": "assign", "user_id": "789"})
            print(workflow.actions)  # []
        """
        if action not in self.actions:
            raise ValueError(f"action '{action}' not found")
        self.actions.remove(action)

    def activate(self) -> None:
        """
        Activate the workflow.

        Sets the workflow to active status, enabling it to execute when triggered.

        Usage Examples:
            # Python - Activate workflow
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign", is_active=False)
            workflow.activate()
            print(workflow.is_active)  # True
        """
        self.is_active = True

    def deactivate(self) -> None:
        """
        Deactivate the workflow.

        Sets the workflow to inactive status, disabling it from executing when triggered.

        Usage Examples:
            # Python - Deactivate workflow
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign", is_active=True)
            workflow.deactivate()
            print(workflow.is_active)  # False
        """
        self.is_active = False

    def set_priority(self, priority: int) -> None:
        """
        Set the execution priority.

        Updates the workflow's execution priority.

        Args:
            priority: The new priority value

        Raises:
            ValueError: If priority is negative

        Usage Examples:
            # Python - Set priority
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign")
            workflow.set_priority(1)
            print(workflow.priority)  # 1
        """
        if priority < 0:
            raise ValueError("priority must be non-negative")
        self.priority = priority

    def is_active_workflow(self) -> bool:
        """
        Check if the workflow is active.

        Returns:
            bool: True if the workflow is active

        Usage Examples:
            # Python - Check if active
            workflow = Workflow(id="wf_123", team_id="team_001", name="Auto-assign", is_active=True)
            print(workflow.is_active_workflow())  # True

            workflow.deactivate()
            print(workflow.is_active_workflow())  # False
        """
        return self.is_active
