"""Unit tests for WorkflowContext domain model."""

import pytest

from clickup_mcp.models.domain.workflow_context import WorkflowContext


class TestWorkflowContext:
    """Test suite for WorkflowContext domain model."""

    def test_workflow_context_creation(self):
        """Test creating a workflow context with valid data."""
        context = WorkflowContext(
            id="ctx_123",
            workflow_id="wf_456",
            name="Production Context",
            variables={"priority": "high", "assignee": "user_789"},
            is_active=True,
        )

        assert context.context_id == "ctx_123"
        assert context.workflow_id == "wf_456"
        assert context.name == "Production Context"
        assert context.variables == {"priority": "high", "assignee": "user_789"}
        assert context.is_active is True

    def test_backward_compatible_id_property(self):
        """Test that the id property returns context_id."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        assert context.id == "ctx_123"
        assert context.id == context.context_id

    def test_update_name(self):
        """Test updating context name."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Old Name")
        context.update_name("New Name")
        assert context.name == "New Name"

    def test_update_name_empty_string_raises_error(self):
        """Test that updating name with empty string raises ValueError."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Old Name")
        with pytest.raises(ValueError, match="name cannot be empty string"):
            context.update_name("")

    def test_update_description(self):
        """Test updating context description."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", description="Old Description")
        context.update_description("New Description")
        assert context.description == "New Description"

    def test_update_description_clear(self):
        """Test clearing context description."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", description="Description")
        context.update_description(None)
        assert context.description is None

    def test_set_variable(self):
        """Test setting a context variable."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        context.set_variable("priority", "urgent")
        assert context.variables == {"priority": "urgent"}

    def test_set_variable_update_existing(self):
        """Test updating an existing variable."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", variables={"priority": "high"})
        context.set_variable("priority", "urgent")
        assert context.variables == {"priority": "urgent"}

    def test_set_variable_empty_key_raises_error(self):
        """Test that setting variable with empty key raises ValueError."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        with pytest.raises(ValueError, match="variable key cannot be empty"):
            context.set_variable("", "value")

    def test_remove_variable(self):
        """Test removing a context variable."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", variables={"priority": "urgent"})
        context.remove_variable("priority")
        assert context.variables == {}

    def test_remove_variable_not_found_raises_error(self):
        """Test that removing non-existent variable raises ValueError."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        with pytest.raises(ValueError, match="variable .* not found"):
            context.remove_variable("priority")

    def test_set_variables(self):
        """Test setting all context variables."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        context.set_variables({"priority": "urgent", "assignee": "user_789"})
        assert context.variables == {"priority": "urgent", "assignee": "user_789"}

    def test_add_condition(self):
        """Test adding an execution condition."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        context.add_condition("status == 'open'")
        assert context.conditions == ["status == 'open'"]

    def test_add_condition_empty_raises_error(self):
        """Test that adding empty condition raises ValueError."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        with pytest.raises(ValueError, match="condition cannot be empty"):
            context.add_condition("")

    def test_add_condition_duplicate_raises_error(self):
        """Test that adding duplicate condition raises ValueError."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", conditions=["status == 'open'"])
        with pytest.raises(ValueError, match="condition .* already exists"):
            context.add_condition("status == 'open'")

    def test_remove_condition(self):
        """Test removing an execution condition."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", conditions=["status == 'open'"])
        context.remove_condition("status == 'open'")
        assert context.conditions == []

    def test_remove_condition_not_found_raises_error(self):
        """Test that removing non-existent condition raises ValueError."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test")
        with pytest.raises(ValueError, match="condition .* not found"):
            context.remove_condition("status == 'open'")

    def test_activate(self):
        """Test activating context."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", is_active=False)
        context.activate()
        assert context.is_active is True

    def test_deactivate(self):
        """Test deactivating context."""
        context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", is_active=True)
        context.deactivate()
        assert context.is_active is False

    def test_is_active_context(self):
        """Test checking if context is active."""
        active_context = WorkflowContext(id="ctx_123", workflow_id="wf_456", name="Test", is_active=True)
        inactive_context = WorkflowContext(id="ctx_124", workflow_id="wf_456", name="Test", is_active=False)

        assert active_context.is_active_context() is True
        assert inactive_context.is_active_context() is False
