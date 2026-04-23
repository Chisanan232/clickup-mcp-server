"""
Unit tests for the Analytics API.

Tests the AnalyticsAPI class methods including:
- Get task analytics
- Get team analytics
- Get list analytics
- Get space analytics
"""

import pytest
from unittest.mock import MagicMock

from clickup_mcp.api.analytics import AnalyticsAPI
from clickup_mcp.models.dto.analytics import (
    TaskAnalyticsQuery,
    TeamAnalyticsQuery,
    ListAnalyticsQuery,
    SpaceAnalyticsQuery,
    TaskAnalyticsResponse,
    TeamAnalyticsResponse,
    ListAnalyticsResponse,
    SpaceAnalyticsResponse,
)
from clickup_mcp.client import ClickUpAPIClient


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Create a mock API client."""
    client = MagicMock(spec=ClickUpAPIClient)
    return client


@pytest.fixture
def analytics_api(mock_api_client: MagicMock) -> AnalyticsAPI:
    """Create an AnalyticsAPI instance with mock client."""
    return AnalyticsAPI(mock_api_client)


@pytest.fixture
def sample_task_analytics_data() -> dict:
    """Sample task analytics data for testing."""
    return {
        "id": "a1",
        "team_id": "team_001",
        "list_id": "list_123",
        "start_date": 1640995200000,
        "end_date": 1643673600000,
        "total_tasks": 100,
        "completed_tasks": 75,
        "in_progress_tasks": 15,
        "blocked_tasks": 10,
        "average_completion_time": 86400000,
        "assignee_metrics": {"user_123": {"completed": 30, "in_progress": 5}},
        "status_metrics": {"open": 10, "in progress": 15, "closed": 75},
    }


@pytest.fixture
def sample_team_analytics_data() -> dict:
    """Sample team analytics data for testing."""
    return {
        "id": "a2",
        "team_id": "team_001",
        "start_date": 1640995200000,
        "end_date": 1643673600000,
        "total_tasks": 500,
        "completed_tasks": 400,
        "total_lists": 10,
        "active_users": 25,
        "average_task_completion_time": 86400000,
    }


@pytest.fixture
def sample_list_analytics_data() -> dict:
    """Sample list analytics data for testing."""
    return {
        "id": "a3",
        "list_id": "list_123",
        "start_date": 1640995200000,
        "end_date": 1643673600000,
        "total_tasks": 50,
        "completed_tasks": 40,
        "overdue_tasks": 5,
        "average_completion_time": 86400000,
    }


@pytest.fixture
def sample_space_analytics_data() -> dict:
    """Sample space analytics data for testing."""
    return {
        "id": "a4",
        "space_id": "space_123",
        "start_date": 1640995200000,
        "end_date": 1643673600000,
        "total_tasks": 200,
        "completed_tasks": 150,
        "total_lists": 5,
        "total_folders": 3,
    }


class TestAnalyticsAPI:
    """Test cases for AnalyticsAPI."""

    @pytest.mark.asyncio
    async def test_get_task_analytics(
        self, analytics_api, mock_api_client, sample_task_analytics_data
    ):
        """Test getting task analytics for a team."""
        # Arrange
        team_id = "team_001"
        query = TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = {"data": sample_task_analytics_data}

        # Act
        result = await analytics_api.get_task_analytics(team_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/team/{team_id}/analytics/task"
        assert isinstance(result, TaskAnalyticsResponse)
        assert result.total_tasks == 100

    @pytest.mark.asyncio
    async def test_get_task_analytics_with_filters(
        self, analytics_api, mock_api_client, sample_task_analytics_data
    ):
        """Test getting task analytics with filters."""
        # Arrange
        team_id = "team_001"
        query = TaskAnalyticsQuery(
            start_date=1640995200000,
            end_date=1643673600000,
            assignee_id="user_123",
            status="open",
        )
        mock_api_client.get.return_value = {"data": sample_task_analytics_data}

        # Act
        result = await analytics_api.get_task_analytics(team_id, query)

        # Assert
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["assignee_id"] == "user_123"
        assert call_args[1]["params"]["status"] == "open"

    @pytest.mark.asyncio
    async def test_get_task_analytics_returns_none_on_failure(
        self, analytics_api, mock_api_client
    ):
        """Test getting task analytics that fails returns None."""
        # Arrange
        team_id = "team_001"
        query = TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = None

        # Act
        result = await analytics_api.get_task_analytics(team_id, query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_team_analytics(
        self, analytics_api, mock_api_client, sample_team_analytics_data
    ):
        """Test getting team analytics."""
        # Arrange
        team_id = "team_001"
        query = TeamAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = {"data": sample_team_analytics_data}

        # Act
        result = await analytics_api.get_team_analytics(team_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/team/{team_id}/analytics/team"
        assert isinstance(result, TeamAnalyticsResponse)
        assert result.total_tasks == 500

    @pytest.mark.asyncio
    async def test_get_team_analytics_returns_none_on_failure(
        self, analytics_api, mock_api_client
    ):
        """Test getting team analytics that fails returns None."""
        # Arrange
        team_id = "team_001"
        query = TeamAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = None

        # Act
        result = await analytics_api.get_team_analytics(team_id, query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_list_analytics(
        self, analytics_api, mock_api_client, sample_list_analytics_data
    ):
        """Test getting list analytics."""
        # Arrange
        list_id = "list_123"
        query = ListAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = {"data": sample_list_analytics_data}

        # Act
        result = await analytics_api.get_list_analytics(list_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/list/{list_id}/analytics"
        assert isinstance(result, ListAnalyticsResponse)
        assert result.total_tasks == 50

    @pytest.mark.asyncio
    async def test_get_list_analytics_returns_none_on_failure(
        self, analytics_api, mock_api_client
    ):
        """Test getting list analytics that fails returns None."""
        # Arrange
        list_id = "list_123"
        query = ListAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = None

        # Act
        result = await analytics_api.get_list_analytics(list_id, query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_space_analytics(
        self, analytics_api, mock_api_client, sample_space_analytics_data
    ):
        """Test getting space analytics."""
        # Arrange
        space_id = "space_123"
        query = SpaceAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = {"data": sample_space_analytics_data}

        # Act
        result = await analytics_api.get_space_analytics(space_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/space/{space_id}/analytics"
        assert isinstance(result, SpaceAnalyticsResponse)
        assert result.total_tasks == 200

    @pytest.mark.asyncio
    async def test_get_space_analytics_returns_none_on_failure(
        self, analytics_api, mock_api_client
    ):
        """Test getting space analytics that fails returns None."""
        # Arrange
        space_id = "space_123"
        query = SpaceAnalyticsQuery(start_date=1640995200000, end_date=1643673600000)
        mock_api_client.get.return_value = None

        # Act
        result = await analytics_api.get_space_analytics(space_id, query)

        # Assert
        assert result is None
