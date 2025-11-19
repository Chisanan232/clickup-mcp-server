"""Output schemas for MCP tools (ClickUp server).

This package defines the response models (Pydantic) returned by MCP tools
under `clickup_mcp.mcp_server.*`. These models are wrapped by the
`ToolResponse[T]` envelope at runtime via `handle_tool_errors`.

Prefer importing specific output models from their submodules. Example:

    from clickup_mcp.mcp_server.models.outputs.space import SpaceResult

"""
