from datetime import datetime
from typing import Any

import pytest

from clickup_mcp.web_server.event.models import ClickUpWebhookEvent, ClickUpWebhookEventType
from clickup_mcp.web_server.event.handler import get_registry


@pytest.mark.asyncio
async def test_registry_register_and_dispatch_single_handler():
    calls: list[dict[str, Any]] = []

    async def h(ev: ClickUpWebhookEvent) -> None:
        calls.append({"type": ev.type, "body": ev.body})

    reg = get_registry()
    reg.register(ClickUpWebhookEventType.TASK_CREATED, h)

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={"hello": "world"},
        raw={"hello": "world"},
        headers={},
        received_at=datetime.utcnow(),
    )
    await reg.dispatch(ev)

    assert len(calls) == 1
    assert calls[0]["type"] == ClickUpWebhookEventType.TASK_CREATED
    assert calls[0]["body"]["hello"] == "world"


@pytest.mark.asyncio
async def test_registry_dispatch_calls_all_handlers_for_type():
    calls: list[int] = []

    async def h1(_: ClickUpWebhookEvent) -> None:
        calls.append(1)

    async def h2(_: ClickUpWebhookEvent) -> None:
        calls.append(2)

    reg = get_registry()
    reg.register(ClickUpWebhookEventType.TASK_DELETED, h1)
    reg.register(ClickUpWebhookEventType.TASK_DELETED, h2)

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_DELETED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )
    await reg.dispatch(ev)

    assert calls == [1, 2]
