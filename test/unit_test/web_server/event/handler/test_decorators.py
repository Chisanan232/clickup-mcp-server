from datetime import datetime

import pytest

from clickup_mcp.web_server.event.handler import clickup_event, get_registry
from clickup_mcp.web_server.event.models import (
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)


@pytest.mark.asyncio
async def test_decorator_enum_style_registers_and_runs():
    seen: list[int] = []

    @clickup_event(ClickUpWebhookEventType.TASK_STATUS_UPDATED)
    async def handle(ev: ClickUpWebhookEvent) -> None:
        seen.append(1)
        assert ev.type == ClickUpWebhookEventType.TASK_STATUS_UPDATED

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_STATUS_UPDATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )
    await get_registry().dispatch(ev)
    assert seen == [1]


@pytest.mark.asyncio
async def test_decorator_attr_style_registers_and_runs():
    seen: list[int] = []

    @clickup_event.task_status_updated
    async def handle(ev: ClickUpWebhookEvent) -> None:
        seen.append(2)

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_STATUS_UPDATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )
    await get_registry().dispatch(ev)
    assert seen == [2]


@pytest.mark.asyncio
async def test_decorator_wraps_sync_handler():
    seen: list[int] = []

    @clickup_event.task_created
    def handle_sync(_: ClickUpWebhookEvent) -> None:
        seen.append(3)

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )
    await get_registry().dispatch(ev)
    assert seen == [3]


def test_decorator_unknown_attribute_raises():
    with pytest.raises(AttributeError):
        getattr(clickup_event, "unknown_event_alias")


@pytest.mark.parametrize("event_type", ClickUpWebhookEventType)
def test_clickup_event_has_attribute_for_each_enum_member(event_type: ClickUpWebhookEventType):
    attr_name = event_type.name.lower()
    assert hasattr(clickup_event, attr_name), f"Missing decorator attribute: {attr_name}"


def test_clickup_event_prefixed_attributes_map_to_enum_members():
    prefixes = ("task_", "list_", "folder_", "space_", "goal_", "key_")
    enum_names = {et.name for et in ClickUpWebhookEventType}

    # Iterate through all attributes exposed by the decorator helper
    for name in dir(clickup_event):
        if any(name.startswith(p) for p in prefixes):
            enum_name = name.upper()
            assert (
                enum_name in enum_names
            ), f"Decorator attribute '{name}' does not map to a ClickUpWebhookEventType member"
