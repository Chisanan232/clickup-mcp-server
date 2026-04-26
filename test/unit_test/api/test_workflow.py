"""
Unit tests for the Workflow API.

Tests the WorkflowAPI class methods including:
- Create workflow
- Get workflow
- Update workflow
- Delete workflow
- List workflows
"""

from unittest.mock import MagicMock

import pytest

from clickup_mcp.api.workflow import WorkflowAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.workflow import (
    WorkflowCreate,
    WorkflowListResponse,
    WorkflowUpdate,
)


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Create a mock API client."""
    client = MagicMock(spec=ClickUpAPIClient)
    return client


@pytest.fixture
def workflow_api(mock_api_client: MagicMock) -> WorkflowAPI:
    """Create a WorkflowAPI instance with mock client."""
    return WorkflowAPI(mock_api_client)


@pytest.fixture
def sample_workflow_data() -> dict:
    """Sample workflow data for testing."""
    return {
        "items": [
            {
                "id": "wf_123",
                "team_id": "team_001",
                "name": "Auto-assign on create",
                "description": "Automatically assign tasks on creation",
                "trigger_type": "task_created",
                "trigger_config": {"list_id": "456"},
                "actions": [{"type": "assign", "user_id": "789"}],
                "is_active": True,
                "priority": 1,
                "date_created": 1702080000000,
                "date_updated": 1702080000000,
            }
        ],
        "page": 0,
        "limit": 100,
        "total": 1,
    }


class TestWorkflowAPI:
    """Test cases for WorkflowAPI."""

    @pytest.mark.asyncio
    async def test_create_workflow(self, workflow_api, mock_api_client, sample_workflow_data):
        """Test creating a workflow automation."""
        # Arrange
        team_id = "team_001"
        workflow_create = WorkflowCreate(
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "456"},
            actions=[{"type": "assign", "user_id": "789"}],
        )
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_workflow_data, headers={}
        )

        # Act
        result = await workflow_api.create(team_id, workflow_create)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/team/{team_id}/workflow"
        assert isinstance(result, WorkflowListResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_create_workflow_returns_none_on_failure(self, workflow_api, mock_api_client):
        """Test creating a workflow that fails returns None."""
        # Arrange
        team_id = "team_001"
        workflow_create = WorkflowCreate(
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "456"},
            actions=[{"type": "assign", "user_id": "789"}],
        )
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=500, data=None, headers={}
        )

        # Act
        result = await workflow_api.create(team_id, workflow_create)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_workflow(self, workflow_api, mock_api_client, sample_workflow_data):
        """Test getting a workflow by ID."""
        # Arrange
        workflow_id = "wf_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_workflow_data, headers={}
        )

        # Act
        result = await workflow_api.get(workflow_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/workflow/{workflow_id}")
        assert isinstance(result, WorkflowListResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_get_workflow_returns_none_on_failure(self, workflow_api, mock_api_client):
        """Test getting a workflow that fails returns None."""
        # Arrange
        workflow_id = "wf_123"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=500, data=None, headers={}
        )

        # Act
        result = await workflow_api.get(workflow_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_workflow(self, workflow_api, mock_api_client, sample_workflow_data):
        """Test updating a workflow."""
        # Arrange
        workflow_id = "wf_123"
        workflow_update = WorkflowUpdate(name="Updated name", is_active=False)
        mock_api_client.put.return_value = APIResponse(
            success=True, status_code=200, data=sample_workflow_data, headers={}
        )

        # Act
        result = await workflow_api.update(workflow_id, workflow_update)

        # Assert
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"/workflow/{workflow_id}"
        assert isinstance(result, WorkflowListResponse)

    @pytest.mark.asyncio
    async def test_update_workflow_returns_none_on_failure(self, workflow_api, mock_api_client):
        """Test updating a workflow that fails returns None."""
        # Arrange
        workflow_id = "wf_123"
        workflow_update = WorkflowUpdate(name="Updated name")
        mock_api_client.put.return_value = APIResponse(
            success=False, status_code=500, data=None, headers={}
        )

        # Act
        result = await workflow_api.update(workflow_id, workflow_update)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_workflow(self, workflow_api, mock_api_client):
        """Test deleting a workflow."""
        # Arrange
        workflow_id = "wf_123"
        mock_api_client.delete.return_value = APIResponse(
            success=True, status_code=204, data=None, headers={}
        )

        # Act
        result = await workflow_api.delete(workflow_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/workflow/{workflow_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_workflow_returns_false_on_failure(self, workflow_api, mock_api_client):
        """Test deleting a workflow that fails returns False."""
        # Arrange
        workflow_id = "wf_123"
        mock_api_client.delete.return_value = APIResponse(
            success=False, status_code=500, data=None, headers={}
        )

        # Act
        result = await workflow_api.delete(workflow_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_list_workflows(self, workflow_api, mock_api_client, sample_workflow_data):
        """Test listing workflows for a team."""
        # Arrange
        team_id = "team_001"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_workflow_data, headers={}
        )

        # Act
        result = await workflow_api.list(team_id)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/team/{team_id}/workflow"
        assert isinstance(result, WorkflowListResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_list_workflows_with_pagination(self, workflow_api, mock_api_client, sample_workflow_data):
        """Test listing workflows with pagination parameters."""
        # Arrange
        team_id = "team_001"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_workflow_data, headers={}
        )

        # Act
        result = await workflow_api.list(team_id, page=1, limit=50)

        # Assert
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["page"] == "1"
        assert call_args[1]["params"]["limit"] == "50"

    @pytest.mark.asyncio
    async def test_list_workflows_with_active_filter(self, workflow_api, mock_api_client, sample_workflow_data):
        """Test listing workflows with active status filter."""
        # Arrange
        team_id = "team_001"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_workflow_data, headers={}
        )

        # Act
        result = await workflow_api.list(team_id, is_active=True)

        # Assert
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["is_active"] == "true"

    @pytest.mark.asyncio
    async def test_list_workflows_returns_none_on_failure(self, workflow_api, mock_api_client):
        """Test listing workflows that fails returns None."""
        # Arrange
        team_id = "team_001"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=500, data=None, headers={}
        )

        # Act
        result = await workflow_api.list(team_id)

        # Assert
        assert result is None
