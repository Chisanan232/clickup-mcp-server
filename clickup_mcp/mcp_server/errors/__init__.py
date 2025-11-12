"""Centralized error system for MCP tools.

Exports:
- IssueCode: strict enum of canonical error codes
- ToolIssue, ToolResponse[T]: response envelope models
- map_exception: exception → ToolIssue mapper
- handle_tool_errors: decorator to wrap MCP tools
"""

from .codes import IssueCode
from .handler import handle_tool_errors
from .mapping import map_exception
from .models import ToolIssue, ToolResponse

__all__ = [
    "IssueCode",
    "ToolIssue",
    "ToolResponse",
    "map_exception",
    "handle_tool_errors",
]
