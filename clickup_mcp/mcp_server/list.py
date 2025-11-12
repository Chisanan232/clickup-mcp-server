"""MCP tools for ClickUp Lists.

Tools:
- list.create|get|update|delete
- list.list_in_folder
- list.list_in_space_folderless
- list.add_task / list.remove_task (TIML)
"""

from typing import List

from clickup_mcp.client import ClickUpAPIClientFactory
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
from clickup_mcp.models.domain.list import ClickUpList
from clickup_mcp.models.mapping.list_mapper import ListMapper

from .app import mcp


@mcp.tool(
    name="list.create",
    description=(
        "Create a list under a folder. Discover `folder_id` via `workspace.list` → `space.list` → `folder.list_in_space`. "
        "Constraints: `priority` 1..4; due fields are epoch ms. HTTP: POST /folder/{folder_id}/list."
    ),
)
async def list_create(input: ListCreateInput) -> ListResult | None:
    client = ClickUpAPIClientFactory.get()
    domain = ClickUpList(
        id="temp",
        name=input.name,
        content=input.content,
        folder_id=input.folder_id,
        status=input.status,
        priority=input.priority,
        assignee_id=input.assignee,
        due_date=input.due_date,
        due_date_time=input.due_date_time,
    )
    dto = ListMapper.to_create_dto(domain)
    async with client:
        resp = await client.list.create(input.folder_id, dto)
    if not resp:
        return None
    d = ListMapper.to_domain(resp)
    return ListResult(id=d.id, name=d.name, status=d.status, folder_id=d.folder_id, space_id=d.space_id)


@mcp.tool(
    name="list.get",
    description=(
        "Get a list by ID. If unknown, list via `list.list_in_folder` or `list.list_in_space_folderless`. "
        "HTTP: GET /list/{list_id}."
    ),
)
async def list_get(input: ListGetInput) -> ListResult | None:
    client = ClickUpAPIClientFactory.get()
    async with client:
        resp = await client.list.get(input.list_id)
    if not resp:
        return None
    d = ListMapper.to_domain(resp)
    return ListResult(id=d.id, name=d.name, status=d.status, folder_id=d.folder_id, space_id=d.space_id)


@mcp.tool(
    name="list.update",
    description=("Update list metadata (name/content/status/priority/assignee/due fields). HTTP: PUT /list/{list_id}."),
)
async def list_update(input: ListUpdateInput) -> ListResult | None:
    client = ClickUpAPIClientFactory.get()
    domain = ClickUpList(
        id=input.list_id,
        name=input.name or "",
        content=input.content,
        status=input.status,
        priority=input.priority,
        assignee_id=input.assignee,
        due_date=input.due_date,
        due_date_time=input.due_date_time,
    )
    dto = ListMapper.to_update_dto(domain)
    async with client:
        resp = await client.list.update(input.list_id, dto)
    if not resp:
        return None
    d = ListMapper.to_domain(resp)
    return ListResult(id=d.id, name=d.name, status=d.status, folder_id=d.folder_id, space_id=d.space_id)


@mcp.tool(
    name="list.delete",
    description=("Delete a list by ID (irreversible; permission-scoped). HTTP: DELETE /list/{list_id}."),
)
async def list_delete(input: ListDeleteInput) -> DeletionResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.list.delete(input.list_id)
    return DeletionResult(deleted=bool(ok))


@mcp.tool(
    name="list.list_in_folder",
    description=("List lists in a folder to discover list IDs. HTTP: GET /folder/{folder_id}/list."),
)
async def list_list_in_folder(input: ListListInFolderInput) -> ListListResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        lists = await client.list.get_all_in_folder(input.folder_id)
    items: List[ListListItem] = []
    for l in lists:
        d = ListMapper.to_domain(l)
        items.append(ListListItem(id=d.id, name=d.name))
    return ListListResult(items=items)


@mcp.tool(
    name="list.list_in_space_folderless",
    description=("List folderless lists in a space to discover list IDs. HTTP: GET /space/{space_id}/list."),
)
async def list_list_in_space_folderless(input: ListListInSpaceFolderlessInput) -> ListListResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        lists = await client.list.get_all_folderless(input.space_id)
    items: List[ListListItem] = []
    for l in lists:
        d = ListMapper.to_domain(l)
        items.append(ListListItem(id=d.id, name=d.name))
    return ListListResult(items=items)


@mcp.tool(
    name="list.add_task",
    description=("Add an existing task to a list (TIML must be enabled). HTTP: POST /list/{list_id}/task/{task_id}."),
)
async def list_add_task(input: ListAddTaskInput) -> OperationResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.list.add_task(input.list_id, input.task_id)
    return OperationResult(ok=bool(ok))


@mcp.tool(
    name="list.remove_task",
    description=("Remove a task from a secondary list (TIML). HTTP: DELETE /list/{list_id}/task/{task_id}."),
)
async def list_remove_task(input: ListRemoveTaskInput) -> OperationResult:
    client = ClickUpAPIClientFactory.get()
    async with client:
        ok = await client.list.remove_task(input.list_id, input.task_id)
    return OperationResult(ok=bool(ok))
