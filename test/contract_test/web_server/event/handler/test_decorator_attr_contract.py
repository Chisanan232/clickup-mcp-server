from datetime import datetime

import pytest

from clickup_mcp.web_server.event import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
    clickup_event,
    get_registry,
)


def _snake(name: str) -> str:
    return name.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", list(ClickUpWebhookEventType))
async def test_attr_decorator_contract_for_all_event_types(event_type: ClickUpWebhookEventType) -> None:
    reg = get_registry()
    reg.clear()
    called: dict[str, ClickUpWebhookEvent] = {}

    attr_name = _snake(event_type.name)
    decorator = getattr(clickup_event, attr_name)

    @decorator
    async def handler(ev: ClickUpWebhookEvent) -> None:
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
