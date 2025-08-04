from mcp.server import FastMCP

from clickup_mcp._base import BaseServerFactory

_MCP_SERVER_INSTANCE: FastMCP | None = None


class MCPServerFactory(BaseServerFactory[FastMCP]):
    @staticmethod
    def create(**kwargs) -> FastMCP:
        """
        Create and configure the MCP server.

        Args:
            **kwargs: Additional arguments (unused, but included for base class compatibility)

        Returns:
            Configured FastMCP server instance
        """
        # Create a new FastMCP instance
        global _MCP_SERVER_INSTANCE
        assert _MCP_SERVER_INSTANCE is None, "It is not allowed to create more than one instance of FastMCP."
        _MCP_SERVER_INSTANCE = FastMCP()
        return _MCP_SERVER_INSTANCE

    @staticmethod
    def get() -> FastMCP:
        """
        Get the MCP server instance

        Returns:
            Configured FastMCP server instance
        """
        assert _MCP_SERVER_INSTANCE is not None, "It must be created FastMCP first."
        return _MCP_SERVER_INSTANCE

    @staticmethod
    def reset() -> None:
        """
        Reset the singleton instance (for testing purposes).
        """
        global _MCP_SERVER_INSTANCE
        _MCP_SERVER_INSTANCE = None


# Create a default MCP server instance for backward compatibility
mcp = MCPServerFactory.create()
mcp_factory = MCPServerFactory
