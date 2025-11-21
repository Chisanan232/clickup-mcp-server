from datetime import datetime
import inspect

import pytest

from clickup_mcp.web_server.event import (
    BaseClickUpWebhookHandler,
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
)
from clickup_mcp.web_server.event.handler import get_registry


class MyHandler(BaseClickUpWebhookHandler):
    def __init__(self, seen: list[str]) -> None:
        self.seen = seen
        super().__init__()

    async def on_task_status_updated(self, event: ClickUpWebhookEvent) -> None:
        self.seen.append(f"status:{event.type}")

    async def on_task_created(self, event: ClickUpWebhookEvent) -> None:
        self.seen.append(f"created:{event.type}")


@pytest.mark.asyncio
async def test_oop_base_registers_overrides_and_dispatches():
    seen: list[str] = []
    _ = MyHandler(seen)

    ev_status = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_STATUS_UPDATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )
    ev_created = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )

    reg = get_registry()
    await reg.dispatch(ev_status)
    await reg.dispatch(ev_created)

    assert seen == [
        f"status:{ClickUpWebhookEventType.TASK_STATUS_UPDATED}",
        f"created:{ClickUpWebhookEventType.TASK_CREATED}",
    ]


@pytest.mark.asyncio
async def test_oop_dunder_call_is_invoked_when_instance_is_registered():
    seen: list[str] = []

    class CallHandler(BaseClickUpWebhookHandler):
        def __init__(self, seen_ref: list[str]) -> None:
            self.seen = seen_ref
            super().__init__()

        async def on_task_created(self, event: ClickUpWebhookEvent) -> None:
            self.seen.append(f"__call__:{event.type}")

    h = CallHandler(seen)
    # Clear the auto-registered per-event handlers and register the instance itself
    reg = get_registry()
    reg.clear()
    reg.register(ClickUpWebhookEventType.TASK_CREATED, h)

    ev = ClickUpWebhookEvent(
        type=ClickUpWebhookEventType.TASK_CREATED,
        body={},
        raw={},
        headers={},
        received_at=datetime.utcnow(),
    )

    await reg.dispatch(ev)

    assert seen == [f"__call__:{ClickUpWebhookEventType.TASK_CREATED}"]


def test_oop_on_prefixed_methods_map_to_enum_and_resolve():
    prefixes = ("on_task_", "on_list_", "on_folder_", "on_space_", "on_goal_", "on_key_result_")
    # Collect all on_* hook names from the base class
    hook_names: list[str] = []
    for name, member in inspect.getmembers(BaseClickUpWebhookHandler):
        if name.startswith("on_") and any(name.startswith(p) for p in prefixes) and inspect.isfunction(member):
            hook_names.append(name)

    # Ensure every hook corresponds to an enum member, and resolve_handler maps it back
    enum_names = {et.name for et in ClickUpWebhookEventType}
    derived_enum_names = set()

    base = BaseClickUpWebhookHandler()
    for hook in hook_names:
        enum_name = hook[len("on_"):].upper()
        assert (
            enum_name in enum_names
        ), f"Hook '{hook}' does not map to ClickUpWebhookEventType member '{enum_name}'"

        et = ClickUpWebhookEventType[enum_name]
        resolved = base._resolve_handler(et)
        assert resolved is not None and resolved.__name__ == hook
        derived_enum_names.add(enum_name)

    # The set of hooks should exactly cover the enum members
    assert derived_enum_names == enum_names


def test_oop_every_enum_event_resolves_to_corresponding_on_method():
    base = BaseClickUpWebhookHandler()
    for et in ClickUpWebhookEventType:
        expected_name = f"on_{et.name.lower()}"
        resolved = base._resolve_handler(et)
        assert resolved is not None, f"No handler resolved for {et}"
        assert resolved.__name__ == expected_name, (
            f"Resolved handler name mismatch for {et}: got {resolved.__name__}, expected {expected_name}"
        )
