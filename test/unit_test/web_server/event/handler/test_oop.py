from datetime import datetime

import pytest

from clickup_mcp.web_server.event import (
    BaseClickUpWebhookHandler,
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)
from clickup_mcp.web_server.event.handler import get_registry


class MyHandler(BaseClickUpWebhookHandler):
    def __init__(self, seen: list[str]) -> None:
        self.seen = seen
        super().__init__()

    async def on_task_status_updated(self, event: ClickUpWebhookEvent) -> None:
        self.seen.append(f"status:{event.type}")

    async def on_task_created(self, event: ClickUpWebhookEvent) -> None:
        self.seen.append(f"created:{event.type}")


@pytest.mark.asyncio
async def test_oop_base_registers_overrides_and_dispatches():
    seen: list[str] = []
    _ = MyHandler(seen)

    ev_status = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_STATUS_UPDATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )
    ev_created = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )

    reg = get_registry()
    await reg.dispatch(ev_status)
    await reg.dispatch(ev_created)

    assert seen == [
        f"status:{ClickUpWebhookEventType.TASK_STATUS_UPDATED}",
        f"created:{ClickUpWebhookEventType.TASK_CREATED}",
    ]


@pytest.mark.asyncio
async def test_oop_dunder_call_is_invoked_when_instance_is_registered():
    seen: list[str] = []

    class CallHandler(BaseClickUpWebhookHandler):
        def __init__(self, seen_ref: list[str]) -> None:
            self.seen = seen_ref
            super().__init__()

        async def on_task_created(self, event: ClickUpWebhookEvent) -> None:
            self.seen.append(f"__call__:{event.type}")

    h = CallHandler(seen)
    # Clear the auto-registered per-event handlers and register the instance itself
    reg = get_registry()
    reg.clear()
    reg.register(ClickUpWebhookEventType.TASK_CREATED, h)  # type: ignore[arg-type]

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )

    await reg.dispatch(ev)

    assert seen == [f"__call__:{ClickUpWebhookEventType.TASK_CREATED}"]
