"""MCP tools for ClickUp Folders.

Tools:
- folder.create|get|update|delete
- folder.list_in_space
"""

from typing import List

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError, ResourceNotFoundError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.folder import (
    FolderCreateInput,
    FolderDeleteInput,
    FolderGetInput,
    FolderListInSpaceInput,
    FolderUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult
from clickup_mcp.mcp_server.models.outputs.folder import (
    FolderListItem,
    FolderListResult,
    FolderResult,
)
from clickup_mcp.models.domain.folder import ClickUpFolder
from clickup_mcp.models.mapping.folder_mapper import FolderMapper

from .app import mcp


@mcp.tool(
    name="folder.create",
    description=(
        "Create a folder under a space to group lists. Discover `space_id` via `workspace.list` → `space.list`. "
        "HTTP: POST /space/{space_id}/folder."
    ),
)
@handle_tool_errors
async def folder_create(input: FolderCreateInput) -> FolderResult | None:
    client = ClickUpAPIClientFactory.get()
    domain = FolderMapper.from_create_input(input)
    dto = FolderMapper.to_create_dto(domain)
    async with client:
        resp = await client.folder.create(input.space_id, dto)
    if not resp:
        raise ClickUpAPIError("Create folder failed")
    d = FolderMapper.to_domain(resp)
    return FolderMapper.to_folder_result_output(d)


@mcp.tool(
    name="folder.get",
    description=(
        "Get a folder by ID. If unknown, list folders via `folder.list_in_space`. HTTP: GET /folder/{folder_id}."
    ),
)
@handle_tool_errors
async def folder_get(input: FolderGetInput) -> FolderResult | None:
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.folder.get(input.folder_id)
    if not resp:
        raise ResourceNotFoundError("Folder not found")
    d = FolderMapper.to_domain(resp)
    return FolderMapper.to_folder_result_output(d)


@mcp.tool(
    name="folder.update",
    description=("Rename a folder. Only name updates supported here. HTTP: PUT /folder/{folder_id}."),
)
@handle_tool_errors
async def folder_update(input: FolderUpdateInput) -> FolderResult | None:
    client = ClickUpAPIClientFactory.get()
    domain = FolderMapper.from_update_input(input)
    dto = FolderMapper.to_update_dto(domain)
    async with client:
        resp = await client.folder.update(input.folder_id, dto)
    if not resp:
        raise ResourceNotFoundError("Folder not found")
    d = FolderMapper.to_domain(resp)
    return FolderResult(id=d.id, name=d.name, space_id=d.space_id)


@mcp.tool(
    name="folder.delete",
    description=("Delete a folder by ID (irreversible; permission-scoped). HTTP: DELETE /folder/{folder_id}."),
)
@handle_tool_errors
async def folder_delete(input: FolderDeleteInput) -> DeletionResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.folder.delete(input.folder_id)
    return DeletionResult(deleted=bool(ok))


@mcp.tool(
    name="folder.list_in_space",
    description=("List folders in a space to discover container IDs for lists. HTTP: GET /space/{space_id}/folder."),
)
@handle_tool_errors
async def folder_list_in_space(input: FolderListInSpaceInput) -> FolderListResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        folders = await client.folder.get_all(input.space_id)
    items: List[FolderListItem] = []
    for f in folders:
        d = FolderMapper.to_domain(f)
        items.append(FolderMapper.to_folder_list_item_output(d))
    return FolderListResult(items=items)
