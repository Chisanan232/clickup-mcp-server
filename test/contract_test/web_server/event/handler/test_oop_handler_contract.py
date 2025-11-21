from datetime import datetime

import pytest

from clickup_mcp.web_server.event import (
    BaseClickUpWebhookHandler,
    ClickUpWebhookEvent,
    ClickUpWebhookEventType,
    get_registry,
)


class RecordingHandler(BaseClickUpWebhookHandler):
    def __init__(self) -> None:
        self.calls: list[tuple[ClickUpWebhookEventType, ClickUpWebhookEvent]] = []
        super().__init__()


# Dynamically attach on_<event> methods for all enum members before instantiation
def _attach_methods() -> None:
    for et in ClickUpWebhookEventType:
        method_name = f"on_{et.name.lower()}"

        async def _handler(
            self: RecordingHandler, event: ClickUpWebhookEvent, _et: ClickUpWebhookEventType = et
        ) -> None:
            self.calls.append((_et, event))

        setattr(RecordingHandler, method_name, _handler)


_attach_methods()


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", list(ClickUpWebhookEventType))
async def test_oop_handler_contract_for_all_event_types(event_type: ClickUpWebhookEventType) -> None:
    reg = get_registry()
    reg.clear()
    handler = RecordingHandler()

    evt = ClickUpWebhookEvent(
        type=event_type,
        body={"event": event_type.value},
        raw={"event": event_type.value},
        headers={},
        received_at=datetime.utcnow(),
    )

    await reg.dispatch(evt)

    assert (event_type, evt) in handler.calls
