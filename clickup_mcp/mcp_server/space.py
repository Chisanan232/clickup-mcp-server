"""MCP functions for ClickUp Spaces.

This module exposes space tools following the scope.operation naming:
- space.get, space.create, space.update, space.delete, space.list

It keeps backward-compatibility with an existing "get_space" tool used by tests.
"""

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError, ResourceNotFoundError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.space import (
    SpaceCreateInput,
    SpaceDeleteInput,
    SpaceGetInput,
    SpaceListInput,
    SpaceUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult
from clickup_mcp.mcp_server.models.outputs.space import (
    SpaceListResult,
    SpaceResult,
)
from clickup_mcp.models.mapping.space_mapper import SpaceMapper

from .app import mcp


@mcp.tool(
    name="get_space",
    title="Get ClickUp Space",
    description=("Get a ClickUp space by its ID. Use for backward-compat tests. HTTP: GET /space/{space_id}."),
)
async def get_space(space_id: str = "") -> dict[str, object] | None:
    """
    Get a ClickUp space by its ID.

    API:
        GET /space/{space_id}

    Args:
        space_id: The ID of the space to retrieve

    Returns:
        dict | None: Space domain model as a dict, or None if not found

    Examples:
        # Python (async)
        space = await get_space("spc_123")
        if space:
            print(space.get("name"))
    """
    if not space_id:
        raise ValueError("Space ID is required")

    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.space.get(space_id)
    if not resp:
        return None
    domain = SpaceMapper.to_domain(resp)
    return domain.model_dump()


@mcp.tool(
    name="space.get",
    description=(
        "Get a space by ID. If you don't know `space_id`, call `workspace.list` → `space.list` first. "
        "HTTP: GET /space/{space_id}."
    ),
)
@handle_tool_errors
async def space_get(input: SpaceGetInput) -> SpaceResult | None:
    """
    Get a space by ID.

    API:
        GET /space/{space_id}

    Args:
        input: SpaceGetInput with `space_id`

    Returns:
        SpaceResult | None: Space projection for MCP, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await space_get(SpaceGetInput(space_id="spc_123"))
        if response.ok and response.result:
            print(response.result.name)
    """
    if not input.space_id:
        raise ValueError("Space ID is required")
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.space.get(input.space_id)
    if not resp:
        raise ResourceNotFoundError("Space not found")
    d = SpaceMapper.to_domain(resp)
    return SpaceMapper.to_space_result_output(d)


@mcp.tool(
    name="space.list",
    description=(
        "List spaces in a workspace (team). Use `workspace.list` first to discover team IDs. "
        "HTTP: GET /team/{team_id}/space."
    ),
)
@handle_tool_errors
async def space_list(input: SpaceListInput) -> SpaceListResult:
    """
    List spaces in a workspace (team).

    API:
        GET /team/{team_id}/space

    Args:
        input: SpaceListInput with `team_id`

    Returns:
        SpaceListResult: Items of SpaceListItem with id/name/private/team_id

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await space_list(SpaceListInput(team_id="team_1"))
        if response.ok:
            for it in response.result.items:
                print(it.id, it.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        spaces = await client.team.get_spaces(input.team_id)
    items = []
    for s in spaces:
        d = SpaceMapper.to_domain(s)
        items.append(SpaceMapper.to_space_list_item_output(d))
    return SpaceListResult(items=items)


@mcp.tool(
    name="space.create",
    description=(
        "Create a space under a workspace (team). Discover `team_id` via `workspace.list`. "
        "HTTP: POST /team/{team_id}/space."
    ),
)
@handle_tool_errors
async def space_create(input: SpaceCreateInput) -> SpaceResult | None:
    """
    Create a space under a workspace (team).

    API:
        POST /team/{team_id}/space

    Args:
        input: SpaceCreateInput including `team_id` and fields for creation

    Returns:
        SpaceResult | None: Created space projection, or None if creation failed

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await space_create(SpaceCreateInput(team_id="team_1", name="Engineering"))
        if response.ok and response.result:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO (via mapper)
    domain = SpaceMapper.from_create_input(input)
    dto = SpaceMapper.to_create_dto(domain)
    async with client:
        resp = await client.space.create(input.team_id, dto)
    if not resp:
        raise ClickUpAPIError("Create space failed")
    d = SpaceMapper.to_domain(resp)
    return SpaceMapper.to_space_result_output(d)


@mcp.tool(
    name="space.update",
    description=(
        "Update space attributes (name, private, multiple_assignees). "
        "If you don't know `space_id`, call `space.list` first. HTTP: PUT /space/{space_id}."
    ),
)
@handle_tool_errors
async def space_update(input: SpaceUpdateInput) -> SpaceResult | None:
    """
    Update space attributes.

    API:
        PUT /space/{space_id}

    Args:
        input: SpaceUpdateInput with `space_id` and fields to update

    Returns:
        SpaceResult | None: Updated space projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await space_update(SpaceUpdateInput(space_id="spc_1", name="Platform"))
        if response.ok and response.result:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO (via mapper)
    domain = SpaceMapper.from_update_input(input)
    dto = SpaceMapper.to_update_dto(domain)
    async with client:
        resp = await client.space.update(input.space_id, dto)
    if not resp:
        raise ResourceNotFoundError("Space not found")
    d = SpaceMapper.to_domain(resp)
    return SpaceMapper.to_space_result_output(d)


@mcp.tool(
    name="space.delete",
    description=(
        "Delete a space by ID (irreversible; permission-scoped). Discover IDs via `space.list`. "
        "HTTP: DELETE /space/{space_id}."
    ),
)
@handle_tool_errors
async def space_delete(input: SpaceDeleteInput) -> DeletionResult:
    """
    Delete a space by ID.

    API:
        DELETE /space/{space_id}

    Args:
        input: SpaceDeleteInput with `space_id`

    Returns:
        DeletionResult: `deleted=True` on success, otherwise False

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await space_delete(SpaceDeleteInput(space_id="spc_1"))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.space.delete(input.space_id)
    return DeletionResult(deleted=bool(ok))
