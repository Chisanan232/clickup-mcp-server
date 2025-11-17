"""List DTO ↔ Domain mappers.

Translate between List transport DTOs and the ClickUpList domain entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.list import ClickUpList
from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate
if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.outputs.list import ListListItem, ListResult
    from clickup_mcp.mcp_server.models.inputs.list_ import ListCreateInput, ListUpdateInput


class ListMapper:
    """Static helpers to convert between List DTOs and domain entity."""

    @staticmethod
    def from_create_input(input: "ListCreateInput") -> ClickUpList:
        """Map MCP ListCreateInput to List domain entity."""
        return ClickUpList(
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

    @staticmethod
    def from_update_input(input: "ListUpdateInput") -> ClickUpList:
        """Map MCP ListUpdateInput to List domain entity."""
        return ClickUpList(
            id=input.list_id,
            name=input.name or "",
            content=input.content,
            status=input.status,
            priority=input.priority,
            assignee_id=input.assignee,
            due_date=input.due_date,
            due_date_time=input.due_date_time,
        )

    @staticmethod
    def to_domain(resp: ListResp) -> ClickUpList:
        folder_id = resp.folder.id if resp.folder and resp.folder.id else None
        space_id = resp.space.id if resp.space and resp.space.id else None
        assignee_id = resp.assignee.id if resp.assignee and resp.assignee.id is not None else None
        return ClickUpList(
            id=resp.id,
            name=resp.name,
            content=resp.content,
            folder_id=folder_id,
            space_id=space_id,
            status=resp.status,
            priority=resp.priority,
            assignee_id=assignee_id,
            due_date=resp.due_date,
            due_date_time=resp.due_date_time,
        )

    @staticmethod
    def to_create_dto(lst: ClickUpList) -> ListCreate:
        return ListCreate(
            name=lst.name,
            content=lst.content,
            due_date=lst.due_date,
            due_date_time=lst.due_date_time,
            priority=lst.priority,
            assignee=lst.assignee_id if isinstance(lst.assignee_id, int) else None,
            status=lst.status,
        )

    @staticmethod
    def to_update_dto(lst: ClickUpList) -> ListUpdate:
        return ListUpdate(
            name=lst.name,
            content=lst.content,
            due_date=lst.due_date,
            due_date_time=lst.due_date_time,
            priority=lst.priority,
            assignee=lst.assignee_id if isinstance(lst.assignee_id, int) else None,
            status=lst.status,
        )

    @staticmethod
    def to_list_result_output(lst: ClickUpList) -> "ListResult":
        from clickup_mcp.mcp_server.models.outputs.list import ListResult

        return ListResult(id=lst.id, name=lst.name, status=lst.status, folder_id=lst.folder_id, space_id=lst.space_id)

    @staticmethod
    def to_list_list_item_output(lst: ClickUpList) -> "ListListItem":
        from clickup_mcp.mcp_server.models.outputs.list import ListListItem

        return ListListItem(id=lst.id, name=lst.name)
