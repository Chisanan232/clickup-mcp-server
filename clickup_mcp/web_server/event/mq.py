from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Any, Dict, Optional

from abe.backends.message_queue.base.protocol import MessageQueueBackend
from abe.backends.message_queue.loader import load_backend

from .bootstrap import import_handler_modules_from_env
from .handler import get_registry
from .models import ClickUpWebhookEvent, ClickUpWebhookEventType
from .sink import EventSink

_TOPIC_NAME = "clickup.webhooks"

# Global queue backend for publishing Slack events
_queue_backend: Optional[MessageQueueBackend] = None


def serialize_event(event: ClickUpWebhookEvent) -> Dict[str, Any]:
    return {
        "type": event.type.value,
        "body": event.body,
        "headers": dict(event.headers),
        "received_at": event.received_at.isoformat(),
        "delivery_id": event.delivery_id,
    }


def deserialize_event(message: Dict[str, Any]) -> ClickUpWebhookEvent:
    return ClickUpWebhookEvent(
        type=ClickUpWebhookEventType(message["type"]),
        body=message["body"],
        raw=message.get("body", {}),
        headers=message.get("headers") or {},
        received_at=datetime.fromisoformat(message["received_at"]),
        delivery_id=message.get("delivery_id"),
    )


def _load_backend_selected(backend_name: str) -> MessageQueueBackend:
    """Get or initialize the global queue backend.

    Returns
    -------
    MessageQueueBackend
        The global queue backend instance
    """
    os.environ["QUEUE_BACKEND"] = backend_name

    global _queue_backend
    if _queue_backend is None:
        _queue_backend = load_backend()
    return _queue_backend


class QueueEventSink(EventSink):
    def __init__(self, backend_name: str) -> None:
        self._backend_name: str = backend_name
        self._backend: Optional[MessageQueueBackend] = None
        self._topic: str = _TOPIC_NAME

    def _ensure_backend(self) -> MessageQueueBackend:
        if self._backend is not None:
            return self._backend
        self._backend = _load_backend_selected(self._backend_name)
        return self._backend

    async def handle(self, event: ClickUpWebhookEvent) -> None:
        backend = self._ensure_backend()
        payload = serialize_event(event)
        result = backend.publish(topic=self._topic, key=event.delivery_id or event.type.value, payload=payload)
        if asyncio.iscoroutine(result):
            await result


async def run_clickup_webhook_consumer(backend_name: str) -> None:
    """Consume webhook events and dispatch to the local registry."""
    # Make sure user handler modules are loaded so registry has handlers
    import_handler_modules_from_env()
    # Resolve loader the same way as the producer sink
    backend = _load_backend_selected(backend_name)
    # Register webhook event handler
    registry = get_registry()

    async for msg in backend.consume(topic=_TOPIC_NAME):
        event = deserialize_event(msg)
        await registry.dispatch(event)


def main() -> None:  # pragma: no cover - thin CLI wrapper
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Run ClickUp webhook consumer")
    parser.add_argument(
        "--queue-backend",
        dest="queue_backend",
        default=os.getenv("QUEUE_BACKEND", "local"),
        help="Queue backend name (default from QUEUE_BACKEND env)",
    )
    args = parser.parse_args()

    asyncio.run(run_clickup_webhook_consumer(backend_name=args.queue_backend))
