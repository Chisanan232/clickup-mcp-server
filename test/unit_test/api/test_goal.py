"""
Unit tests for the Goal API.

Tests the GoalAPI class methods including:
- Create goal
- Get goal
- Update goal
- Delete goal
- List goals
"""

import pytest
from unittest.mock import MagicMock

from clickup_mcp.api.goal import GoalAPI
from clickup_mcp.models.dto.goal import (
    GoalCreate,
    GoalListQuery,
    GoalUpdate,
    GoalListResponse,
)
from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.http import APIResponse


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Create a mock API client."""
    client = MagicMock(spec=ClickUpAPIClient)
    return client


@pytest.fixture
def goal_api(mock_api_client: MagicMock) -> GoalAPI:
    """Create a GoalAPI instance with mock client."""
    return GoalAPI(mock_api_client)


@pytest.fixture
def sample_goal_data() -> dict:
    """Sample goal data for testing."""
    return {
        "id": "goal_123",
        "team_id": "team_001",
        "name": "Q1 Revenue Goal",
        "description": "Achieve $1M in revenue",
        "due_date": 1702080000000,
        "status": "active",
        "key_results": ["KR1", "KR2"],
        "owners": ["user_123"],
        "multiple_owners": False,
        "date_created": 1702080000000,
        "date_updated": 1702080000000,
    }


@pytest.fixture
def sample_goal_list_data() -> dict:
    """Sample goal list data for testing."""
    return {
        "items": [
            {
                "id": "goal_123",
                "team_id": "team_001",
                "name": "Q1 Revenue Goal",
                "description": "Achieve $1M in revenue",
                "due_date": 1702080000000,
                "status": "active",
                "key_results": ["KR1", "KR2"],
                "owners": ["user_123"],
                "multiple_owners": False,
            },
            {
                "id": "goal_124",
                "team_id": "team_001",
                "name": "Q2 Revenue Goal",
                "description": "Achieve $2M in revenue",
                "due_date": 1702080000000,
                "status": "active",
                "key_results": ["KR3"],
                "owners": ["user_123"],
                "multiple_owners": False,
            },
        ],
        "next_page": "cursor=2",
        "total": 10,
    }


class TestGoalAPI:
    """Test cases for GoalAPI."""

    @pytest.mark.asyncio
    async def test_create_goal(self, goal_api, mock_api_client, sample_goal_list_data):
        """Test creating a goal."""
        # Arrange
        team_id = "team_001"
        goal_create = GoalCreate(
            name="Q1 Revenue Goal", description="Achieve $1M in revenue", due_date=1702080000000
        )
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_goal_list_data, headers={}
        )

        # Act
        result = await goal_api.create(team_id, goal_create)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/team/{team_id}/goal"
        assert isinstance(result, GoalListResponse)
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_create_goal_returns_none_on_failure(self, goal_api, mock_api_client):
        """Test creating a goal that fails returns None."""
        # Arrange
        team_id = "team_001"
        goal_create = GoalCreate(
            name="Q1 Revenue Goal", description="Achieve $1M in revenue", due_date=1702080000000
        )
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await goal_api.create(team_id, goal_create)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_goal(self, goal_api, mock_api_client, sample_goal_data):
        """Test getting a goal by ID."""
        # Arrange
        goal_id = "goal_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_goal_data, headers={}
        )

        # Act
        result = await goal_api.get(goal_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/goal/{goal_id}")
        assert result is not None
        assert result["id"] == "goal_123"

    @pytest.mark.asyncio
    async def test_get_goal_returns_none_on_failure(self, goal_api, mock_api_client):
        """Test getting a goal that fails returns None."""
        # Arrange
        goal_id = "goal_123"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Not found"}, headers={}
        )

        # Act
        result = await goal_api.get(goal_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_goal(self, goal_api, mock_api_client, sample_goal_data):
        """Test updating a goal."""
        # Arrange
        goal_id = "goal_123"
        goal_update = GoalUpdate(name="Updated Goal Name")
        mock_api_client.put.return_value = APIResponse(
            success=True, status_code=200, data=sample_goal_data, headers={}
        )

        # Act
        result = await goal_api.update(goal_id, goal_update)

        # Assert
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"/goal/{goal_id}"
        assert result is not None
        assert result["id"] == "goal_123"

    @pytest.mark.asyncio
    async def test_update_goal_returns_none_on_failure(self, goal_api, mock_api_client):
        """Test updating a goal that fails returns None."""
        # Arrange
        goal_id = "goal_123"
        goal_update = GoalUpdate(name="Updated Goal Name")
        mock_api_client.put.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await goal_api.update(goal_id, goal_update)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_goal(self, goal_api, mock_api_client):
        """Test deleting a goal."""
        # Arrange
        goal_id = "goal_123"
        mock_api_client.delete.return_value = APIResponse(
            success=True, status_code=200, data=None, headers={}
        )

        # Act
        result = await goal_api.delete(goal_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/goal/{goal_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_goal_returns_false_on_failure(self, goal_api, mock_api_client):
        """Test deleting a goal that fails returns False."""
        # Arrange
        goal_id = "goal_123"
        mock_api_client.delete.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Not found"}, headers={}
        )

        # Act
        result = await goal_api.delete(goal_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_list_goals(self, goal_api, mock_api_client, sample_goal_list_data):
        """Test listing goals with query parameters."""
        # Arrange
        team_id = "team_001"
        query = GoalListQuery(status="active", limit=50)
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_goal_list_data, headers={}
        )

        # Act
        result = await goal_api.list(team_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/team/{team_id}/goal"
        assert isinstance(result, GoalListResponse)
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_list_goals_returns_none_on_failure(self, goal_api, mock_api_client):
        """Test listing goals that fails returns None."""
        # Arrange
        team_id = "team_001"
        query = GoalListQuery(status="active", limit=50)
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await goal_api.list(team_id, query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_goals_with_filters(self, goal_api, mock_api_client, sample_goal_list_data):
        """Test listing goals with multiple filters."""
        # Arrange
        team_id = "team_001"
        query = GoalListQuery(
            status="active", owner="user_123", start_date=1702080000000, end_date=1702083600000
        )
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_goal_list_data, headers={}
        )

        # Act
        result = await goal_api.list(team_id, query)

        # Assert
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["status"] == "active"
        assert call_args[1]["params"]["owner"] == "user_123"
        assert call_args[1]["params"]["start_date"] == 1702080000000
        assert call_args[1]["params"]["end_date"] == 1702083600000
        assert isinstance(result, GoalListResponse)
