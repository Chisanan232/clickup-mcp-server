"""MCP tools for ClickUp Workspaces (a.k.a Teams in v2).

This module exposes workspace tools following the scope.operation naming:
- workspace.list, workspace.create, workspace.get, workspace.update, workspace.delete
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ResourceNotFoundError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.workspace import (
    WorkspaceCreateInput,
    WorkspaceDeleteInput,
    WorkspaceGetInput,
    WorkspaceUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult
from clickup_mcp.mcp_server.models.outputs.workspace import (
    WorkspaceListResult,
    WorkspaceResult,
)
from clickup_mcp.models.mapping.team_mapper import TeamMapper
from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

from .app import mcp


@mcp.tool(
    name="workspace.list",
    title="List Workspaces",
    description=(
        "List workspaces (teams) the token can access. Use this first to discover team IDs, then call "
        "`space.list` to enumerate spaces. HTTP: GET /team. Returns { workspaces: [{ team_id, name }] }."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workspace_list() -> WorkspaceListResult:
    """
    List workspaces (teams) accessible to the current token.

    API:
        GET /team

    Returns:
        WorkspaceListResult: Items containing `team_id` and `name` for each workspace.

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with one or more issues (with canonical codes like VALIDATION_ERROR,
        RATE_LIMIT, INTERNAL). On success, `ok=True` and `result` contains WorkspaceListResult.

    Examples:
        # Python (async)
        response = await workspace_list()
        if response.ok:
            for ws in response.result.items:
                print(ws.team_id, ws.name)
        else:
            for iss in response.issues:
                print(iss.code, iss.message)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        teams = await client.team.get_authorized_teams()
    return TeamMapper.to_workspace_list_result_output(teams)


@mcp.tool(
    name="workspace.create",
    title="Create Workspace",
    description=(
        "Create a new workspace (team) with a name, optional color, and avatar. "
        "HTTP: POST /team. Returns the created workspace details."
    ),
    annotations={
        "readOnlyHint": False,
        "openWorldHint": False,
    },
)
@handle_tool_errors
async def workspace_create(input: WorkspaceCreateInput) -> WorkspaceResult:
    """
    Create a new workspace (team).

    API:
        POST /team

    Args:
        input: WorkspaceCreateInput with name, optional color, and avatar

    Returns:
        WorkspaceResult: Created workspace details

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with issues (e.g., VALIDATION_ERROR, RATE_LIMIT, INTERNAL).

    Examples:
        # Python (async)
        response = await workspace_create(WorkspaceCreateInput(name="Engineering Team", color="#3498db"))
        if response.ok:
            print(response.result.id, response.result.name)
    """
    # Map MCP input to domain entity
    workspace_domain = WorkspaceMapper.from_create_input(input)
    # Convert domain to DTO for API request
    workspace_create_dto = WorkspaceMapper.to_create_dto(workspace_domain)

    # Call API
    client = ClickUpAPIClientFactory.get()
    async with client:
        workspace_resp = await client.team.create_workspace(workspace_create_dto)

    if workspace_resp is None:
        raise Exception("Failed to create workspace")

    # Convert API response to domain entity
    workspace_domain = WorkspaceMapper.to_domain(workspace_resp)
    # Convert domain to MCP output
    return WorkspaceMapper.to_workspace_result_output(workspace_domain)


@mcp.tool(
    name="workspace.get",
    title="Get Workspace",
    description=(
        "Get a workspace (team) by its ID. If you don't know the ID, call `workspace.list` first. "
        "HTTP: GET /team/{team_id}."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def workspace_get(input: WorkspaceGetInput) -> WorkspaceResult:
    """
    Get a workspace by ID.

    API:
        GET /team/{team_id}

    Args:
        input: WorkspaceGetInput with workspace_id

    Returns:
        WorkspaceResult: Workspace details

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await workspace_get(WorkspaceGetInput(workspace_id="9018752317"))
        if response.ok:
            print(response.result.name)
    """
    # Call API
    client = ClickUpAPIClientFactory.get()
    async with client:
        workspace_resp = await client.team.get_workspace(input.workspace_id)

    if workspace_resp is None:
        raise ResourceNotFoundError(f"Workspace not found: {input.workspace_id}")

    # Convert API response to domain entity
    workspace_domain = WorkspaceMapper.to_domain(workspace_resp)
    # Convert domain to MCP output
    return WorkspaceMapper.to_workspace_result_output(workspace_domain)


@mcp.tool(
    name="workspace.update",
    title="Update Workspace",
    description=(
        "Update an existing workspace's name, color, or avatar. "
        "HTTP: PUT /team/{team_id}. Returns the updated workspace details."
    ),
    annotations={
        "readOnlyHint": False,
        "openWorldHint": False,
    },
)
@handle_tool_errors
async def workspace_update(input: WorkspaceUpdateInput) -> WorkspaceResult:
    """
    Update a workspace.

    API:
        PUT /team/{team_id}

    Args:
        input: WorkspaceUpdateInput with workspace_id and optional fields to update

    Returns:
        WorkspaceResult: Updated workspace details

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await workspace_update(WorkspaceUpdateInput(workspace_id="9018752317", name="Updated Name"))
        if response.ok:
            print(response.result.name)
    """
    # Map MCP input to domain entity
    workspace_domain = WorkspaceMapper.from_update_input(input)
    # Convert domain to DTO for API request
    workspace_update_dto = WorkspaceMapper.to_update_dto(workspace_domain)

    # Call API
    client = ClickUpAPIClientFactory.get()
    async with client:
        workspace_resp = await client.team.update_workspace(input.workspace_id, workspace_update_dto)

    if workspace_resp is None:
        raise ResourceNotFoundError(f"Workspace not found: {input.workspace_id}")

    # Convert API response to domain entity
    workspace_domain = WorkspaceMapper.to_domain(workspace_resp)
    # Convert domain to MCP output
    return WorkspaceMapper.to_workspace_result_output(workspace_domain)


@mcp.tool(
    name="workspace.delete",
    title="Delete Workspace",
    description=(
        "Delete a workspace (team) by its ID. This action cannot be undone. "
        "HTTP: DELETE /team/{team_id}. Returns success/failure status."
    ),
    annotations={
        "readOnlyHint": False,
        "openWorldHint": False,
    },
)
@handle_tool_errors
async def workspace_delete(input: WorkspaceDeleteInput) -> DeletionResult:
    """
    Delete a workspace.

    API:
        DELETE /team/{team_id}

    Args:
        input: WorkspaceDeleteInput with workspace_id

    Returns:
        DeletionResult: Success status and message

    Error Handling:
        This function is wrapped by `@handle_tool_errors` and returns a ToolResponse at runtime.
        On failure, `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await workspace_delete(WorkspaceDeleteInput(workspace_id="9018752317"))
        if response.ok:
            print(response.result.deleted)
    """
    # Call API
    client = ClickUpAPIClientFactory.get()
    success = await client.team.delete_workspace(input.workspace_id)

    return DeletionResult(deleted=success)
