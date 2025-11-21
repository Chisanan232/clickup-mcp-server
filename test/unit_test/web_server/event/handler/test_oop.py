from datetime import datetime

import pytest

from clickup_mcp.web_server.event.handler import get_registry
from clickup_mcp.web_server.event import (
    BaseClickUpWebhookHandler,
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)


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
