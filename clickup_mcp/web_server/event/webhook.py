"""
ClickUp webhook ingress endpoints.

Design:
- Exposes FastAPI routes under prefix `/webhook` for receiving ClickUp webhooks.
- Validates payloads with Pydantic DTOs and normalizes to `ClickUpWebhookEvent`.
- Dispatches events to an `EventSink` abstraction selected by `QUEUE_BACKEND` env var:
  - `local` (default): direct in-process dispatch via handler registry
  - others: enqueues to MQ via `QueueEventSink` for async processing

Usage (curl):
    curl -X POST http://localhost:8000/webhook/clickup \
      -H 'Content-Type: application/json' \
      -d '{"event":"taskUpdated","task_id":"task_123","history_items":[]}'

Environment:
- `QUEUE_BACKEND`: "local" (default) for direct dispatch, otherwise selects MQ backend
"""

from datetime import datetime

from fastapi import APIRouter, Request

from .models import ClickUpWebhookEvent
from .models.dto import ClickUpWebhookRequest
from .sink import get_event_sink

router = APIRouter(tags=["webhooks"], prefix="/webhook")


@router.post("/clickup")
async def clickup_webhook(dto: ClickUpWebhookRequest, request: Request):
    """
    Ingest a ClickUp webhook event and route it to the event sink.

    Flow:
    - Validate request body into `ClickUpWebhookRequest` (Pydantic)
    - Build normalized `ClickUpWebhookEvent` with headers and timestamp
    - Resolve sink via `get_event_sink()` and forward for handling

    Args:
        dto: Validated ClickUp webhook payload
        request: FastAPI request (used to capture headers)

    Returns:
        JSON object `{ "ok": true }` on acceptance

    Examples:
        # Python - unit test style
        from fastapi.testclient import TestClient
        from clickup_mcp.web_server.app import WebServerFactory

        app = WebServerFactory.create()
        client = TestClient(app)
        resp = client.post('/webhook/clickup', json={"event":"taskUpdated","task_id":"t1"})
        assert resp.status_code == 200 and resp.json()["ok"] is True
    """
    headers = dict(request.headers)

    # Construct domain event from validated DTO
    body = dto.model_dump(mode="python")
    event = ClickUpWebhookEvent(
        type=dto.event,
        body=body,
        raw=body,
        headers=headers,
        received_at=datetime.utcnow(),
        delivery_id=headers.get("X-Request-Id"),
    )

    sink = get_event_sink()
    await sink.handle(event)

    return {"ok": True}
