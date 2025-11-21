from __future__ import annotations

import importlib
import os
from typing import List


def import_handler_modules_from_env(env_var: str = "CLICKUP_WEBHOOK_HANDLER_MODULES") -> List[str]:
    """Import handler modules declared in env var (comma-separated module paths).

    Returns the list of successfully imported module names.
    """
    modules_str = os.getenv(env_var, "").strip()
    imported: List[str] = []
    if not modules_str:
        return imported
    for name in [m.strip() for m in modules_str.split(",") if m.strip()]:
        importlib.import_module(name)
        imported.append(name)
    return imported
