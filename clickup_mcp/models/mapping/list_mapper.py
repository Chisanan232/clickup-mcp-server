"""List DTO ↔ Domain mappers.

Translate between List transport DTOs and the ClickUpList domain entity.
"""

from __future__ import annotations

from clickup_mcp.models.domain.list import ClickUpList
from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate
from clickup_mcp.mcp_server.models.outputs.list import ListListItem, ListResult


class ListMapper:
    """Static helpers to convert between List DTOs and domain entity."""

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
    def to_list_result_output(lst: ClickUpList) -> ListResult:
        return ListResult(id=lst.id, name=lst.name, status=lst.status, folder_id=lst.folder_id, space_id=lst.space_id)

    @staticmethod
    def to_list_list_item_output(lst: ClickUpList) -> ListListItem:
        return ListListItem(id=lst.id, name=lst.name)
