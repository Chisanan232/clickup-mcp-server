from __future__ import annotations

import os
from abc import ABC, abstractmethod

from .handler import get_registry
from .models import ClickUpWebhookEvent


class EventSink(ABC):
    @abstractmethod
    async def handle(self, event: ClickUpWebhookEvent) -> None:  # pragma: no cover - interface
        ...


class LocalEventSink(EventSink):
    async def handle(self, event: ClickUpWebhookEvent) -> None:
        await get_registry().dispatch(event)


def get_event_sink() -> EventSink:
    backend = os.getenv("QUEUE_BACKEND", "local").lower()
    if backend == "local":
        return LocalEventSink()
    # Lazy import to avoid hard dependency at import time
    from .mq import QueueEventSink  # type: ignore

    return QueueEventSink(backend_name=backend)
