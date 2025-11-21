from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List

import pytest

from clickup_mcp.web_server.event.handler.registry import get_registry
from clickup_mcp.web_server.event.models import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)
from clickup_mcp.web_server.event.mq import (
    deserialize_event,
    run_clickup_webhook_consumer,
    serialize_event,
)
from clickup_mcp.web_server.event.sink import LocalEventSink, get_event_sink


@pytest.mark.asyncio
async def test_get_event_sink_local_and_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure local mode
    monkeypatch.setenv("QUEUE_BACKEND", "local")

    # Arrange handler recording
    calls: List[ClickUpWebhookEvent] = []

    async def handler(evt: ClickUpWebhookEvent) -> None:
        calls.append(evt)

    reg = get_registry()
    reg.clear()
    reg.register(ClickUpWebhookEventType.TASK_CREATED, handler)

    # Execute
    sink = get_event_sink()
    assert isinstance(sink, LocalEventSink)

    evt = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={"event": "taskCreated", "x": 1},
        raw={"event": "taskCreated", "x": 1},
        headers={},
        received_at=__import__("datetime").datetime.utcnow(),
        delivery_id=None,
    )
    await sink.handle(evt)

    # Assert
    assert len(calls) == 1
    assert calls[0].type == ClickUpWebhookEventType.TASK_CREATED


class _FakeBackend:
    def __init__(self) -> None:
        self.published: List[Dict[str, Any]] = []
        self._consume_seed: List[Dict[str, Any]] = []

    def seed(self, payload: Dict[str, Any]) -> None:
        self._consume_seed.append(payload)

    async def publish(self, *, topic: str, key: str, payload: Dict[str, Any]) -> None:
        self.published.append({"topic": topic, "key": key, "payload": payload})

    async def consume(self, *, topic: str) -> AsyncGenerator[Dict[str, Any], None]:
        for v in list(self._consume_seed):
            yield v


@pytest.mark.asyncio
async def test_queue_sink_produces_and_consumer_dispatches(monkeypatch: pytest.MonkeyPatch) -> None:
    # Build a fake abe backend and patch loader used by mq module
    import clickup_mcp.web_server.event.mq as mq

    fake_backend = _FakeBackend()

    # Ensure module-level backend is reset and loader returns our fake backend
    monkeypatch.setenv("QUEUE_BACKEND", "kafka")
    monkeypatch.setattr(mq, "_queue_backend", None, raising=False)
    monkeypatch.setattr(mq, "load_backend", lambda: fake_backend, raising=True)

    # Register a handler to observe consumer dispatch
    received: List[ClickUpWebhookEventType] = []

    async def handler(evt: ClickUpWebhookEvent) -> None:
        received.append(evt.type)

    reg = get_registry()
    reg.clear()
    reg.register(ClickUpWebhookEventType.TASK_UPDATED, handler)

    # Create event and call queue sink
    from clickup_mcp.web_server.event.sink import (
        get_event_sink,  # re-import to pick env
    )

    event = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_UPDATED,
        body={"event": "taskUpdated", "y": 2},
        raw={"event": "taskUpdated", "y": 2},
        headers={},
        received_at=__import__("datetime").datetime.utcnow(),
        delivery_id="d1",
    )

    sink = get_event_sink()

    # Publish
    await sink.handle(event)

    # Assert published payload
    assert len(fake_backend.published) == 1
    published = fake_backend.published[0]
    assert published["topic"] == "clickup.webhooks"
    assert published["key"] == "d1"
    assert published["payload"] == serialize_event(event)

    # Seed consumer with the published payload and run consumer once
    fake_backend.seed(published["payload"])

    await run_clickup_webhook_consumer(backend_name="kafka")

    # Handler should have been called
    assert received == [ClickUpWebhookEventType.TASK_UPDATED]


def test_serialize_deserialize_roundtrip() -> None:
    from datetime import datetime

    original = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.LIST_UPDATED,
        body={"event": "listUpdated", "z": 3},
        raw={"event": "listUpdated", "z": 3},
        headers={"h": "1"},
        received_at=datetime.utcnow(),
        delivery_id="abc",
    )

    data = serialize_event(original)
    restored = deserialize_event(data)

    assert restored.type == original.type
    assert restored.body == original.body
    assert restored.headers == original.headers
    # ISO timestamp reconstructs; allow small delta if needed (string equality is fine here)
    assert restored.delivery_id == original.delivery_id
