from __future__ import annotations

"""
Pydantic DTOs for ClickUp webhook requests.

Design:
- These models validate and normalize raw webhook JSON payloads into
  strongly-typed structures used by the webhook ingress.

Usage Example:
    from clickup_mcp.web_server.event.models.dto import ClickUpWebhookRequest

    req = ClickUpWebhookRequest(event="taskUpdated", task_id="t1", history_items=[])
    assert req.event.value == "taskUpdated"
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .enums import ClickUpWebhookEventType


class ClickUpWebhookHistoryUser(BaseModel):
    """User in a webhook history item.

    Attributes:
        id: ClickUp user ID (string or integer)
        username: Optional username
    """

    id: str | int
    username: Optional[str] = None


class ClickUpWebhookHistoryItem(BaseModel):
    """Change record describing what changed in an entity.

    Attributes:
        id: History item ID
        date: Change date in ClickUp format (string)
        field: Optional field name changed
        type: Optional type code
        user: Optional user who made the change
        before: Previous value (any type)
        after: New value (any type)
    """

    id: str
    date: str
    field: Optional[str] = None
    type: Optional[int] = None
    user: Optional[ClickUpWebhookHistoryUser] = None
    before: Any = None
    after: Any = None


class ClickUpWebhookRequest(BaseModel):
    """Top-level ClickUp webhook body.

    Attributes:
        event: Webhook event type
        webhook_id: Optional webhook configuration ID
        task_id: ID of affected task (if applicable)
        list_id: ID of affected list (if applicable)
        folder_id: ID of affected folder (if applicable)
        space_id: ID of affected space (if applicable)
        goal_id: ID of affected goal (if applicable)
        key_result_id: ID of affected key result (if applicable)
        history_items: Optional list of change records

    Examples:
        ClickUpWebhookRequest(event="taskUpdated", task_id="t1")
    """

    event: ClickUpWebhookEventType
    webhook_id: Optional[str] = None

    task_id: Optional[str] = None
    list_id: Optional[str] = None
    folder_id: Optional[str] = None
    space_id: Optional[str] = None
    goal_id: Optional[str] = None
    key_result_id: Optional[str] = Field(default=None, alias="key_result_id")

    history_items: Optional[List[ClickUpWebhookHistoryItem]] = None

    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }
