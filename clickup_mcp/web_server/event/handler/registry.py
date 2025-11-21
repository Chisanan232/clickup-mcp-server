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

    Handlers are grouped by ClickUpWebhookEventType.
    """

    def __init__(self) -> None:
        self._handlers: Dict[ClickUpWebhookEventType, List[AsyncHandler]] = defaultdict(list)

    def register(self, event_type: ClickUpWebhookEventType, handler: AsyncHandler) -> None:
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: ClickUpWebhookEvent) -> None:
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            await handler(event)

    def clear(self) -> None:
        """Helper for tests to reset the registry."""
        self._handlers.clear()


_registry = ClickUpEventRegistry()


def get_registry() -> ClickUpEventRegistry:
    return _registry
