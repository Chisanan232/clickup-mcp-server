"""Unit tests for Workflow DTOs."""

import pytest

from clickup_mcp.models.dto.workflow import (
    WorkflowCreate,
    WorkflowListQuery,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowUpdate,
)


class TestWorkflowCreate:
    """Test suite for WorkflowCreate DTO."""

    def test_workflow_create_to_payload(self):
        """Test converting WorkflowCreate to payload."""
        dto = WorkflowCreate(
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "789"},
            actions=[{"type": "assign", "user_id": "user_123"}],
            is_active=True,
            priority=1,
        )
        payload = dto.to_payload()

        assert payload["name"] == "Auto-assign on create"
        assert payload["trigger_type"] == "task_created"
        assert payload["trigger_config"] == {"list_id": "789"}
        assert payload["actions"] == [{"type": "assign", "user_id": "user_123"}]
        assert payload["is_active"] is True
        assert payload["priority"] == 1

    def test_workflow_create_to_payload_excludes_none(self):
        """Test that to_payload excludes None values."""
        dto = WorkflowCreate(name="Test", trigger_type="task_created", description=None)
        payload = dto.to_payload()

        assert "description" not in payload
        assert "name" in payload

    def test_workflow_create_with_defaults(self):
        """Test WorkflowCreate with default values."""
        dto = WorkflowCreate(name="Test", trigger_type="task_created")

        assert dto.description is None
        assert dto.trigger_config == {}
        assert dto.actions == []
        assert dto.is_active is True
        assert dto.priority is None


class TestWorkflowUpdate:
    """Test suite for WorkflowUpdate DTO."""

    def test_workflow_update_to_payload(self):
        """Test converting WorkflowUpdate to payload."""
        dto = WorkflowUpdate(
            name="Updated name",
            description="Updated description",
            is_active=False,
            priority=2,
        )
        payload = dto.to_payload()

        assert payload["name"] == "Updated name"
        assert payload["description"] == "Updated description"
        assert payload["is_active"] is False
        assert payload["priority"] == 2

    def test_workflow_update_to_payload_excludes_none(self):
        """Test that to_payload excludes None values."""
        dto = WorkflowUpdate(name="Updated name", description=None)
        payload = dto.to_payload()

        assert "description" not in payload
        assert "name" in payload


class TestWorkflowListQuery:
    """Test suite for WorkflowListQuery DTO."""

    def test_workflow_list_query_to_query(self):
        """Test converting WorkflowListQuery to query parameters."""
        dto = WorkflowListQuery(page=1, limit=50, is_active=True)
        query = dto.to_query()

        assert query["page"] == "1"
        assert query["limit"] == "50"
        assert query["is_active"] == "true"

    def test_workflow_list_query_with_defaults(self):
        """Test WorkflowListQuery with default values."""
        dto = WorkflowListQuery()

        assert dto.page == 0
        assert dto.limit == 100
        assert dto.is_active is None

    def test_workflow_list_query_to_query_excludes_none(self):
        """Test that to_query excludes None values."""
        dto = WorkflowListQuery(page=1, limit=50, is_active=None)
        query = dto.to_query()

        assert "is_active" not in query
        assert "page" in query
        assert "limit" in query


class TestWorkflowResponse:
    """Test suite for WorkflowResponse DTO."""

    def test_workflow_response_deserialize(self):
        """Test deserializing API response to WorkflowResponse."""
        data = {
            "id": "wf_123",
            "team_id": "team_456",
            "name": "Auto-assign on create",
            "description": "Test description",
            "trigger_type": "task_created",
            "trigger_config": {"list_id": "789"},
            "actions": [{"type": "assign", "user_id": "user_123"}],
            "is_active": True,
            "priority": 1,
            "date_created": 1702000000000,
            "date_updated": 1702100000000,
        }
        response = WorkflowResponse.deserialize(data)

        assert response.id == "wf_123"
        assert response.team_id == "team_456"
        assert response.name == "Auto-assign on create"
        assert response.trigger_type == "task_created"
        assert response.is_active is True


class TestWorkflowListResponse:
    """Test suite for WorkflowListResponse DTO."""

    def test_workflow_list_response_deserialize(self):
        """Test deserializing API response to WorkflowListResponse."""
        data = {
            "items": [
                {
                    "id": "wf_123",
                    "team_id": "team_456",
                    "name": "Workflow 1",
                    "trigger_type": "task_created",
                    "is_active": True,
                },
                {
                    "id": "wf_124",
                    "team_id": "team_456",
                    "name": "Workflow 2",
                    "trigger_type": "status_changed",
                    "is_active": False,
                },
            ],
            "page": 0,
            "limit": 100,
            "total": 2,
        }
        response = WorkflowListResponse.deserialize(data)

        assert len(response.items) == 2
        assert response.page == 0
        assert response.limit == 100
        assert response.total == 2
        assert response.items[0].name == "Workflow 1"
        assert response.items[1].name == "Workflow 2"

    def test_workflow_list_response_deserialize_empty_items(self):
        """Test deserializing empty items list."""
        data = {"items": [], "page": 0, "limit": 100, "total": 0}
        response = WorkflowListResponse.deserialize(data)

        assert response.items == []
        assert response.total == 0
