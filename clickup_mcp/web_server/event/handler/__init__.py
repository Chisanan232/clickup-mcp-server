"""
Handler registration entry points for ClickUp webhooks.

Provides:
- `clickup_event`: Decorator facade with enum and alias-based registration
- `BaseClickUpWebhookHandler`: OOP base that auto-registers `on_*` overrides
- `get_registry` / `ClickUpEventRegistry`: In-process async handler registry

Usage:
    from clickup_mcp.web_server.event.handler import clickup_event, BaseClickUpWebhookHandler
    from clickup_mcp.web_server.event.models import ClickUpWebhookEvent, ClickUpWebhookEventType

    @clickup_event.task_updated
    def handle(evt: ClickUpWebhookEvent):
        ...

    class TaskHandler(BaseClickUpWebhookHandler):
        async def on_task_created(self, evt: ClickUpWebhookEvent) -> None:
            ...
"""

from .decorators import clickup_event
from .oop import BaseClickUpWebhookHandler
from .registry import ClickUpEventRegistry, get_registry

__all__ = [
    "get_registry",
    "ClickUpEventRegistry",
    "clickup_event",
    "BaseClickUpWebhookHandler",
]
