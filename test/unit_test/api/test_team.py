"""
Tests for the Team API resource manager.

This module contains tests for the TeamAPI class that handles ClickUp Team/Workspace operations.
"""

import pytest

from clickup_mcp.api.team import TeamAPI
from clickup_mcp.client import APIResponse, ClickUpAPIClient
from clickup_mcp.models.domain.team import ClickUpTeam


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
