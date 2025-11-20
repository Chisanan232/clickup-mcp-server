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
        # Task events
        ("taskCreated_full.json", ClickUpWebhookEventType.TASK_CREATED),
        ("taskCreated.json", ClickUpWebhookEventType.TASK_CREATED),
        ("taskUpdated.json", ClickUpWebhookEventType.TASK_UPDATED),
        ("taskDeleted.json", ClickUpWebhookEventType.TASK_DELETED),
        ("taskStatusUpdated.json", ClickUpWebhookEventType.TASK_STATUS_UPDATED),
        ("taskAssigneeUpdated.json", ClickUpWebhookEventType.TASK_ASSIGNEE_UPDATED),
        ("taskDueDateUpdated.json", ClickUpWebhookEventType.TASK_DUE_DATE_UPDATED),
        ("taskTagUpdated.json", ClickUpWebhookEventType.TASK_TAG_UPDATED),
        ("taskMoved.json", ClickUpWebhookEventType.TASK_MOVED),
        ("taskCommentPosted.json", ClickUpWebhookEventType.TASK_COMMENT_POSTED),
        ("taskCommentUpdated.json", ClickUpWebhookEventType.TASK_COMMENT_UPDATED),
        ("taskTimeEstimateUpdated.json", ClickUpWebhookEventType.TASK_TIME_ESTIMATE_UPDATED),
        ("taskTimeTrackedUpdated.json", ClickUpWebhookEventType.TASK_TIME_TRACKED_UPDATED),
        ("taskPriorityUpdated.json", ClickUpWebhookEventType.TASK_PRIORITY_UPDATED),

        # List events (multiple variants for some)
        ("listCreated.json", ClickUpWebhookEventType.LIST_CREATED),
        ("listCreated_2.json", ClickUpWebhookEventType.LIST_CREATED),
        ("listUpdated.json", ClickUpWebhookEventType.LIST_UPDATED),
        ("listDeleted.json", ClickUpWebhookEventType.LIST_DELETED),
        ("listDeleted_2.json", ClickUpWebhookEventType.LIST_DELETED),
        ("listDeleted_3.json", ClickUpWebhookEventType.LIST_DELETED),

        # Folder events
        ("folderCreated.json", ClickUpWebhookEventType.FOLDER_CREATED),
        ("folderUpdated.json", ClickUpWebhookEventType.FOLDER_UPDATED),
        ("folderDeleted.json", ClickUpWebhookEventType.FOLDER_DELETED),

        # Space events (with multiple variants for updated)
        ("spaceCreated.json", ClickUpWebhookEventType.SPACE_CREATED),
        ("spaceUpdated.json", ClickUpWebhookEventType.SPACE_UPDATED),
        ("spaceUpdated_2.json", ClickUpWebhookEventType.SPACE_UPDATED),
        ("spaceDeleted.json", ClickUpWebhookEventType.SPACE_DELETED),

        # Goal events
        ("goalCreated.json", ClickUpWebhookEventType.GOAL_CREATED),
        ("goalUpdated.json", ClickUpWebhookEventType.GOAL_UPDATED),
        ("goalDeleted.json", ClickUpWebhookEventType.GOAL_DELETED),

        # Key Result events
        ("keyResultCreated.json", ClickUpWebhookEventType.KEY_RESULT_CREATED),
        ("keyResultUpdated.json", ClickUpWebhookEventType.KEY_RESULT_UPDATED),
        ("keyResultDeleted.json", ClickUpWebhookEventType.KEY_RESULT_DELETED),
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
