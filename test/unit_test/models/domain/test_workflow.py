"""Unit tests for Workflow domain model."""

import pytest

from clickup_mcp.models.domain.workflow import Workflow


class TestWorkflow:
    """Test suite for Workflow domain model."""

    def test_workflow_creation(self):
        """Test creating a workflow with valid data."""
        workflow = Workflow(
            id="wf_123",
            team_id="team_456",
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "789"},
            actions=[{"type": "assign", "user_id": "user_123"}],
            is_active=True,
            priority=1,
        )

        assert workflow.workflow_id == "wf_123"
        assert workflow.team_id == "team_456"
        assert workflow.name == "Auto-assign on create"
        assert workflow.trigger_type == "task_created"
        assert workflow.is_active is True
        assert workflow.priority == 1

    def test_backward_compatible_id_property(self):
        """Test that the id property returns workflow_id."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        assert workflow.id == "wf_123"
        assert workflow.id == workflow.workflow_id

    def test_update_name(self):
        """Test updating workflow name."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Old Name", trigger_type="task_created")
        workflow.update_name("New Name")
        assert workflow.name == "New Name"

    def test_update_name_empty_string_raises_error(self):
        """Test that updating name with empty string raises ValueError."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Old Name", trigger_type="task_created")
        with pytest.raises(ValueError, match="name cannot be empty string"):
            workflow.update_name("")

    def test_update_description(self):
        """Test updating workflow description."""
        workflow = Workflow(
            id="wf_123", team_id="team_456", name="Test", description="Old Description", trigger_type="task_created"
        )
        workflow.update_description("New Description")
        assert workflow.description == "New Description"

    def test_update_description_clear(self):
        """Test clearing workflow description."""
        workflow = Workflow(
            id="wf_123", team_id="team_456", name="Test", description="Description", trigger_type="task_created"
        )
        workflow.update_description(None)
        assert workflow.description is None

    def test_update_description_empty_string_raises_error(self):
        """Test that updating description with empty string raises ValueError."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        with pytest.raises(ValueError, match="description cannot be empty string"):
            workflow.update_description("")

    def test_set_trigger_type(self):
        """Test setting trigger type."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        workflow.set_trigger_type("status_changed")
        assert workflow.trigger_type == "status_changed"

    def test_set_trigger_type_empty_string_raises_error(self):
        """Test that setting trigger type with empty string raises ValueError."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        with pytest.raises(ValueError, match="trigger_type cannot be empty string"):
            workflow.set_trigger_type("")

    def test_set_trigger_config(self):
        """Test setting trigger config."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        workflow.set_trigger_config({"list_id": "789"})
        assert workflow.trigger_config == {"list_id": "789"}

    def test_set_actions(self):
        """Test setting actions."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        workflow.set_actions([{"type": "assign", "user_id": "user_123"}])
        assert workflow.actions == [{"type": "assign", "user_id": "user_123"}]

    def test_add_action(self):
        """Test adding an action."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        workflow.add_action({"type": "assign", "user_id": "user_123"})
        assert len(workflow.actions) == 1
        assert workflow.actions[0] == {"type": "assign", "user_id": "user_123"}

    def test_add_action_empty_raises_error(self):
        """Test that adding empty action raises ValueError."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        with pytest.raises(ValueError, match="action cannot be empty"):
            workflow.add_action({})

    def test_add_action_duplicate_raises_error(self):
        """Test that adding duplicate action raises ValueError."""
        action = {"type": "assign", "user_id": "user_123"}
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created", actions=[action])
        with pytest.raises(ValueError, match="action .* already exists"):
            workflow.add_action(action)

    def test_remove_action(self):
        """Test removing an action."""
        action = {"type": "assign", "user_id": "user_123"}
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created", actions=[action])
        workflow.remove_action(action)
        assert workflow.actions == []

    def test_remove_action_not_found_raises_error(self):
        """Test that removing non-existent action raises ValueError."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        with pytest.raises(ValueError, match="action .* not found"):
            workflow.remove_action({"type": "assign", "user_id": "user_123"})

    def test_activate(self):
        """Test activating workflow."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", is_active=False, trigger_type="task_created")
        workflow.activate()
        assert workflow.is_active is True

    def test_deactivate(self):
        """Test deactivating workflow."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", is_active=True, trigger_type="task_created")
        workflow.deactivate()
        assert workflow.is_active is False

    def test_set_priority(self):
        """Test setting priority."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        workflow.set_priority(2)
        assert workflow.priority == 2

    def test_set_priority_negative_raises_error(self):
        """Test that setting negative priority raises ValueError."""
        workflow = Workflow(id="wf_123", team_id="team_456", name="Test", trigger_type="task_created")
        with pytest.raises(ValueError, match="priority must be non-negative"):
            workflow.set_priority(-1)

    def test_is_active_workflow(self):
        """Test checking if workflow is active."""
        active_workflow = Workflow(
            id="wf_123", team_id="team_456", name="Test", is_active=True, trigger_type="task_created"
        )
        inactive_workflow = Workflow(
            id="wf_124", team_id="team_456", name="Test", is_active=False, trigger_type="task_created"
        )

        assert active_workflow.is_active_workflow() is True
        assert inactive_workflow.is_active_workflow() is False
