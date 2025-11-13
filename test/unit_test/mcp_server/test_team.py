"""
Unit tests for the MCP server team functions.

This module contains tests for the MCP functions related to ClickUp teams.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.team import get_authorized_teams
from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListResult
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
    envelope = await get_authorized_teams()

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()

    # Verify the result format and content
    assert envelope.ok is True
    assert isinstance(envelope.result, WorkspaceListResult)
    assert len(envelope.result.items) == 2

    # Check first team data
    first = envelope.result.items[0].model_dump()
    assert first["team_id"] == "team1"
    assert first["name"] == "Team One"

    # Check members data
    # Members are not included in WorkspaceListItem projection

    # Check second team
    second = envelope.result.items[1].model_dump()
    assert second["team_id"] == "team2"
    assert second["name"] == "Team Two"


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
    envelope = await get_authorized_teams()

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()

    assert envelope.ok is True
    assert isinstance(envelope.result, WorkspaceListResult)
    assert len(envelope.result.items) == 0


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.team.ClickUpAPIClientFactory.get")
async def test_get_authorized_teams_with_missing_token(mock_get_client: MagicMock) -> None:
    """Test getting authorized teams when API token is missing."""
    # Set up mock to raise ValueError when called
    mock_get_client.side_effect = ValueError("ClickUp API token not found")

    # Call the function; decorator should map error to envelope with issues
    envelope = await get_authorized_teams()
    assert envelope.ok is False
    assert len(envelope.issues) == 1

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

    # Call the function; decorator should map error to envelope with issues
    envelope = await get_authorized_teams()
    assert envelope.ok is False
    assert len(envelope.issues) == 1

    # Verify mocks were called
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()
