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
    workspace_list,
    workspace_update,
)
from clickup_mcp.models.dto.workspace import WorkspaceResp


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_list_success(mock_get_client: MagicMock) -> None:
    """Test listing workspaces successfully."""
    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_authorized_teams = AsyncMock(return_value=[])
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_list()

    # Assertions
    mock_get_client.assert_called_once()
    mock_client.team.get_authorized_teams.assert_called_once()
    assert result.ok is True
    assert result.result.items == []


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
async def test_workspace_get_with_avatar(mock_get_client: MagicMock) -> None:
    """Test getting a workspace with avatar."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(
        id=workspace_id, name="Engineering Team", color="#3498db", avatar="https://example.com/avatar.png"
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_get(WorkspaceGetInput(workspace_id=workspace_id))

    # Assertions
    assert result.ok is True
    assert result.result.id == workspace_id
    assert result.result.avatar == "https://example.com/avatar.png"


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
async def test_workspace_update_with_color_only(mock_get_client: MagicMock) -> None:
    """Test updating a workspace with only color."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(id=workspace_id, name="Engineering Team", color="#e74c3c")

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.update_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_update(WorkspaceUpdateInput(workspace_id=workspace_id, color="#e74c3c"))

    # Assertions
    assert result.ok is True
    assert result.result.color == "#e74c3c"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_delete_success(mock_get_client: MagicMock) -> None:
    """Test deleting a workspace successfully."""
    # Test data
    workspace_id: str = "9018752317"

    # Set up mocks
    mock_client = MagicMock()
    mock_team = MagicMock()
    mock_team.delete_workspace = AsyncMock(return_value=True)
    mock_client.team = mock_team
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_delete(WorkspaceDeleteInput(workspace_id=workspace_id))

    # Assertions
    mock_get_client.assert_called_once()
    assert result.ok is True
    assert result.result.deleted is True


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_delete_failure(mock_get_client: MagicMock) -> None:
    """Test deleting a workspace when API returns False."""
    mock_client = MagicMock()
    mock_team = MagicMock()
    mock_team.delete_workspace = AsyncMock(return_value=False)
    mock_client.team = mock_team
    mock_get_client.return_value = mock_client

    result = await workspace_delete(WorkspaceDeleteInput(workspace_id="nonexistent"))
    assert result.ok is True
    assert result.result.deleted is False


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_with_avatar(mock_get_client: MagicMock) -> None:
    """Test creating a workspace with avatar."""
    # Test data
    workspace_id: str = "9018752317"
    avatar_url = "https://example.com/avatar.png"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(
        id=workspace_id, name="Engineering Team", color="#3498db", avatar=avatar_url
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_create(WorkspaceCreateInput(name="Engineering Team", color="#3498db", avatar=avatar_url))

    # Assertions
    assert result.ok is True
    assert result.result.id == workspace_id
    assert result.result.avatar == avatar_url


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_with_name_only(mock_get_client: MagicMock) -> None:
    """Test creating a workspace with only name."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(
        id=workspace_id, name="Engineering Team", color=None, avatar=None
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_create(WorkspaceCreateInput(name="Engineering Team"))

    # Assertions
    assert result.ok is True
    assert result.result.id == workspace_id
    assert result.result.name == "Engineering Team"
    assert result.result.color is None
    assert result.result.avatar is None


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_with_special_characters(mock_get_client: MagicMock) -> None:
    """Test creating a workspace with special characters in name."""
    # Test data
    workspace_id: str = "9018752317"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(
        id=workspace_id, name="Team @#$%^&*()", color="#3498db"
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_create(WorkspaceCreateInput(name="Team @#$%^&*()", color="#3498db"))

    # Assertions
    assert result.ok is True
    assert result.result.name == "Team @#$%^&*()"


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_with_long_name(mock_get_client: MagicMock) -> None:
    """Test creating a workspace with a very long name."""
    # Test data
    workspace_id: str = "9018752317"
    long_name = "A" * 200
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(
        id=workspace_id, name=long_name, color="#3498db"
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_create(WorkspaceCreateInput(name=long_name, color="#3498db"))

    # Assertions
    assert result.ok is True
    assert result.result.name == long_name


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_create_with_invalid_color_format(mock_get_client: MagicMock) -> None:
    """Test creating a workspace with invalid color format (should be passed through to API)."""
    # Test data
    workspace_id: str = "9018752317"
    invalid_color = "not-a-valid-color"
    mock_workspace_resp: WorkspaceResp = WorkspaceResp(
        id=workspace_id, name="Engineering Team", color=invalid_color
    )

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.create_workspace = AsyncMock(return_value=mock_workspace_resp)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_create(WorkspaceCreateInput(name="Engineering Team", color=invalid_color))

    # Assertions - the API may reject this, but our layer should pass it through
    assert result.ok is True
    assert result.result.color == invalid_color


@pytest.mark.asyncio
@patch("clickup_mcp.mcp_server.workspace.ClickUpAPIClientFactory.get")
async def test_workspace_list_with_multiple_workspaces(mock_get_client: MagicMock) -> None:
    """Test listing multiple workspaces."""
    # Test data
    mock_teams = [
        WorkspaceResp(id="9018752317", name="Engineering Team", color="#3498db"),
        WorkspaceResp(id="9018752318", name="Marketing Team", color="#e74c3c"),
        WorkspaceResp(id="9018752319", name="Sales Team", color="#2ecc71"),
    ]

    # Set up mocks
    mock_client: MagicMock = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.team.get_authorized_teams = AsyncMock(return_value=mock_teams)
    mock_get_client.return_value = mock_client

    # Call the function
    result = await workspace_list()

    # Assertions
    assert result.ok is True
    assert len(result.result.items) == 3
    assert result.result.items[0].name == "Engineering Team"
    assert result.result.items[1].name == "Marketing Team"
    assert result.result.items[2].name == "Sales Team"
