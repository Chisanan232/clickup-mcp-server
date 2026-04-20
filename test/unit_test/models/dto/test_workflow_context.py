"""Unit tests for WorkflowContext DTOs."""

from clickup_mcp.models.dto.workflow_context import (
    WorkflowContextCreate,
    WorkflowContextListQuery,
    WorkflowContextListResponse,
    WorkflowContextResponse,
    WorkflowContextUpdate,
)


class TestWorkflowContextCreate:
    """Test suite for WorkflowContextCreate DTO."""

    def test_workflow_context_create_to_payload(self):
        """Test converting WorkflowContextCreate to payload."""
        dto = WorkflowContextCreate(
            name="Production Context",
            description="Test description",
            variables={"priority": "high", "assignee": "user_789"},
            conditions=["status == 'open'"],
            is_active=True,
        )
        payload = dto.to_payload()

        assert payload["name"] == "Production Context"
        assert payload["description"] == "Test description"
        assert payload["variables"] == {"priority": "high", "assignee": "user_789"}
        assert payload["conditions"] == ["status == 'open'"]
        assert payload["is_active"] is True

    def test_workflow_context_create_to_payload_excludes_none(self):
        """Test that to_payload excludes None values."""
        dto = WorkflowContextCreate(name="Test", description=None)
        payload = dto.to_payload()

        assert "description" not in payload
        assert "name" in payload

    def test_workflow_context_create_with_defaults(self):
        """Test WorkflowContextCreate with default values."""
        dto = WorkflowContextCreate(name="Test")

        assert dto.description is None
        assert dto.variables == {}
        assert dto.conditions == []
        assert dto.is_active is True


class TestWorkflowContextUpdate:
    """Test suite for WorkflowContextUpdate DTO."""

    def test_workflow_context_update_to_payload(self):
        """Test converting WorkflowContextUpdate to payload."""
        dto = WorkflowContextUpdate(
            name="Updated Context",
            description="Updated description",
            variables={"priority": "urgent"},
            conditions=["status == 'closed'"],
            is_active=False,
        )
        payload = dto.to_payload()

        assert payload["name"] == "Updated Context"
        assert payload["description"] == "Updated description"
        assert payload["variables"] == {"priority": "urgent"}
        assert payload["conditions"] == ["status == 'closed'"]
        assert payload["is_active"] is False

    def test_workflow_context_update_to_payload_excludes_none(self):
        """Test that to_payload excludes None values."""
        dto = WorkflowContextUpdate(name="Updated Context", description=None)
        payload = dto.to_payload()

        assert "description" not in payload
        assert "name" in payload


class TestWorkflowContextListQuery:
    """Test suite for WorkflowContextListQuery DTO."""

    def test_workflow_context_list_query_to_query(self):
        """Test converting WorkflowContextListQuery to query parameters."""
        dto = WorkflowContextListQuery(page=1, limit=50)
        query = dto.to_query()

        assert query["page"] == "1"
        assert query["limit"] == "50"

    def test_workflow_context_list_query_with_defaults(self):
        """Test WorkflowContextListQuery with default values."""
        dto = WorkflowContextListQuery()

        assert dto.page == 0
        assert dto.limit == 100


class TestWorkflowContextResponse:
    """Test suite for WorkflowContextResponse DTO."""

    def test_workflow_context_response_deserialize(self):
        """Test deserializing API response to WorkflowContextResponse."""
        data = {
            "id": "ctx_123",
            "workflow_id": "wf_456",
            "name": "Production Context",
            "description": "Test description",
            "variables": {"priority": "high"},
            "conditions": ["status == 'open'"],
            "is_active": True,
            "date_created": 1702000000000,
            "date_updated": 1702100000000,
        }
        response = WorkflowContextResponse.deserialize(data)

        assert response.id == "ctx_123"
        assert response.workflow_id == "wf_456"
        assert response.name == "Production Context"
        assert response.variables == {"priority": "high"}
        assert response.is_active is True


class TestWorkflowContextListResponse:
    """Test suite for WorkflowContextListResponse DTO."""

    def test_workflow_context_list_response_deserialize(self):
        """Test deserializing API response to WorkflowContextListResponse."""
        data = {
            "items": [
                {
                    "id": "ctx_123",
                    "workflow_id": "wf_456",
                    "name": "Context 1",
                    "is_active": True,
                },
                {
                    "id": "ctx_124",
                    "workflow_id": "wf_456",
                    "name": "Context 2",
                    "is_active": False,
                },
            ],
            "page": 0,
            "limit": 100,
            "total": 2,
        }
        response = WorkflowContextListResponse.deserialize(data)

        assert len(response.items) == 2
        assert response.page == 0
        assert response.limit == 100
        assert response.total == 2
        assert response.items[0].name == "Context 1"
        assert response.items[1].name == "Context 2"

    def test_workflow_context_list_response_deserialize_empty_items(self):
        """Test deserializing empty items list."""
        data = {"items": [], "page": 0, "limit": 100, "total": 0}
        response = WorkflowContextListResponse.deserialize(data)

        assert response.items == []
        assert response.total == 0
