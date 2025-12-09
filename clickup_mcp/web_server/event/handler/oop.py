"""
OOP-style ClickUp webhook handler base class.

Design:
- Subclass `BaseClickUpWebhookHandler` and override `on_*` methods for events you care about.
- The base class auto-registers overridden methods into the central registry on instantiation.
- Instances are callable and route incoming events to the appropriate overridden method.

Registration semantics:
- During `__init__`, the base inspects overridden methods and registers them with `get_registry()`.
- Only methods actually overridden by the subclass are registered.

Usage Example:
    from clickup_mcp.web_server.event.handler.oop import BaseClickUpWebhookHandler
    from clickup_mcp.web_server.event.models import ClickUpWebhookEvent

    class TaskStatusHandler(BaseClickUpWebhookHandler):
        async def on_task_status_updated(self, event: ClickUpWebhookEvent) -> None:
            print("Status updated", event.body.get("task_id"))

    # Instantiate to register handlers
    _ = TaskStatusHandler()
"""

from abc import ABC
from typing import Optional

from clickup_mcp.web_server.event.models import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)

from .registry import AsyncHandler, get_registry


class BaseClickUpWebhookHandler(ABC):
    """
    OOP style handler base for ClickUp webhooks.

    Subclasses implement one or more `on_*` methods corresponding to event types
    (e.g., `on_task_status_updated`). The base automatically registers overridden
    methods into the global registry.

    Notes:
    - Creating an instance triggers registration.
    - The instance is also callable and will dispatch events to the resolved method.
    """

    def __init__(self) -> None:
        self._register_overridden_handlers()

    async def __call__(self, event: ClickUpWebhookEvent) -> None:
        handler = self._resolve_handler(event.type)
        if handler is not None:
            await handler(event)

    # ----- Hooks to be optionally overridden by subclasses -----

    async def on_task_status_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_assignee_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_due_date_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_tag_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_moved(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_comment_posted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_comment_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_time_estimate_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_time_tracked_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_priority_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_created(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_task_deleted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    # List events
    async def on_list_created(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_list_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_list_deleted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    # Folder events
    async def on_folder_created(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_folder_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_folder_deleted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    # Space events
    async def on_space_created(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_space_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_space_deleted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    # Goal events
    async def on_goal_created(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_goal_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_goal_deleted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    # Key Result events
    async def on_key_result_created(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_key_result_updated(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    async def on_key_result_deleted(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover
        ...

    # ----- Internal helpers -----

    def _resolve_handler(self, event_type: ClickUpWebhookEventType) -> Optional[AsyncHandler]:
        mapping: dict[ClickUpWebhookEventType, AsyncHandler] = {
            # Task
            ClickUpWebhookEventType.TASK_CREATED: self.on_task_created,
            ClickUpWebhookEventType.TASK_UPDATED: self.on_task_updated,
            ClickUpWebhookEventType.TASK_DELETED: self.on_task_deleted,
            ClickUpWebhookEventType.TASK_STATUS_UPDATED: self.on_task_status_updated,
            ClickUpWebhookEventType.TASK_ASSIGNEE_UPDATED: self.on_task_assignee_updated,
            ClickUpWebhookEventType.TASK_DUE_DATE_UPDATED: self.on_task_due_date_updated,
            ClickUpWebhookEventType.TASK_TAG_UPDATED: self.on_task_tag_updated,
            ClickUpWebhookEventType.TASK_MOVED: self.on_task_moved,
            ClickUpWebhookEventType.TASK_COMMENT_POSTED: self.on_task_comment_posted,
            ClickUpWebhookEventType.TASK_COMMENT_UPDATED: self.on_task_comment_updated,
            ClickUpWebhookEventType.TASK_TIME_ESTIMATE_UPDATED: self.on_task_time_estimate_updated,
            ClickUpWebhookEventType.TASK_TIME_TRACKED_UPDATED: self.on_task_time_tracked_updated,
            ClickUpWebhookEventType.TASK_PRIORITY_UPDATED: self.on_task_priority_updated,
            # List
            ClickUpWebhookEventType.LIST_CREATED: self.on_list_created,
            ClickUpWebhookEventType.LIST_UPDATED: self.on_list_updated,
            ClickUpWebhookEventType.LIST_DELETED: self.on_list_deleted,
            # Folder
            ClickUpWebhookEventType.FOLDER_CREATED: self.on_folder_created,
            ClickUpWebhookEventType.FOLDER_UPDATED: self.on_folder_updated,
            ClickUpWebhookEventType.FOLDER_DELETED: self.on_folder_deleted,
            # Space
            ClickUpWebhookEventType.SPACE_CREATED: self.on_space_created,
            ClickUpWebhookEventType.SPACE_UPDATED: self.on_space_updated,
            ClickUpWebhookEventType.SPACE_DELETED: self.on_space_deleted,
            # Goal
            ClickUpWebhookEventType.GOAL_CREATED: self.on_goal_created,
            ClickUpWebhookEventType.GOAL_UPDATED: self.on_goal_updated,
            ClickUpWebhookEventType.GOAL_DELETED: self.on_goal_deleted,
            # Key Result
            ClickUpWebhookEventType.KEY_RESULT_CREATED: self.on_key_result_created,
            ClickUpWebhookEventType.KEY_RESULT_UPDATED: self.on_key_result_updated,
            ClickUpWebhookEventType.KEY_RESULT_DELETED: self.on_key_result_deleted,
        }
        return mapping.get(event_type)

    def _register_overridden_handlers(self) -> None:
        """
        Register only overridden `on_*` methods into the global registry.

        The method compares the subclass bound method's underlying function against
        the base class implementation to decide whether it's overridden.
        """
        registry = get_registry()

        for event_type in ClickUpWebhookEventType:
            handler = self._resolve_handler(event_type)
            if handler is None:
                continue
            # handler is a bound method; compare its underlying function to the base class method.
            method_name = handler.__name__
            base_method = getattr(BaseClickUpWebhookHandler, method_name, None)
            func = getattr(handler, "__func__", None)  # underlying function for bound method
            if base_method is not None and func is base_method:
                # Not overridden on subclass
                continue
            registry.register(event_type, handler)
