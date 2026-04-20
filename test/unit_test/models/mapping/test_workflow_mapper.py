"""Unit tests for Workflow mapper."""

from clickup_mcp.models.domain.workflow import Workflow
from clickup_mcp.models.dto.workflow import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)
from clickup_mcp.models.mapping.workflow_mapper import WorkflowMapper


class MockWorkflowCreateInput:
    """Mock MCP input for workflow creation."""

    def __init__(
        self,
        team_id: str,
        name: str,
        trigger_type: str,
        trigger_config: dict | None = None,
        actions: list | None = None,
        is_active: bool = True,
        priority: int | None = None,
    ):
        self.team_id = team_id
        self.name = name
        self.description = None
        self.trigger_type = trigger_type
        self.trigger_config = trigger_config or {}
        self.actions = actions or []
        self.is_active = is_active
        self.priority = priority


class MockWorkflowUpdateInput:
    """Mock MCP input for workflow update."""

    def __init__(
        self,
        workflow_id: str,
        name: str | None = None,
        description: str | None = None,
        trigger_type: str | None = None,
        trigger_config: dict | None = None,
        actions: list | None = None,
        is_active: bool | None = None,
        priority: int | None = None,
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.trigger_type = trigger_type
        self.trigger_config = trigger_config
        self.actions = actions
        self.is_active = is_active
        self.priority = priority


class TestWorkflowMapper:
    """Test suite for WorkflowMapper."""

    def test_from_create_input(self):
        """Test converting MCP create input to domain."""
        mcp_input = MockWorkflowCreateInput(
            team_id="team_456",
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "789"},
            actions=[{"type": "assign", "user_id": "user_123"}],
            is_active=True,
            priority=1,
        )

        domain = WorkflowMapper.from_create_input(mcp_input)

        assert domain.workflow_id == "temp"
        assert domain.team_id == "team_456"
        assert domain.name == "Auto-assign on create"
        assert domain.trigger_type == "task_created"
        assert domain.trigger_config == {"list_id": "789"}
        assert domain.actions == [{"type": "assign", "user_id": "user_123"}]
        assert domain.is_active is True
        assert domain.priority == 1

    def test_from_update_input(self):
        """Test converting MCP update input to domain."""
        mcp_input = MockWorkflowUpdateInput(
            workflow_id="wf_123",
            name="Updated name",
            description="Updated description",
            is_active=False,
            priority=2,
        )

        domain = WorkflowMapper.from_update_input(mcp_input)

        assert domain.workflow_id == "wf_123"
        assert domain.team_id == "temp"
        assert domain.name == "Updated name"
        assert domain.description == "Updated description"
        assert domain.is_active is False
        assert domain.priority == 2

    def test_to_domain(self):
        """Test converting API response DTO to domain."""
        response = WorkflowResponse(
            id="wf_123",
            team_id="team_456",
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "789"},
            actions=[{"type": "assign", "user_id": "user_123"}],
            is_active=True,
            priority=1,
            date_created=1702000000000,
            date_updated=1702100000000,
        )

        domain = WorkflowMapper.to_domain(response)

        assert domain.workflow_id == "wf_123"
        assert domain.team_id == "team_456"
        assert domain.name == "Auto-assign on create"
        assert domain.trigger_type == "task_created"
        assert domain.is_active is True

    def test_to_create_dto(self):
        """Test converting domain to create DTO."""
        domain = Workflow(
            id="wf_123",
            team_id="team_456",
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "789"},
            actions=[{"type": "assign", "user_id": "user_123"}],
            is_active=True,
            priority=1,
        )

        dto = WorkflowMapper.to_create_dto(domain)

        assert isinstance(dto, WorkflowCreate)
        assert dto.name == "Auto-assign on create"
        assert dto.trigger_type == "task_created"
        assert dto.trigger_config == {"list_id": "789"}
        assert dto.is_active is True

    def test_to_update_dto(self):
        """Test converting domain to update DTO."""
        domain = Workflow(
            id="wf_123",
            team_id="team_456",
            name="Updated name",
            description="Updated description",
            trigger_type="task_created",
            trigger_config={"list_id": "789"},
            actions=[{"type": "assign", "user_id": "user_123"}],
            is_active=False,
            priority=2,
        )

        dto = WorkflowMapper.to_update_dto(domain)

        assert isinstance(dto, WorkflowUpdate)
        assert dto.name == "Updated name"
        assert dto.description == "Updated description"
        assert dto.is_active is False

    def test_to_workflow_result_output(self):
        """Test converting domain to MCP result output."""
        domain = Workflow(
            id="wf_123",
            team_id="team_456",
            name="Auto-assign on create",
            trigger_type="task_created",
            is_active=True,
            priority=1,
            date_created=1702000000000,
            date_updated=1702100000000,
        )

        output = WorkflowMapper.to_workflow_result_output(domain)

        assert output["id"] == "wf_123"
        assert output["team_id"] == "team_456"
        assert output["name"] == "Auto-assign on create"
        assert output["trigger_type"] == "task_created"
        assert output["is_active"] is True
        assert output["priority"] == 1

    def test_to_workflow_list_item_output(self):
        """Test converting domain to MCP list item output."""
        domain = Workflow(
            id="wf_123",
            team_id="team_456",
            name="Auto-assign on create",
            trigger_type="task_created",
            is_active=True,
            priority=1,
        )

        output = WorkflowMapper.to_workflow_list_item_output(domain)

        assert output["id"] == "wf_123"
        assert output["team_id"] == "team_456"
        assert output["name"] == "Auto-assign on create"
        assert output["trigger_type"] == "task_created"
        assert output["is_active"] is True
        assert output["priority"] == 1
