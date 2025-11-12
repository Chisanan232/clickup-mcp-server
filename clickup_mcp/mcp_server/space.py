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
    SpaceListItem,
    SpaceListResult,
    SpaceResult,
)
from clickup_mcp.models.domain.space import ClickUpSpace
from clickup_mcp.models.mapping.space_mapper import SpaceMapper

from .app import mcp


@mcp.tool(
    name="get_space",
    title="Get ClickUp Space",
    description=("Get a ClickUp space by its ID. Use for backward-compat tests. HTTP: GET /space/{space_id}."),
)
async def get_space(space_id: str = "") -> dict[str, object] | None:
    """
    Get a ClickUp space by its ID. HTTP: GET /space/{space_id}
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
    if not input.space_id:
        raise ValueError("Space ID is required")
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.space.get(input.space_id)
    if not resp:
        raise ResourceNotFoundError("Space not found")
    d = SpaceMapper.to_domain(resp)
    return SpaceResult(id=d.id, name=d.name, private=d.private, team_id=d.team_id)


@mcp.tool(
    name="space.list",
    description=(
        "List spaces in a workspace (team). Use `workspace.list` first to discover team IDs. "
        "HTTP: GET /team/{team_id}/space."
    ),
)
@handle_tool_errors
async def space_list(input: SpaceListInput) -> SpaceListResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        spaces = await client.team.get_spaces(input.team_id)
    items = []
    for s in spaces:
        d = SpaceMapper.to_domain(s)
        items.append(SpaceListItem(id=d.id, name=d.name))
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
    client = ClickUpAPIClientFactory.get()
    # Input -> Domain -> DTO
    domain = ClickUpSpace(id="temp", name=input.name, multiple_assignees=input.multiple_assignees or False)
    dto = SpaceMapper.to_create_dto(domain)
    async with client:
        resp = await client.space.create(input.team_id, dto)
    if not resp:
        raise ClickUpAPIError("Create space failed")
    d = SpaceMapper.to_domain(resp)
    return SpaceResult(id=d.id, name=d.name, private=d.private, team_id=d.team_id)


@mcp.tool(
    name="space.update",
    description=(
        "Update space attributes (name, private, multiple_assignees). "
        "If you don't know `space_id`, call `space.list` first. HTTP: PUT /space/{space_id}."
    ),
)
@handle_tool_errors
async def space_update(input: SpaceUpdateInput) -> SpaceResult | None:
    client = ClickUpAPIClientFactory.get()
    # Build a domain model carrying fields to update; name/multiple_assignees/private may be None
    domain = ClickUpSpace(
        id=input.space_id,
        name=input.name or "",
        private=bool(input.private) if input.private is not None else False,
        multiple_assignees=bool(input.multiple_assignees) if input.multiple_assignees is not None else False,
    )
    dto = SpaceMapper.to_update_dto(domain)
    async with client:
        resp = await client.space.update(input.space_id, dto)
    if not resp:
        raise ResourceNotFoundError("Space not found")
    d = SpaceMapper.to_domain(resp)
    return SpaceResult(id=d.id, name=d.name, private=d.private, team_id=d.team_id)


@mcp.tool(
    name="space.delete",
    description=(
        "Delete a space by ID (irreversible; permission-scoped). Discover IDs via `space.list`. "
        "HTTP: DELETE /space/{space_id}."
    ),
)
@handle_tool_errors
async def space_delete(input: SpaceDeleteInput) -> DeletionResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.space.delete(input.space_id)
    return DeletionResult(deleted=bool(ok))
