from datetime import datetime

import pytest

from clickup_mcp.web_server.event import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
    clickup_event,
    get_registry,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", list(ClickUpWebhookEventType))
async def test_enum_decorator_async_for_all_event_types(event_type: ClickUpWebhookEventType) -> None:
    reg = get_registry()
    reg.clear()
    called: dict[str, ClickUpWebhookEvent] = {}

    @clickup_event(event_type)
    async def handle(ev: ClickUpWebhookEvent) -> None:
        called["ev"] = ev

    ev = ClickUpWebhookEvent(
        type=event_type,
        body={"event": event_type.value},
        raw={"event": event_type.value},
        headers={},
        received_at=datetime.utcnow(),
    )
    await reg.dispatch(ev)

    assert called.get("ev") is not None and called["ev"].type == event_type


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", list(ClickUpWebhookEventType))
async def test_enum_decorator_sync_for_all_event_types(event_type: ClickUpWebhookEventType) -> None:
    reg = get_registry()
    reg.clear()
    called: dict[str, ClickUpWebhookEvent] = {}

    @clickup_event(event_type)
    def handle(ev: ClickUpWebhookEvent) -> None:
        called["ev"] = ev

    ev = ClickUpWebhookEvent(
        type=event_type,
        body={"event": event_type.value},
        raw={"event": event_type.value},
        headers={},
        received_at=datetime.utcnow(),
    )
    await reg.dispatch(ev)

    assert called.get("ev") is not None and called["ev"].type == event_type
