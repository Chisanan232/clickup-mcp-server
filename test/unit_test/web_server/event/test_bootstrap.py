from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from clickup_mcp.config import get_settings
from clickup_mcp.web_server.event.bootstrap import import_handler_modules_from_env


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear settings cache before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_import_handler_modules_none(monkeypatch: pytest.MonkeyPatch) -> None:
    # No env var set -> returns empty list
    monkeypatch.delenv("CLICKUP_WEBHOOK_HANDLER_MODULES", raising=False)
    
    # We must mock get_settings or ensure environment is clean
    # Since monkeypatch modifies os.environ, get_settings() should pick it up if cache is cleared
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


def test_import_handler_modules_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    mods = [
        "clickup_mcp.web_server.event.handler.oop",
        "clickup_mcp.web_server.event.handler.decorators",
    ]
    # Include extra spaces around commas and names to verify trimming
    monkeypatch.setenv("CLICKUP_WEBHOOK_HANDLER_MODULES", f"  {mods[0]} ,  {mods[1]}  ")

    imported = import_handler_modules_from_env()

    assert imported == mods


def test_import_handler_modules_invalid_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # Invalid module should bubble up ModuleNotFoundError (no swallow)
    monkeypatch.setenv("CLICKUP_WEBHOOK_HANDLER_MODULES", "no.such.module.path")

    with pytest.raises(ModuleNotFoundError):
        import_handler_modules_from_env()
