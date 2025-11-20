from __future__ import annotations

import json
from pathlib import Path

import pytest

from clickup_mcp.web_server.event.models import ClickUpWebhookEventType
from clickup_mcp.web_server.event.models.dto import ClickUpWebhookRequest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "clickup_webhooks"


@pytest.mark.parametrize(
    ("fixture_name", "expected_type"),
    [
        ("taskCreated_full.json", ClickUpWebhookEventType.TASK_CREATED),
    ],
)
def test_clickup_webhook_request_parses_official_payloads(
    fixture_name: str, expected_type: ClickUpWebhookEventType
) -> None:
    raw = json.loads((FIXTURE_DIR / fixture_name).read_text())
    dto = ClickUpWebhookRequest.model_validate(raw)

    assert dto.event == expected_type
    # webhook_id optional, but present in our fixture
    assert dto.webhook_id == raw.get("webhook_id")

    # basic shape checks
    if "task_id" in raw:
        assert dto.task_id == raw["task_id"]

    # history_items are preserved when present
    if "history_items" in raw:
        assert dto.history_items is not None
        assert len(dto.history_items) >= 1
        first = dto.history_items[0]
        assert first.id
        assert first.date
