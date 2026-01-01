"""MCP tools for ClickUp Lists.

Tools:
- list.create|get|update|delete
- list.list_in_folder
- list.list_in_space_folderless
- list.add_task / list.remove_task (TIML)
"""

from typing import List

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.exceptions import ClickUpAPIError
from clickup_mcp.mcp_server.errors import handle_tool_errors
from clickup_mcp.mcp_server.models.inputs.list_ import (
    ListAddTaskInput,
    ListCreateInput,
    ListDeleteInput,
    ListGetInput,
    ListListInFolderInput,
    ListListInSpaceFolderlessInput,
    ListRemoveTaskInput,
    ListUpdateInput,
)
from clickup_mcp.mcp_server.models.outputs.common import DeletionResult, OperationResult
from clickup_mcp.mcp_server.models.outputs.list import (
    ListListItem,
    ListListResult,
    ListResult,
)
from clickup_mcp.models.mapping.list_mapper import ListMapper

from .app import mcp


@mcp.tool(
    title="Create List",
    name="list.create",
    description=(
        "Create a list under a folder. Discover `folder_id` via `workspace.list` → `space.list` → `folder.list_in_space`. "
        "Constraints: `priority` 1..4; due fields are epoch ms. HTTP: POST /folder/{folder_id}/list."
    ),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_create(input: ListCreateInput) -> ListResult | None:
    """
    Create a list under a folder.

    API:
        POST /folder/{folder_id}/list

    Args:
        input: ListCreateInput with `folder_id` and list fields (e.g., name)

    Returns:
        ListResult | None: Created list projection, or None on failure

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., VALIDATION_ERROR, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await list_create(ListCreateInput(folder_id="fld_1", name="Sprint Backlog"))
        if response.ok and response.result:
            print(response.result.id)
    """
    client = ClickUpAPIClientFactory.get()
    domain = ListMapper.from_create_input(input)
    dto = ListMapper.to_create_dto(domain)
    async with client:
        resp = await client.list.create(input.folder_id, dto)
    if not resp:
        raise ClickUpAPIError("Create list failed")
    d = ListMapper.to_domain(resp)
    return ListMapper.to_list_result_output(d)


@mcp.tool(
    title="Get List",
    name="list.get",
    description=(
        "Get a list by ID. If unknown, list via `list.list_in_folder` or `list.list_in_space_folderless`. "
        "HTTP: GET /list/{list_id}."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_get(input: ListGetInput) -> ListResult | None:
    """
    Get a list by ID.

    API:
        GET /list/{list_id}

    Args:
        input: ListGetInput with `list_id`

    Returns:
        ListResult | None: List projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, PERMISSION_DENIED, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await list_get(ListGetInput(list_id="lst_1"))
        if response.ok and response.result:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.list.get(input.list_id)
    if not resp:
        return None
    d = ListMapper.to_domain(resp)
    return ListMapper.to_list_result_output(d)


@mcp.tool(
    title="Update List",
    name="list.update",
    description=("Update list metadata (name/content/status/priority/assignee/due fields). HTTP: PUT /list/{list_id}."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_update(input: ListUpdateInput) -> ListResult | None:
    """
    Update list metadata and scheduling fields.

    API:
        PUT /list/{list_id}

    Args:
        input: ListUpdateInput with `list_id` and fields to update

    Returns:
        ListResult | None: Updated list projection, or None if not found

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues (e.g., NOT_FOUND, VALIDATION_ERROR, RATE_LIMIT).

    Examples:
        # Python (async)
        response = await list_update(ListUpdateInput(list_id="lst_1", name="Sprint 14"))
        if response.ok and response.result:
            print(response.result.name)
    """
    client = ClickUpAPIClientFactory.get()
    domain = ListMapper.from_update_input(input)
    dto = ListMapper.to_update_dto(domain)
    async with client:
        resp = await client.list.update(input.list_id, dto)
    if not resp:
        return None
    d = ListMapper.to_domain(resp)
    return ListMapper.to_list_result_output(d)


@mcp.tool(
    title="Delete List",
    name="list.delete",
    description=("Delete a list by ID (irreversible; permission-scoped). HTTP: DELETE /list/{list_id}."),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_delete(input: ListDeleteInput) -> DeletionResult:
    """
    Delete a list by ID.

    API:
        DELETE /list/{list_id}

    Args:
        input: ListDeleteInput with `list_id`

    Returns:
        DeletionResult: `deleted=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await list_delete(ListDeleteInput(list_id="lst_1"))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.list.delete(input.list_id)
    return DeletionResult(deleted=bool(ok))


@mcp.tool(
    title="List Lists in Folder",
    name="list.list_in_folder",
    description=("List lists in a folder to discover list IDs. HTTP: GET /folder/{folder_id}/list."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_list_in_folder(input: ListListInFolderInput) -> ListListResult:
    """
    List lists in a folder.

    API:
        GET /folder/{folder_id}/list

    Args:
        input: ListListInFolderInput with `folder_id`

    Returns:
        ListListResult: Items with id/name/status/folder_id/space_id

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await list_list_in_folder(ListListInFolderInput(folder_id="fld_1"))
        if response.ok:
            for it in response.result.items:
                print(it.id, it.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        lists = await client.list.get_all_in_folder(input.folder_id)
    items: List[ListListItem] = []
    for l in lists:
        d = ListMapper.to_domain(l)
        items.append(ListMapper.to_list_list_item_output(d))
    return ListListResult(items=items)


@mcp.tool(
    title="List Folderless Lists in Space",
    name="list.list_in_space_folderless",
    description=("List folderless lists in a space to discover list IDs. HTTP: GET /space/{space_id}/list."),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_list_in_space_folderless(input: ListListInSpaceFolderlessInput) -> ListListResult:
    """
    List folderless lists in a space.

    API:
        GET /space/{space_id}/list

    Args:
        input: ListListInSpaceFolderlessInput with `space_id`

    Returns:
        ListListResult: Items with id/name/status/folder_id/space_id

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues indicating the error category.

    Examples:
        # Python (async)
        response = await list_list_in_space_folderless(ListListInSpaceFolderlessInput(space_id="spc_1"))
        if response.ok:
            for it in response.result.items:
                print(it.id, it.name)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        lists = await client.list.get_all_folderless(input.space_id)
    items: List[ListListItem] = []
    for l in lists:
        d = ListMapper.to_domain(l)
        items.append(ListMapper.to_list_list_item_output(d))
    return ListListResult(items=items)


@mcp.tool(
    title="Add Task to List",
    name="list.add_task",
    description=("Add an existing task to a list (TIML must be enabled). HTTP: POST /list/{list_id}/task/{task_id}."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_add_task(input: ListAddTaskInput) -> OperationResult:
    """
    Add an existing task to a list (TIML).

    API:
        POST /list/{list_id}/task/{task_id}

    Args:
        input: ListAddTaskInput with `list_id` and `task_id`

    Returns:
        OperationResult: `ok=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await list_add_task(ListAddTaskInput(list_id="lst_1", task_id="tsk_1"))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.list.add_task(input.list_id, input.task_id)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    title="Remove Task from List",
    name="list.remove_task",
    description=("Remove a task from a secondary list (TIML). HTTP: DELETE /list/{list_id}/task/{task_id}."),
    annotations={
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
@handle_tool_errors
async def list_remove_task(input: ListRemoveTaskInput) -> OperationResult:
    """
    Remove a task from a secondary list (TIML).

    API:
        DELETE /list/{list_id}/task/{task_id}

    Args:
        input: ListRemoveTaskInput with `list_id` and `task_id`

    Returns:
        OperationResult: `ok=True` on success

    Error Handling:
        Decorated with `@handle_tool_errors`, returns ToolResponse at runtime. On failure,
        `ok=False` with issues classifying the error.

    Examples:
        # Python (async)
        response = await list_remove_task(ListRemoveTaskInput(list_id="lst_1", task_id="tsk_1"))
        print(response.ok)
    """
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.list.remove_task(input.list_id, input.task_id)
    return OperationResult(ok=bool(ok))
