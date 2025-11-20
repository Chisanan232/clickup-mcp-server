from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .enums import ClickUpWebhookEventType


class ClickUpWebhookHistoryUser(BaseModel):
    id: str | int
    username: Optional[str] = None


class ClickUpWebhookHistoryItem(BaseModel):
    id: str
    date: str
    field: Optional[str] = None
    type: Optional[int] = None
    user: Optional[ClickUpWebhookHistoryUser] = None
    before: Any = None
    after: Any = None


class ClickUpWebhookRequest(BaseModel):
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
