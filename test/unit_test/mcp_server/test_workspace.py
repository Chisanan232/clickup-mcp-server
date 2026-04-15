"""
Test module for ClickUp Workspace MCP functions.

This module contains tests for the MCP functions related to ClickUp workspaces.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from clickup_mcp.mcp_server.errors import IssueCode
from clickup_mcp.mcp_server.models.inputs.workspace import (
    WorkspaceCreateInput,
    WorkspaceDeleteInput,
    WorkspaceGetInput,
    WorkspaceUpdateInput,
)
from clickup_mcp.mcp_server.workspace import (
    workspace_create,
    workspace_delete,
    workspace_get,
    workspace_update,
)
from clickup_mcp.models.dto.workspace import WorkspaceResp


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_success(mock_get_client: MagicMock) -> None:
    """Test creating a workspace successfully."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(id=workspace_id, name="Engineering Team", color="#3498db")

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_create(WorkspaceCreateInput(name="Engineering Team", color="#3498db"))

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.create_workspace.assert_called_once()
    assert result.ok is True
    assert result.result.id == workspace_id
    assert result.result.name == "Engineering Team"
    assert result.result.color == "#3498db"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_empty_response_maps_to_internal(mock_get_client: MagicMock) -> None:
    """Test creating a workspace when API returns None."""
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    result = await workspace_create(WorkspaceCreateInput(name="Engineering Team"))
    assert result.ok is False
    assert result.issues and result.issues[0].code == IssueCode.INTERNAL


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_get_success(mock_get_client: MagicMock) -> None:
    """Test getting a workspace successfully."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(id=workspace_id, name="Engineering Team", color="#3498db")

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_get(WorkspaceGetInput(workspace_id=workspace_id))

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.get_workspace.assert_called_once_with(workspace_id)
    assert result.ok is True
    assert result.result.id == workspace_id
    assert result.result.name == "Engineering Team"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_get_empty_response_maps_to_not_found(mock_get_client: MagicMock) -> None:
    """Test getting a workspace when API returns None."""
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_workspace = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    result = await workspace_get(WorkspaceGetInput(workspace_id="nonexistent"))
    assert result.ok is False
    assert result.issues and result.issues[0].code == IssueCode.NOT_FOUND


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_update_success(mock_get_client: MagicMock) -> None:
    """Test updating a workspace successfully."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(id=workspace_id, name="Updated Team Name", color="#e74c3c")

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.update_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_update(WorkspaceUpdateInput(workspace_id=workspace_id, name="Updated Team Name"))

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.update_workspace.assert_called_once()
    assert result.ok is True
    assert result.result.id == workspace_id
    assert result.result.name == "Updated Team Name"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_update_empty_response_maps_to_not_found(mock_get_client: MagicMock) -> None:
    """Test updating a workspace when API returns None."""
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.update_workspace = AsyncMock(return_value=None)
    mock_get_client.return_value = mock_client

    result = await workspace_update(WorkspaceUpdateInput(workspace_id="nonexistent", name="Updated"))
    assert result.ok is False
    assert result.issues and result.issues[0].code == IssueCode.NOT_FOUND


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_delete_success(mock_get_client: MagicMock) -> None:
    """Test deleting a workspace successfully."""
    # Test data
    workspace_id: str = "9018752317"

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.delete_workspace = AsyncMock(return_value=True)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_delete(WorkspaceDeleteInput(workspace_id=workspace_id))

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.delete_workspace.assert_called_once_with(workspace_id)
    assert result.ok is True
    assert result.result.ok is True


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_delete_failure(mock_get_client: MagicMock) -> None:
    """Test deleting a workspace when API returns False."""
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.delete_workspace = AsyncMock(return_value=False)
    mock_get_client.return_value = mock_client

    result = await workspace_delete(WorkspaceDeleteInput(workspace_id="nonexistent"))
    assert result.ok is True
    assert result.result.ok is False
