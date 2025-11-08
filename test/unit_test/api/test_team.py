"""
Tests for the Team API resource manager.

This module contains tests for the TeamAPI class that handles ClickUp Team/Workspace operations.
"""

import pytest

from clickup_mcp.api.team import TeamAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.domain.team import ClickUpTeam
from clickup_mcp.models.dto.space import SpaceResp


@pytest.mark.asyncio
class TestTeamAPI:
    """Tests for TeamAPI class."""

    async def test_get_authorized_teams(self, mocker):
        """Test getting authorized teams."""
        # Mock API response data
        mock_response_data = {
            "teams": [
                {
                    "id": "123456",
                    "name": "My Workspace",
                    "color": "#000000",
                    "avatar": "https://example.com/avatar.jpg",
                    "members": [
                        {
                            "user": {
                                "id": 7890,
                                "username": "John Doe",
                                "email": "john@example.com",
                                "color": "#FF0000",
                                "profilePicture": "https://example.com/profile.jpg",
                                "initials": "JD",
                            }
                        }
                    ],
                }
            ]
        }

        # Create mock response
        mock_response = APIResponse(status_code=200, data=mock_response_data)

        # Setup mock client
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        # Create team API instance
        team_api = TeamAPI(mock_client)

        # Call the method being tested
        teams = await team_api.get_authorized_teams()

        # Verify API call was made correctly
        mock_client.get.assert_called_once_with("/team")

        # Assert response is properly processed
        assert teams is not None
        assert isinstance(teams, list)
        assert len(teams) == 1
        assert isinstance(teams[0], ClickUpTeam)
        assert teams[0].team_id == "123456"
        assert teams[0].id == "123456"  # Test backwards compatibility
        assert teams[0].name == "My Workspace"
        assert teams[0].color == "#000000"
        assert teams[0].avatar == "https://example.com/avatar.jpg"
        assert len(teams[0].members) == 1
        assert teams[0].members[0].user.user_id == 7890
        assert teams[0].members[0].user.id == 7890  # Test backwards compatibility
        assert teams[0].members[0].user.username == "John Doe"

    async def test_get_authorized_teams_empty_response(self, mocker):
        """Test handling empty response when getting authorized teams."""
        # Create empty response
        mock_response = APIResponse(status_code=200, data={"teams": []})

        # Setup mock client
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        # Create team API instance
        team_api = TeamAPI(mock_client)

        # Call the method being tested
        teams = await team_api.get_authorized_teams()

        # Verify API call was made correctly
        mock_client.get.assert_called_once_with("/team")

        # Assert response is properly processed
        assert teams is not None
        assert isinstance(teams, list)
        assert len(teams) == 0

    async def test_get_spaces_success(self, mocker):
        """Test getting spaces for a team returns SpaceResp list."""
        team_id = "team_123"
        mock_response_data = {
            "spaces": [
                {
                    "id": "space_1",
                    "name": "Space One",
                    "private": False,
                    "statuses": [
                        {"id": "1", "status": "Open", "color": "#ff0000"},
                    ],
                    "multiple_assignees": True,
                    "features": {"due_dates": {"enabled": True}},
                }
            ]
        }

        mock_response = APIResponse(status_code=200, data=mock_response_data)
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        api = TeamAPI(mock_client)
        spaces = await api.get_spaces(team_id)

        mock_client.get.assert_called_once_with(f"/team/{team_id}/space")
        assert isinstance(spaces, list)
        assert len(spaces) == 1
        assert isinstance(spaces[0], SpaceResp)
        assert spaces[0].id == "space_1"
        assert spaces[0].name == "Space One"
        assert spaces[0].private is False
        assert spaces[0].multiple_assignees is True
        assert "due_dates" in (spaces[0].features or {})

    async def test_get_spaces_error_response(self, mocker):
        """Test get_spaces returns empty list on non-200 response."""
        team_id = "team_123"
        mock_response = APIResponse(status_code=500, data=None, success=False, error="Server Error")
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        api = TeamAPI(mock_client)
        spaces = await api.get_spaces(team_id)

        mock_client.get.assert_called_once_with(f"/team/{team_id}/space")
        assert spaces == []

    async def test_get_spaces_missing_key(self, mocker):
        """Test get_spaces returns empty list when 'spaces' key is missing."""
        team_id = "team_123"
        mock_response = APIResponse(status_code=200, data={})
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        api = TeamAPI(mock_client)
        spaces = await api.get_spaces(team_id)

        mock_client.get.assert_called_once_with(f"/team/{team_id}/space")
        assert spaces == []

    async def test_get_spaces_spaces_not_list(self, mocker):
        """Test get_spaces returns empty list when 'spaces' is not a list."""
        team_id = "team_123"
        mock_response = APIResponse(status_code=200, data={"spaces": {}})
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        api = TeamAPI(mock_client)
        spaces = await api.get_spaces(team_id)

        mock_client.get.assert_called_once_with(f"/team/{team_id}/space")
        assert spaces == []

    async def test_get_spaces_non_dict_data(self, mocker):
        """Test get_spaces returns empty list when response data is None (non-dict/absent)."""
        team_id = "team_123"
        mock_response = APIResponse(status_code=200, data=None)
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        api = TeamAPI(mock_client)
        spaces = await api.get_spaces(team_id)

        mock_client.get.assert_called_once_with(f"/team/{team_id}/space")
        assert spaces == []

    async def test_get_authorized_teams_error_response(self, mocker):
        """Test handling error response when getting authorized teams."""
        # Create error response
        mock_response = APIResponse(status_code=401, data=None, success=False, error="Unauthorized")

        # Setup mock client
        mock_client = mocker.AsyncMock(spec=ClickUpAPIClient)
        mock_client.get.return_value = mock_response

        # Create team API instance
        team_api = TeamAPI(mock_client)

        # Call the method being tested
        teams = await team_api.get_authorized_teams()

        # Verify API call was made correctly
        mock_client.get.assert_called_once_with("/team")

        # Assert response is properly processed - should return empty list on error
        assert teams is not None
        assert isinstance(teams, list)
        assert len(teams) == 0
