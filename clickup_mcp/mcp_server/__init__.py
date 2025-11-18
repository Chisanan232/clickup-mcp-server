"""ClickUp MCP functions package.

Import submodules so FastMCP tool decorators run at import time.
"""

# Import tool modules to register tools
from . import folder  # noqa: F401
from . import list  # noqa: F401
from . import space  # noqa: F401
from . import task  # noqa: F401
from . import team  # noqa: F401
from . import workspace  # noqa: F401

# Ensure app is created before importing tool modules
from .app import mcp  # noqa: F401

__all__ = [
    # legacy
    "mcp",
]
