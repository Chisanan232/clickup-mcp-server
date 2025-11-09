"""
Unit tests for Space API.
"""

from test.unit_test._base import BaseAPIClientTestSuite
from unittest.mock import AsyncMock, Mock

import pytest

from clickup_mcp.api.space import SpaceAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.dto.space import SpaceResp


class TestSpaceAPI(BaseAPIClientTestSuite):
    """Test cases for SpaceAPI."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        client = Mock(spec=ClickUpAPIClient)
        client.get = AsyncMock()
        return client

    @pytest.fixture
    def space_api(self, mock_api_client):
        """Create a SpaceAPI instance with a mock client."""
        return SpaceAPI(mock_api_client)

    @pytest.fixture
    def sample_space_data(self):
        """Return sample space data."""
        return {
            "id": "123456",
            "name": "Test Space",
            "private": False,
            "statuses": [
                {"id": "1", "status": "Open", "color": "#ff0000"},
                {"id": "2", "status": "Closed", "color": "#00ff00"},
            ],
            "multiple_assignees": True,
            "features": {"due_dates": {"enabled": True}, "time_tracking": {"enabled": False}},
        }

    @pytest.mark.asyncio
    async def test_get_space(self, space_api, mock_api_client, sample_space_data):
        """Test getting a space by ID."""
        # Arrange
        space_id = "123456"
        mock_api_client.get.return_value = APIResponse(
            success=True, status_code=200, data=sample_space_data, headers={}
        )

        # Act
        result = await space_api.get(space_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/space/{space_id}")
        assert isinstance(result, SpaceResp)
        assert result.id == space_id
        assert result.name == "Test Space"
        assert result.private is False
        assert len(result.statuses) == 2
        assert result.multiple_assignees is True
        assert "due_dates" in result.features
        assert result.features["due_dates"]["enabled"] is True

    @pytest.mark.asyncio
    async def test_get_space_returns_none_on_404(self, space_api, mock_api_client):
        """Test getting a space that doesn't exist returns None."""
        # Arrange
        space_id = "nonexistent"
        mock_api_client.get.return_value = APIResponse(
            success=False, status_code=404, data={"err": "Space not found"}, headers={}
        )

        # Act
        result = await space_api.get(space_id)

        # Assert
        mock_api_client.get.assert_called_once_with(f"/space/{space_id}")
        assert result is None
