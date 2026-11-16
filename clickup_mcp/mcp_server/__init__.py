"""ClickUp MCP functions package.

Design:
- Import-time registration: importing this package loads tool modules so their
  `@mcp.tool` decorators execute and register tools with the global `FastMCP` instance.
- Import order matters: we ensure the MCP app is created before importing tools
  so registration attaches to the correct instance.

Usage Examples:
    # Importing this package registers all tools on the default MCP instance
    import clickup_mcp.mcp_server as mcp_pkg

    # Access the default MCP instance (created in app.py at import time)
    from clickup_mcp.mcp_server.app import mcp

    # Optional: list registered tools (example; exact API may vary)
    # print(mcp.list_tools())
"""

# Import tool modules to register tools
from . import (  # noqa: F401
    analytics,
    bottleneck,
    folder,
    goal,
    insights,
    key_result,
    list,
    reporting,
    space,
    task,
    team,
    time,
    workflow,
    workspace,
)

# Ensure app is created before importing tool modules
from .app import mcp  # noqa: F401

__all__ = [
    # legacy
    "mcp",
]
