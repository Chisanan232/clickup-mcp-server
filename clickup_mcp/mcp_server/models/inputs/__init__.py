"""Input schemas for MCP tools (ClickUp server).

This package exposes Pydantic models that define the input payloads for the
MCP tools under `clickup_mcp.mcp_server.*` (e.g., space, folder, list, task).

Prefer importing specific input models from their submodules to keep import
paths stable. Example:

    from clickup_mcp.mcp_server.models.inputs.space import SpaceGetInput

"""

