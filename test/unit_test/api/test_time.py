"""
Unit tests for the Time API.

Tests the TimeAPI class methods including:
- Create time entry
- Get time entry
- List time entries
- Update time entry
- Delete time entry
- Start tracking
- Stop tracking
- Get tracking status
"""

from unittest.mock import MagicMock

import pytest

from clickup_mcp.api.time import TimeAPI
from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.dto.time import (
    TimeEntryCreate,
    TimeEntryListQuery,
    TimeEntryListResponse,
    TimeEntryResponse,
    TimeEntryUpdate,
    TimeTrackingStatusResponse,
)
from clickup_mcp.models.http import APIResponse


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Create a mock API client."""
    client = MagicMock(spec=ClickUpAPIClient)
    return client


@pytest.fixture
def time_api(mock_api_client: MagicMock) -> TimeAPI:
    """Create a TimeAPI instance with mock client."""
    return TimeAPI(mock_api_client)


@pytest.fixture
def sample_time_entry_data() -> dict:
    """Sample time entry data for testing."""
    return {
        "id": "entry_123",
        "task_id": "task_456",
        "user_id": 789,
        "team_id": "team_001",
        "description": "Implementation work",
        "duration": 3600000,
        "start": 1702080000000,
        "end": 1702083600000,
        "billable": False,
    }


@pytest.fixture
def sample_time_entry_list_data() -> dict:
    """Sample time entry list data for testing."""
    return {
        "items": [
            {
                "id": "entry_123",
                "task_id": "task_456",
                "user_id": 789,
                "team_id": "team_001",
                "description": "Implementation work",
                "duration": 3600000,
                "billable": False,
            },
            {
                "id": "entry_124",
                "task_id": "task_457",
                "user_id": 789,
                "team_id": "team_001",
                "description": "Review work",
                "duration": 1800000,
                "billable": True,
            },
        ],
        "next_page": "cursor=2",
        "total": 10,
    }


@pytest.fixture
def sample_tracking_status_data() -> dict:
    """Sample tracking status data for testing."""
    return {
        "active": True,
        "start": 1702080000000,
        "task_id": "task_123",
    }


class TestTimeAPI:
    """Test cases for TimeAPI."""

    @pytest.mark.asyncio
    async def test_create_time_entry(self, time_api, mock_api_client, sample_time_entry_data):
        """Test creating a time entry."""
        # Arrange
        team_id = "team_001"
        time_entry_create = TimeEntryCreate(task_id="task_456", description="Implementation work", duration=3600000)
        mock_api_client.post.return_value = APIResponse(
            success=True, status_code=200, data=sample_time_entry_data, headers={}
        )

        # Act
        result = await time_api.create(team_id, time_entry_create)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/team/{team_id}/time_entries"
        assert isinstance(result, TimeEntryResponse)
        assert result.id == "entry_123"

    @pytest.mark.asyncio
    async def test_create_time_entry_returns_none_on_failure(self, time_api, mock_api_client):
        """Test creating a time entry that fails returns None."""
        # Arrange
        team_id = "team_001"
        time_entry_create = TimeEntryCreate(task_id="task_456", description="Implementation work", duration=3600000)
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await time_api.create(team_id, time_entry_create)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_time_entry(self, time_api, mock_api_client, sample_time_entry_data):
        """Test getting a time entry by ID."""
        # Arrange
        team_id = "team_001"
        time_entry_id = "entry_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_time_entry_data, headers={}
        )

        # Act
        result = await time_api.get(team_id, time_entry_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/team/{team_id}/time_entries/{time_entry_id}")
        assert isinstance(result, TimeEntryResponse)
        assert result.id == "entry_123"

    @pytest.mark.asyncio
    async def test_get_time_entry_returns_none_on_failure(self, time_api, mock_api_client):
        """Test getting a time entry that fails returns None."""
        # Arrange
        team_id = "team_001"
        time_entry_id = "entry_123"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Not found"}, headers={}
        )

        # Act
        result = await time_api.get(team_id, time_entry_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_time_entries(self, time_api, mock_api_client, sample_time_entry_list_data):
        """Test listing time entries with query parameters."""
        # Arrange
        team_id = "team_001"
        query = TimeEntryListQuery(task_id="task_456", limit=50)
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_time_entry_list_data, headers={}
        )

        # Act
        result = await time_api.list(team_id, query)

        # Assert
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == f"/team/{team_id}/time_entries"
        assert isinstance(result, TimeEntryListResponse)
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_list_time_entries_returns_none_on_failure(self, time_api, mock_api_client):
        """Test listing time entries that fails returns None."""
        # Arrange
        team_id = "team_001"
        query = TimeEntryListQuery(task_id="task_456", limit=50)
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await time_api.list(team_id, query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_time_entry(self, time_api, mock_api_client, sample_time_entry_data):
        """Test updating a time entry."""
        # Arrange
        team_id = "team_001"
        time_entry_id = "entry_123"
        time_entry_update = TimeEntryUpdate(duration=7200000)
        mock_api_client.put.return_value = APIResponse(
            success=True, status_code=200, data=sample_time_entry_data, headers={}
        )

        # Act
        result = await time_api.update(team_id, time_entry_id, time_entry_update)

        # Assert
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"/team/{team_id}/time_entries/{time_entry_id}"
        assert isinstance(result, TimeEntryResponse)

    @pytest.mark.asyncio
    async def test_update_time_entry_returns_none_on_failure(self, time_api, mock_api_client):
        """Test updating a time entry that fails returns None."""
        # Arrange
        team_id = "team_001"
        time_entry_id = "entry_123"
        time_entry_update = TimeEntryUpdate(duration=7200000)
        mock_api_client.put.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await time_api.update(team_id, time_entry_id, time_entry_update)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_time_entry(self, time_api, mock_api_client):
        """Test deleting a time entry."""
        # Arrange
        team_id = "team_001"
        time_entry_id = "entry_123"
        mock_api_client.delete.return_value = APIResponse(success=True, status_code=200, data=None, headers={})

        # Act
        result = await time_api.delete(team_id, time_entry_id)

        # Assert
        mock_api_client.delete.assert_called_once_with(f"/team/{team_id}/time_entries/{time_entry_id}")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_time_entry_returns_false_on_failure(self, time_api, mock_api_client):
        """Test deleting a time entry that fails returns False."""
        # Arrange
        team_id = "team_001"
        time_entry_id = "entry_123"
        mock_api_client.delete.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Not found"}, headers={}
        )

        # Act
        result = await time_api.delete(team_id, time_entry_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_start_tracking(self, time_api, mock_api_client):
        """Test starting time tracking for a task."""
        # Arrange
        task_id = "task_123"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})

        # Act
        result = await time_api.start_tracking(task_id)

        # Assert
        mock_api_client.post.assert_called_once_with(f"/task/{task_id}/time_tracking/start")
        assert result is True

    @pytest.mark.asyncio
    async def test_start_tracking_returns_false_on_failure(self, time_api, mock_api_client):
        """Test starting tracking that fails returns False."""
        # Arrange
        task_id = "task_123"
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await time_api.start_tracking(task_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_stop_tracking(self, time_api, mock_api_client):
        """Test stopping time tracking for a task."""
        # Arrange
        task_id = "task_123"
        description = "Completed implementation"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})

        # Act
        result = await time_api.stop_tracking(task_id, description)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/task/{task_id}/time_tracking/stop"
        assert call_args[1]["data"] == {"description": description}
        assert result is True

    @pytest.mark.asyncio
    async def test_stop_tracking_without_description(self, time_api, mock_api_client):
        """Test stopping tracking without description."""
        # Arrange
        task_id = "task_123"
        mock_api_client.post.return_value = APIResponse(success=True, status_code=200, data=None, headers={})

        # Act
        result = await time_api.stop_tracking(task_id)

        # Assert
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"/task/{task_id}/time_tracking/stop"
        assert call_args[1]["data"] is None
        assert result is True

    @pytest.mark.asyncio
    async def test_stop_tracking_returns_false_on_failure(self, time_api, mock_api_client):
        """Test stopping tracking that fails returns False."""
        # Arrange
        task_id = "task_123"
        mock_api_client.post.return_value = APIResponse(
            success=False, status_code=400, data={"err": "Invalid request"}, headers={}
        )

        # Act
        result = await time_api.stop_tracking(task_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_tracking_status(self, time_api, mock_api_client, sample_tracking_status_data):
        """Test getting time tracking status for a task."""
        # Arrange
        task_id = "task_123"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_tracking_status_data, headers={}
        )

        # Act
        result = await time_api.get_tracking_status(task_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/task/{task_id}/time_tracking")
        assert isinstance(result, TimeTrackingStatusResponse)
        assert result.active is True
        assert result.task_id == "task_123"

    @pytest.mark.asyncio
    async def test_get_tracking_status_returns_none_on_failure(self, time_api, mock_api_client):
        """Test getting tracking status that fails returns None."""
        # Arrange
        task_id = "task_123"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Not found"}, headers={}
        )

        # Act
        result = await time_api.get_tracking_status(task_id)

        # Assert
        assert result is None
