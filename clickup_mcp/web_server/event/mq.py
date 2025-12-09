from __future__ import annotations

"""
Message queue integration for ClickUp webhook events.

Design:
- Provides a queue-backed `EventSink` implementation (`QueueEventSink`) that publishes
  normalized webhook events to a topic (default: `clickup.webhooks`).
- Includes a simple consumer loop (`run_clickup_webhook_consumer`) that reads messages
  and dispatches them to the in-process registry.

Environment & configuration:
- Uses `QUEUE_BACKEND` to select a concrete message-queue backend via `abe` loader.
- Topic name is `_TOPIC_NAME` ("clickup.webhooks").

Usage Examples:
    # Producer path
    from clickup_mcp.web_server.event.mq import QueueEventSink
    sink = QueueEventSink(backend_name="kafka")
    await sink.handle(event)  # publishes serialized event to MQ

    # Consumer path
    import asyncio
    from clickup_mcp.web_server.event.mq import run_clickup_webhook_consumer
    asyncio.run(run_clickup_webhook_consumer(backend_name="kafka"))

See also:
- `clickup_mcp.web_server.event.handler.get_registry` – in-process registry used by consumer
- `clickup_mcp.web_server.event.bootstrap.import_handler_modules_from_env` – discover handlers
"""

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

# Global queue backend for publishing ClickUp webhook events
_queue_backend: Optional[MessageQueueBackend] = None


def serialize_event(event: ClickUpWebhookEvent) -> Dict[str, Any]:
    """
    Convert a `ClickUpWebhookEvent` into a transport-friendly dict.

    Args:
        event: Normalized webhook event

    Returns:
        Dict with primitives suitable for MQ payloads
    """
    return {
        "type": event.type.value,
        "body": event.body,
        "headers": dict(event.headers),
        "received_at": event.received_at.isoformat(),
        "delivery_id": event.delivery_id,
    }


def deserialize_event(message: Dict[str, Any]) -> ClickUpWebhookEvent:
    """
    Convert a MQ message payload into a `ClickUpWebhookEvent`.

    Args:
        message: Dict payload previously produced by `serialize_event`

    Returns:
        ClickUpWebhookEvent: normalized event object
    """
    return ClickUpWebhookEvent(
        type=ClickUpWebhookEventType(message["type"]),
        body=message["body"],
        raw=message.get("body", {}),
        headers=message.get("headers") or {},
        received_at=datetime.fromisoformat(message["received_at"]),
        delivery_id=message.get("delivery_id"),
    )


def _load_backend_selected(backend_name: str) -> MessageQueueBackend:
    """
    Get or initialize the global queue backend.

    Sets `QUEUE_BACKEND` then lazily loads a single global backend instance.

    Args:
        backend_name: Backend identifier (e.g., "kafka", "redis")

    Returns:
        MessageQueueBackend: Global backend instance
    """
    os.environ["QUEUE_BACKEND"] = backend_name

    global _queue_backend
    if _queue_backend is None:
        _queue_backend = load_backend()
    return _queue_backend


class QueueEventSink(EventSink):
    """
    MQ-backed event sink that publishes webhook events to a topic.

    Attributes:
        _backend_name: Backend name resolved by `abe` loader
        _backend: Cached backend instance
        _topic: Topic name (defaults to `clickup.webhooks`)

    Examples:
        sink = QueueEventSink(backend_name="kafka")
        await sink.handle(event)
    """

    def __init__(self, backend_name: str) -> None:
        self._backend_name: str = backend_name
        self._backend: Optional[MessageQueueBackend] = None
        self._topic: str = _TOPIC_NAME

    def _ensure_backend(self) -> MessageQueueBackend:
        """Lazily load and cache the queue backend instance."""
        if self._backend is not None:
            return self._backend
        self._backend = _load_backend_selected(self._backend_name)
        return self._backend

    async def handle(self, event: ClickUpWebhookEvent) -> None:
        """
        Publish the event to the configured MQ backend.

        Awaits if the backend returns a coroutine.
        """
        backend = self._ensure_backend()
        payload = serialize_event(event)
        result = backend.publish(key=self._topic, payload=payload)
        if asyncio.iscoroutine(result):
            await result


async def run_clickup_webhook_consumer(backend_name: str) -> None:
    """
    Consume webhook events from MQ and dispatch to the local registry.

    Steps:
    - Import user handler modules (ensures registry contains handlers)
    - Resolve backend via the same mechanism used by the producer
    - Consume messages and route to `get_registry().dispatch` after deserialization
    """
    # Make sure user handler modules are loaded so registry has handlers
    import_handler_modules_from_env()
    # Resolve loader the same way as the producer sink
    backend = _load_backend_selected(backend_name)
    # Register webhook event handler
    registry = get_registry()

    async for msg in backend.consume(group=_TOPIC_NAME):
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
