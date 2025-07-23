"""
Test module for ClickUp Space MCP functions.

This module contains tests for the MCP functions related to ClickUp spaces.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.space import get_space
from clickup_mcp.models.domain.space import ClickUpSpace


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_success(mock_get_client):
    """Test getting a space successfully."""
    # Test data
    space_id = "test_space_id"
    mock_space = ClickUpSpace(
        space_id=space_id,
        name="Test Space",
        private=False,
        statuses=[],
        multiple_assignees=False,
    )

    # Set up mocks
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(return_value=mock_space)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await get_space(space_id)

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.space.get.assert_called_once_with(space_id)
    assert result is not None
    assert result["space_id"] == space_id
    assert result["name"] == "Test Space"
    assert result == mock_space.model_dump()


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_not_found(mock_get_client):
    """Test getting a non-existent space."""
    # Test data
    space_id = "nonexistent_space_id"

    # Set up mocks with None return to simulate not found
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await get_space(space_id)

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.space.get.assert_called_once_with(space_id)
    assert result is None


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_with_missing_token(mock_get_client):
    """Test getting a space when token is missing from environment."""
    # Set up mock to raise ValueError when called
    mock_get_client.side_effect = ValueError("ClickUp API token not found")

    # Test data
    space_id = "test_space_id"

    # Call the function and expect the ValueError to be propagated
    with pytest.raises(ValueError, match="ClickUp API token not found"):
        await get_space(space_id)

    # Verify the mock was called
    mock_get_client.assert_called_once()


@pytest.mark.asyncio
async def test_get_space_with_empty_space_id():
    """Test getting a space with an empty space ID."""
    # Test data
    space_id = ""

    # Call the function and expect an exception
    with pytest.raises(ValueError, match="Space ID is required"):
        await get_space(space_id)


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_with_error(mock_get_client):
    """Test getting a space with an API error."""
    # Test data
    space_id = "test_space_id"
    api_token = "test_api_token"
    error_message = "API error occurred"

    # Set up mocks
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(side_effect=Exception(error_message))
    mock_get_client.return_value = mock_client

    # Call the function and expect an exception
    with pytest.raises(ValueError, match=f"Error retrieving space: {error_message}"):
        await get_space(space_id)

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.space.get.assert_called_once_with(space_id)
