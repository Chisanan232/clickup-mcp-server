from __future__ import annotations

"""
Event sinks for ClickUp webhooks.

Design:
- Defines an `EventSink` abstraction that receives normalized `ClickUpWebhookEvent`
  and dispatches them either locally (in-process) or to a message queue (via mq.QueueEventSink).
- Selection is controlled by the `QUEUE_BACKEND` environment variable.

Backends:
- `local` (default): dispatches events directly to the in-process registry.
- any other value: resolved by mq.QueueEventSink which publishes to a queue.

Usage Examples:
    # Local sink (default)
    import os
    from clickup_mcp.web_server.event.sink import get_event_sink

    os.environ["QUEUE_BACKEND"] = "local"
    sink = get_event_sink()  # LocalEventSink

    # MQ-backed sink
    os.environ["QUEUE_BACKEND"] = "kafka"
    sink = get_event_sink()  # QueueEventSink
"""

import os
from abc import ABC, abstractmethod

from .handler import get_registry
from .models import ClickUpWebhookEvent


class EventSink(ABC):
    """
    Abstract event sink interface.

    Concrete sinks implement `handle()` to process a `ClickUpWebhookEvent`.
    """

    @abstractmethod
    async def handle(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover - interface
        """Process a single webhook event."""


class LocalEventSink(EventSink):
    """
    In-process event sink using the global handler registry.

    Useful for development or simple deployments without a queue.
    """

    async def handle(self, event: ClickUpWebhookEvent) -> None:
        await get_registry().dispatch(event)


def get_event_sink() -> EventSink:
    """
    Resolve event sink from `QUEUE_BACKEND` environment variable.

    Returns:
        EventSink: `LocalEventSink` when QUEUE_BACKEND=local (default), otherwise a `QueueEventSink`.

    Notes:
        Uses a lazy import for MQ sink to avoid hard dependency when not needed.
    """
    backend = os.getenv("QUEUE_BACKEND", "local").lower()
    if backend == "local":
        return LocalEventSink()
    # Lazy import to avoid hard dependency at import time
    from .mq import QueueEventSink

    return QueueEventSink(backend_name=backend)
