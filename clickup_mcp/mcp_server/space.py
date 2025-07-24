"""
MCP functions for ClickUp Spaces.

This module provides MCP functions for interacting with ClickUp Spaces.
These functions follow the FastMCP pattern for easy integration into MCP servers.
"""

from clickup_mcp.client import ClickUpAPIClientFactory

from .app import mcp


@mcp.tool(name="get_space", title="Get ClickUp Space", description="Get a ClickUp space by its ID.")
async def get_space(space_id: str = "") -> dict[str, object] | None:
    """
    Get a ClickUp space by its ID.

    This function retrieves a space from ClickUp by its space ID. It returns
    the space domain model if found, or None if the space does not exist.

    Args:
        space_id: The ID of the space to retrieve.

    Returns:
        The ClickUpSpace domain model as a dictionary if found, or None if the space does not exist.

    Raises:
        ValueError: If the API token is not found or if the space ID is empty.
    """
    # Validate inputs
    if not space_id:
        raise ValueError("Space ID is required")

    client = ClickUpAPIClientFactory.get()

    try:
        # Get the space using the client
        async with client:
            space = await client.space.get(space_id)

        # Convert to dict for proper serialization
        if space:
            return space.model_dump()
        return None
    except Exception as e:
        raise ValueError(f"Error retrieving space: {str(e)}")
