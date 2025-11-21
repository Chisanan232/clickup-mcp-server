from __future__ import annotations

import sys
from typing import List

import pytest

import clickup_mcp.web_server.event.mq as mq


def test_queue_event_sink_ensure_backend_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[str] = []

    class _DummyBackend:
        pass

    def _fake_loader(name: str) -> _DummyBackend:
        calls.append(name)
        return _DummyBackend()

    # Ensure module-level global is not used by _ensure_backend path
    monkeypatch.setattr(mq, "_load_backend_selected", _fake_loader, raising=True)

    sink = mq.QueueEventSink(backend_name="kafka")

    # First call should resolve via loader
    b1 = sink._ensure_backend()
    assert isinstance(b1, _DummyBackend)
    assert calls == ["kafka"]

    # Second call should return cached instance without calling loader again
    b2 = sink._ensure_backend()
    assert b2 is b1
    assert calls == ["kafka"]


@pytest.mark.parametrize(
    "argv,env_backend,expected",
    [
        (["prog", "--queue-backend", "kafka"], None, "kafka"),
        (["prog"], "rabbitmq", "rabbitmq"),
    ],
)
def test_main_parses_queue_backend_and_invokes_runner(
    monkeypatch: pytest.MonkeyPatch, argv: list[str], env_backend: str | None, expected: str
) -> None:
    # Capture the backend_name passed into the runner
    seen: List[str] = []

    async def fake_runner(*, backend_name: str) -> None:
        seen.append(backend_name)

    # Patch runner
    monkeypatch.setattr(mq, "run_clickup_webhook_consumer", fake_runner, raising=True)

    # Prepare argv and env
    monkeypatch.setattr(sys, "argv", argv)
    if env_backend is not None:
        monkeypatch.setenv("QUEUE_BACKEND", env_backend)
    else:
        monkeypatch.delenv("QUEUE_BACKEND", raising=False)

    # Call main (will run the fake async function)
    mq.main()

    assert seen == [expected]
