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
    """
    Create a folder under a space.

    API:
        POST /space/{space_id}/folder

    Args:
        input: FolderCreateInput with `space_id` and folder fields (e.g., name)

    Returns:
        FolderResult | None: Created folder projection, or None on failure

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await folder_create(FolderCreateInput(space_id="spc_1", name="Planning"))
        if response.ok and response.result:
            print(response.result.id)
    """
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
    """
    Get a folder by ID.

    API:
        GET /folder/{folder_id}

    Args:
        input: FolderGetInput with `folder_id`

    Returns:
        FolderResult | None: Folder projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await folder_get(FolderGetInput(folder_id="fld_1"))
        if response.ok and response.result:
            print(response.result.name)
    """
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
    """
    Update folder metadata (name only).

    API:
        PUT /folder/{folder_id}

    Args:
        input: FolderUpdateInput with `folder_id` and new name

    Returns:
        FolderResult | None: Updated folder projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await folder_update(FolderUpdateInput(folder_id="fld_1", name="Roadmap"))
        if response.ok and response.result:
            print(response.result.name)
    """
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
    """
    Delete a folder by ID.

    API:
        DELETE /folder/{folder_id}

    Args:
        input: FolderDeleteInput with `folder_id`

    Returns:
        DeletionResult: `deleted=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await folder_delete(FolderDeleteInput(folder_id="fld_1"))
        print(response.ok)
    """
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
    """
    List folders in a space.

    API:
        GET /space/{space_id}/folder

    Args:
        input: FolderListInSpaceInput with `space_id`

    Returns:
        FolderListResult: Items with id/name/space_id

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await folder_list_in_space(FolderListInSpaceInput(space_id="spc_1"))
        if response.ok:
            for it in response.result.items:
                print(it.id, it.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        folders = await client.folder.get_all(input.space_id)
    items: List[FolderListItem] = []
    for f in folders:
        d = FolderMapper.to_domain(f)
        items.append(FolderMapper.to_folder_list_item_output(d))
    return FolderListResult(items=items)
