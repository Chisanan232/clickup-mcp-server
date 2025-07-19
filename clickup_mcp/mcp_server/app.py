from typing import Optional

from mcp.server import FastMCP


def create_mcp_server() -> FastMCP:
    """
    Create and configure the MCP server with the specified environment file.
    
    Returns:
        Configured FastMCP server instance
    """
    # Create a new FastMCP instance
    return FastMCP()


# Create a default MCP server instance for backward compatibility
mcp = create_mcp_server()
