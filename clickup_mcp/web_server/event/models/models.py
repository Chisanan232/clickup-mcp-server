from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

from .enums import ClickUpWebhookEventType


@dataclass
class ClickUpWebhookEvent:
    """
    Normalized representation of an incoming ClickUp webhook event.

    Handlers (both decorator-based and OOP-based) should receive this type.
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
    Reserved for future use (e.g., MQ producer, logger, config, tracing).

    For now, keep it simple. You can design it as a generic container for extras.
    """

    extras: Dict[str, Any] = field(default_factory=dict)
