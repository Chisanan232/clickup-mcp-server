from datetime import datetime

from fastapi import APIRouter, HTTPException, Request

from .models import ClickUpWebhookEvent, ClickUpWebhookEventType
from .models.dto import ClickUpWebhookRequest
from .sink import get_event_sink


router = APIRouter(tags=["webhooks"], prefix="/webhook")


@router.post("/clickup")
async def clickup_webhook(dto: ClickUpWebhookRequest, request: Request):
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
