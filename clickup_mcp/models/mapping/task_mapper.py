"""Task DTO ↔ Domain mappers.

Translation layer between transport DTOs (ClickUp) and vendor-agnostic
Task domain entity. Keeps DTO shapes out of the domain.
"""

from __future__ import annotations

from clickup_mcp.models.domain.task import ClickUpTask
from clickup_mcp.models.mapping.priority import parse_priority_obj
from clickup_mcp.models.dto.task import TaskCreate, TaskResp, TaskUpdate
from clickup_mcp.mcp_server.models.outputs.task import TaskListItem, TaskResult
from clickup_mcp.models.domain.task_priority import (
    domain_priority_label,
    int_to_domain_priority,
)


class TaskMapper:
    """Static helpers to convert between Task DTOs and domain entity."""

    @staticmethod
    def to_domain(resp: TaskResp) -> ClickUpTask:
        """Map a TaskResp DTO to a ClickUpTask domain entity."""
        status_label: str | None = None
        if resp.status and resp.status.status:
            status_label = resp.status.status

        prio_int: int | None = None
        if resp.priority is not None:
            prio_int = parse_priority_obj(resp.priority)

        # Direct property access for clarity; DTOs provide defaults
        assignees = [u.id for u in resp.assignees if u.id is not None]
        folder_id = resp.folder.id if resp.folder and resp.folder.id else None
        list_id = resp.list.id if resp.list and resp.list.id else None
        space_id = resp.space.id if resp.space and resp.space.id else None

        cf = [{"id": c.id, "value": c.value} for c in resp.custom_fields if c.id is not None]

        return ClickUpTask(
            id=resp.id,
            name=resp.name,
            status=status_label,
            priority=prio_int,
            list_id=list_id,
            folder_id=folder_id,
            space_id=space_id,
            parent_id=resp.parent,
            assignee_ids=assignees,
            due_date=resp.due_date,
            time_estimate=resp.time_estimate,
            custom_fields=cf,
        )

    @staticmethod
    def to_create_dto(task: ClickUpTask) -> TaskCreate:
        """Map a ClickUpTask domain entity to a TaskCreate DTO."""
        return TaskCreate(
            name=task.name,
            status=task.status,
            priority=task.priority,
            assignees=list(task.assignee_ids),
            due_date=task.due_date,
            time_estimate=task.time_estimate,
            parent=task.parent_id,
            custom_fields=list(task.custom_fields),  # list of {id,value}
        )

    @staticmethod
    def to_update_dto(task: ClickUpTask) -> TaskUpdate:
        """Map a ClickUpTask domain entity to a TaskUpdate DTO.

        Note: Custom fields are not part of TaskUpdate per ClickUp API.
        """
        return TaskUpdate(
            name=task.name,
            status=task.status,
            priority=task.priority,
            assignees=list(task.assignee_ids) or None,
            due_date=task.due_date,
            time_estimate=task.time_estimate,
        )

    @staticmethod
    def to_task_result_output(task: ClickUpTask, url: str | None = None) -> TaskResult:
        """Map a ClickUpTask domain entity to the MCP TaskResult output model."""
        prio_info = None
        if task.priority is not None:
            try:
                d = int_to_domain_priority(task.priority)
                prio_info = {"value": task.priority, "label": domain_priority_label(d)}
            except Exception:
                prio_info = None

        return TaskResult(
            id=task.id,
            name=task.name,
            status=task.status,
            priority=task.priority,
            priority_info=prio_info,
            list_id=task.list_id,
            assignee_ids=list(task.assignee_ids),
            due_date_ms=task.due_date,
            url=url,
            parent_id=task.parent_id,
        )

    @staticmethod
    def to_task_list_item_output(task: ClickUpTask, url: str | None = None) -> TaskListItem:
        """Map a ClickUpTask domain entity to the MCP TaskListItem output model."""
        return TaskListItem(
            id=task.id,
            name=task.name,
            status=task.status,
            list_id=task.list_id,
            url=url,
        )
