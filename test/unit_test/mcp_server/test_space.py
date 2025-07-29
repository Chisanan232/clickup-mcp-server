"""
Test module for ClickUp Space MCP functions.

This module contains tests for the MCP functions related to ClickUp spaces.
"""

from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.space import get_space
from clickup_mcp.models.domain.space import ClickUpSpace


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_success(mock_get_client: MagicMock) -> None:
    """Test getting a space successfully."""
    # Test data
    space_id: str = "test_space_id"
    mock_space: ClickUpSpace = ClickUpSpace(
        space_id=space_id,
        name="Test Space",
        private=False,
        statuses=[],
        multiple_assignees=False,
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(return_value=mock_space)
    mock_get_client.return_value = mock_client

    # Call the function
    result: Optional[Dict[str, Any]] = await get_space(space_id)

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.space.get.assert_called_once_with(space_id)
    assert result is not None
    assert result["space_id"] == space_id
    assert result["name"] == "Test Space"
    assert result == mock_space.model_dump()


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_not_found(mock_get_client: MagicMock) -> None:
    """Test getting a non-existent space."""
    # Test data
    space_id: str = "nonexistent_space_id"

    # Set up mocks with None return to simulate not found
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    # Call the function
    result: Optional[Dict[str, Any]] = await get_space(space_id)

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.space.get.assert_called_once_with(space_id)
    assert result is None


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_with_missing_token(mock_get_client: MagicMock) -> None:
    """Test getting a space when token is missing from environment."""
    # Set up mock to raise ValueError when called
    mock_get_client.side_effect = ValueError("ClickUp API token not found")

    # Test data
    space_id: str = "test_space_id"

    # Call the function and expect the ValueError to be propagated
    with pytest.raises(ValueError, match="ClickUp API token not found"):
        await get_space(space_id)

    # Verify the mock was called
    mock_get_client.assert_called_once()


@pytest.mark.asyncio
async def test_get_space_with_empty_space_id() -> None:
    """Test getting a space with an empty space ID."""
    # Test data
    space_id: str = ""

    # Call the function and expect an exception
    with pytest.raises(ValueError, match="Space ID is required"):
        await get_space(space_id)


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.space.ClickUpAPIClientFactory.get")
async def test_get_space_with_error(mock_get_client: MagicMock) -> None:
    """Test handling an error when getting a space."""
    # Test data
    space_id: str = "test_space_id"
    test_error: ValueError = ValueError("Test error")

    # Set up mocks to simulate an error during get
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.space.get = AsyncMock(side_effect=test_error)
    mock_get_client.return_value = mock_client

    # Call the function and expect the error to be propagated
    with pytest.raises(ValueError, match="Test error"):
        await get_space(space_id)

    # Verify mocks were called
    mock_get_client.assert_called_once()
    mock_client.space.get.assert_called_once_with(space_id)
