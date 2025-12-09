"""
Normalized event models used by the webhook ingress, sinks, and handlers.

Design:
- `ClickUpWebhookEvent` is a simple dataclass representing a normalized ClickUp
  webhook. It is the primary payload delivered to in-process handlers and MQ sinks.
- `ClickUpWebhookContext` is an auxiliary container for optional metadata and
  cross-cutting concerns (e.g., logger, config, tracing). Currently minimal.

Relationship to DTOs:
- Incoming HTTP JSON is validated by Pydantic DTOs in `dto.py` and then converted
  to this dataclass for internal processing and transport.

Examples:
    # Constructing in the webhook route
    from datetime import datetime
    from clickup_mcp.web_server.event.models import ClickUpWebhookEvent, ClickUpWebhookEventType

    event = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_UPDATED,
        body={"event": "taskUpdated", "task_id": "t1"},
        raw={"event": "taskUpdated", "task_id": "t1"},
        headers={"X-Request-Id": "req-123"},
        received_at=datetime.utcnow(),
        delivery_id="req-123",
    )

    # Accessing in a handler
    async def on_task_updated(evt: ClickUpWebhookEvent) -> None:
        print(evt.type.value, evt.body.get("task_id"))
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

from .enums import ClickUpWebhookEventType


@dataclass
class ClickUpWebhookEvent:
    """
    Normalized representation of a ClickUp webhook event.

    Attributes:
        type: Event type enum parsed from the webhook body (e.g., taskUpdated)
        body: Canonical dict used by runtime components and handlers
        raw: Original request body (may equal `body` if no transformation is needed)
        headers: Request headers captured at ingress
        received_at: UTC timestamp when the server received the webhook
        delivery_id: Optional delivery-request identifier (e.g., X-Request-Id)

    Notes:
    - Dataclass is intentionally lightweight for fast serialization to MQ sinks.
    - See `event.mq.serialize_event` for wire representation.

    Examples:
        ClickUpWebhookEvent(
            type=ClickUpWebhookEventType.TASK_CREATED,
            body={"event": "taskCreated", "task_id": "t2"},
            raw={"event": "taskCreated", "task_id": "t2"},
            headers={},
            received_at=datetime.utcnow(),
        )
    """

    type: ClickUpWebhookEventType
    body: Dict[str, Any]
    raw: Dict[str, Any]
    headers: Mapping[str, str]
    received_at: datetime
    delivery_id: Optional[str] = None


@dataclass
class ClickUpWebhookContext:
    """
    Optional context passed alongside events.

    Attributes:
        extras: Arbitrary metadata map for cross-cutting concerns (e.g., logger,
                configuration, tracing IDs)

    Examples:
        ctx = ClickUpWebhookContext(extras={"logger": my_logger, "trace_id": "abc"})
    """

    extras: Dict[str, Any] = field(default_factory=dict)
