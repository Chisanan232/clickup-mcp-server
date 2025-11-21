from __future__ import annotations

import pytest

from clickup_mcp.web_server.event.bootstrap import import_handler_modules_from_env


def test_import_handler_modules_none(monkeypatch: pytest.MonkeyPatch) -> None:
    # No env var set -> returns empty list
    monkeypatch.delenv("CLICKUP_WEBHOOK_HANDLER_MODULES", raising=False)
    assert import_handler_modules_from_env() == []


def test_import_handler_modules_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mods = [
        "clickup_mcp.web_server.event.handler.oop",
        "clickup_mcp.web_server.event.handler.decorators",
    ]
    monkeypatch.setenv("CLICKUP_WEBHOOK_HANDLER_MODULES", ", ".join(mods))

    imported = import_handler_modules_from_env()

    # Should return the module names in order
    assert imported == mods


def test_import_handler_modules_custom_env_and_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    env_name = "MY_CLICKUP_HANDLERS"
    mods = [
        "clickup_mcp.web_server.event.handler.oop",
        "clickup_mcp.web_server.event.handler.decorators",
    ]
    # Include extra spaces around commas and names to verify trimming
    monkeypatch.setenv(env_name, f"  {mods[0]} ,  {mods[1]}  ")

    imported = import_handler_modules_from_env(env_var=env_name)

    assert imported == mods


def test_import_handler_modules_invalid_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # Invalid module should bubble up ModuleNotFoundError (no swallow)
    monkeypatch.setenv("CLICKUP_WEBHOOK_HANDLER_MODULES", "no.such.module.path")

    with pytest.raises(ModuleNotFoundError):
        import_handler_modules_from_env()
