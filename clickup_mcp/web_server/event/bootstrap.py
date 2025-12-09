from __future__ import annotations

"""
Bootstrap utilities for ClickUp webhook handler discovery and registration.

Design:
- Handlers can be registered via import-time side effects from user-defined modules.
- This module provides a helper that imports those modules listed in an env var,
  enabling declarative registration without modifying server code.

Environment:
- `CLICKUP_WEBHOOK_HANDLER_MODULES` (default key): Comma-separated list of Python
  module paths to import. Each module should register handlers in its import body.

Examples:
    # .env
    CLICKUP_WEBHOOK_HANDLER_MODULES=acme.handlers.clickup,another_pkg.webhooks

    # Python
    from clickup_mcp.web_server.event.bootstrap import import_handler_modules_from_env
    imported = import_handler_modules_from_env()
    assert "acme.handlers.clickup" in imported
"""

import importlib
import os
from typing import List


def import_handler_modules_from_env(env_var: str = "CLICKUP_WEBHOOK_HANDLER_MODULES") -> List[str]:
    """
    Import handler modules declared in an environment variable.

    Behavior:
    - Reads `env_var` from the environment; if empty, returns an empty list.
    - Splits by comma, strips whitespace, ignores empty entries.
    - Imports each module using `importlib.import_module`.
    - Returns the list of successfully imported module names.

    Args:
        env_var: Environment variable name holding CSV of module paths.

    Returns:
        List of module names that were imported.

    Examples:
        # With env CLICKUP_WEBHOOK_HANDLER_MODULES set
        import os
        os.environ["CLICKUP_WEBHOOK_HANDLER_MODULES"] = "acme.handlers.clickup,foo.bar"
        names = import_handler_modules_from_env()
        assert names == ["acme.handlers.clickup", "foo.bar"]
    """
    modules_str = os.getenv(env_var, "").strip()
    imported: List[str] = []
    if not modules_str:
        return imported
    for name in [m.strip() for m in modules_str.split(",") if m.strip()]:
        importlib.import_module(name)
        imported.append(name)
    return imported
