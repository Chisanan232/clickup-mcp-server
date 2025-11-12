"""Optional structured logging hooks for MCP tools.

Currently a placeholder to centralize logging decisions later.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("clickup_mcp.mcp_server.errors")


def log_tool_event(event: str, **kwargs) -> None:
    logger.debug("%s %s", event, kwargs)
