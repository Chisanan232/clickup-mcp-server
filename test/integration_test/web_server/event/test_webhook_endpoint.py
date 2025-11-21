from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from clickup_mcp.web_server.event.handler import get_registry
from clickup_mcp.web_server.event.models import ClickUpWebhookEvent, ClickUpWebhookEventType
from clickup_mcp.web_server.event.webhook import router


def test_webhook_endpoint_dispatches_handlers():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # register test handler
    calls: list[ClickUpWebhookEvent] = []

    async def handler(ev: ClickUpWebhookEvent) -> None:
        calls.append(ev)

    reg = get_registry()
    reg.clear()
    reg.register(ClickUpWebhookEventType.TASK_STATUS_UPDATED, handler)

    resp = client.post(
        "/webhook/clickup",
        json={"event": "taskStatusUpdated", "data": {"foo": "bar"}},
        headers={"X-Request-Id": "req-1"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    assert len(calls) == 1
    event = calls[0]
    assert event.type == ClickUpWebhookEventType.TASK_STATUS_UPDATED
    assert event.body["data"]["foo"] == "bar"
