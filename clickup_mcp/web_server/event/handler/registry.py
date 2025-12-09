"""
ClickUp webhook event handler registry.

Design:
- Central in-process registry keyed by `ClickUpWebhookEventType` → list of async handlers.
- Used by decorator API and OOP base class to register handlers.
- `dispatch()` awaits all handlers registered for the event type.

Usage Example:
    from clickup_mcp.web_server.event.handler.registry import get_registry
    from clickup_mcp.web_server.event.models import ClickUpWebhookEvent, ClickUpWebhookEventType

    async def handle_task_updated(evt: ClickUpWebhookEvent) -> None:
        print("Task updated", evt.body.get("task_id"))

    reg = get_registry()
    reg.register(ClickUpWebhookEventType.TASK_UPDATED, handle_task_updated)
"""

from collections import defaultdict
from typing import Awaitable, Callable, Dict, List

from clickup_mcp.web_server.event.models import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)

AsyncHandler = Callable[[ClickUpWebhookEvent], Awaitable[None]]


class ClickUpEventRegistry:
    """
    Central registry of event handlers.

    Handlers are grouped by `ClickUpWebhookEventType` and stored as async callables.
    """

    def __init__(self) -> None:
        self._handlers: Dict[ClickUpWebhookEventType, List[AsyncHandler]] = defaultdict(list)

    def register(self, event_type: ClickUpWebhookEventType, handler: AsyncHandler) -> None:
        """Register an async handler for an event type."""
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: ClickUpWebhookEvent) -> None:
        """
        Dispatch an event to all registered handlers for its type.

        Handlers are awaited sequentially.
        """
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            await handler(event)

    def clear(self) -> None:
        """Helper for tests to reset the registry."""
        self._handlers.clear()


_registry = ClickUpEventRegistry()


def get_registry() -> ClickUpEventRegistry:
    """Return the process-global registry instance."""
    return _registry
