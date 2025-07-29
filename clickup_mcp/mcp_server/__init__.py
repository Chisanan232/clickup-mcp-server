"""
ClickUp MCP functions.

This module exports all MCP functions provided by the clickup-mcp-server.
"""

from .space import get_space
from .team import get_authorized_teams

__all__ = ["get_space", "get_authorized_teams"]
