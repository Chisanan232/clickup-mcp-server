"""
Test module for ClickUp Space MCP functions.

This module contains tests for the MCP functions related to ClickUp spaces.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.space import get_space
from clickup_mcp.models.domain.space import ClickUpSpace


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.create_clickup_client")
async def test_get_space_success(mock_create_client):
    """Test getting a space successfully."""
    # Test data
    space_id = "test_space_id"
    api_token = "test_api_token"
    mock_space = ClickUpSpace(
        space_id=space_id,
        name="Test Space",
        private=False,
        statuses=[],
        multiple_assignees=False,
    )

    # Set up mock client
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(return_value=mock_space)
    mock_create_client.return_value = mock_client

    # Call the function
    result = await get_space(api_token, space_id)

    # Assertions
    mock_create_client.assert_called_once_with(api_token)
    mock_client.space.get.assert_called_once_with(space_id)
    assert result is not None
    assert result["space_id"] == space_id
    assert result["name"] == "Test Space"
    assert result == mock_space.model_dump()


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.create_clickup_client")
async def test_get_space_not_found(mock_create_client):
    """Test getting a non-existent space."""
    # Test data
    space_id = "nonexistent_space_id"
    api_token = "test_api_token"

    # Set up mock client
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(return_value=None)
    mock_create_client.return_value = mock_client

    # Call the function
    result = await get_space(api_token, space_id)

    # Assertions
    mock_create_client.assert_called_once_with(api_token)
    mock_client.space.get.assert_called_once_with(space_id)
    assert result is None


@pytest.mark.asyncio
async def test_get_space_with_empty_token():
    """Test getting a space with an empty API token."""
    # Test data
    space_id = "test_space_id"
    api_token = ""

    # Call the function and expect an exception
    with pytest.raises(ValueError, match="API token is required"):
        await get_space(api_token, space_id)


@pytest.mark.asyncio
async def test_get_space_with_empty_space_id():
    """Test getting a space with an empty space ID."""
    # Test data
    space_id = ""
    api_token = "test_api_token"

    # Call the function and expect an exception
    with pytest.raises(ValueError, match="Space ID is required"):
        await get_space(api_token, space_id)


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.create_clickup_client")
async def test_get_space_with_error(mock_create_client):
    """Test getting a space with an API error."""
    # Test data
    space_id = "test_space_id"
    api_token = "test_api_token"

    # Set up mock client to raise an exception
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(side_effect=Exception("API Error"))
    mock_create_client.return_value = mock_client

    # Call the function and expect an exception
    with pytest.raises(ValueError, match="Error retrieving space: API Error"):
        await get_space(api_token, space_id)

    # Assertions
    mock_create_client.assert_called_once_with(api_token)
    mock_client.space.get.assert_called_once_with(space_id)
