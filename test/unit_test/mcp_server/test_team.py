"""
Unit tests for the MCP server team functions.

This module contains tests for the MCP functions related to ClickUp teams.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.team import get_authorized_teams
from clickup_mcp.models.domain.team import ClickUpTeam, ClickUpTeamMember, ClickUpUser


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.team.ClickUpAPIClientFactory.get")
async def test_get_authorized_teams_success(mock_get_client: MagicMock) -> None:
    """Test getting authorized teams successfully."""
    # Create test data
    mock_teams = [
        ClickUpTeam(
            team_id="team1",
            name="Team One",
            color="#000000",
            avatar="https://example.com/avatar.jpg",
            members=[
                ClickUpTeamMember(
                    user=ClickUpUser(
                        user_id=1234,
                        username="test_user",
                        email="user@example.com",
                        color="#FF0000",
                    )
                )
            ],
        ),
        ClickUpTeam(
            team_id="team2",
            name="Team Two",
            color="#FFFFFF",
        ),
    ]

    # Set up mocks
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_authorized_teams = AsyncMock(return_value=mock_teams)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await get_authorized_teams()

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()
    
    # Verify the result format and content
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check first team data
    assert result[0]["team_id"] == "team1"
    assert result[0]["name"] == "Team One"
    assert result[0]["color"] == "#000000"
    assert result[0]["avatar"] == "https://example.com/avatar.jpg"
    
    # Check members data
    assert len(result[0]["members"]) == 1
    assert result[0]["members"][0]["user"]["user_id"] == 1234
    assert result[0]["members"][0]["user"]["username"] == "test_user"
    assert result[0]["members"][0]["user"]["email"] == "user@example.com"
    
    # Check second team
    assert result[1]["team_id"] == "team2"
    assert result[1]["name"] == "Team Two"
    assert result[1]["color"] == "#FFFFFF"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.team.ClickUpAPIClientFactory.get")
async def test_get_authorized_teams_empty_result(mock_get_client: MagicMock) -> None:
    """Test getting authorized teams when none are available."""
    # Set up mocks to return empty list
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_authorized_teams = AsyncMock(return_value=[])
    mock_get_client.return_value = mock_client

    # Call the function
    result = await get_authorized_teams()

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.team.ClickUpAPIClientFactory.get")
async def test_get_authorized_teams_with_missing_token(mock_get_client: MagicMock) -> None:
    """Test getting authorized teams when API token is missing."""
    # Set up mock to raise ValueError when called
    mock_get_client.side_effect = ValueError("ClickUp API token not found")

    # Call the function and expect the ValueError to be propagated
    with pytest.raises(ValueError, match="ClickUp API token not found"):
        await get_authorized_teams()

    # Verify the mock was called
    mock_get_client.assert_called_once()


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.team.ClickUpAPIClientFactory.get")
async def test_get_authorized_teams_with_error(mock_get_client: MagicMock) -> None:
    """Test handling an error when getting authorized teams."""
    # Create test error
    test_error = ValueError("Test error")

    # Set up mocks to simulate an error
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_authorized_teams = AsyncMock(side_effect=test_error)
    mock_get_client.return_value = mock_client

    # Call the function and expect the error to be wrapped in a ValueError
    with pytest.raises(ValueError, match="Error retrieving teams: Test error"):
        await get_authorized_teams()

    # Verify mocks were called
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()
