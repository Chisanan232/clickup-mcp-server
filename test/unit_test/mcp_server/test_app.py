"""
Unit tests for the MCPServerFactory.

This module tests the factory pattern for creating and managing the MCP server instance.
"""

from unittest.mock import MagicMock, patch

import pytest

from clickup_mcp.mcp_server.app import MCPServerFactory


class TestMCPServerFactory:
    """Test suite for the MCPServerFactory class."""

    @pytest.fixture(autouse=True)
    def reset_mcp_server(self):
        """Reset the global MCP server instance before and after each test."""
        # Import here to avoid circular imports
        import clickup_mcp.mcp_server.app

        # Store original instance
        self.original_instance = clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE

        # Reset before test
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = None

        # Run the test
        yield

        # Restore original after test to avoid affecting other tests
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = self.original_instance

    def test_create_mcp_server(self):
        """Test creating a new MCP server instance."""
        # Use the correct import path as used in the implementation
        with patch("clickup_mcp.mcp_server.app.FastMCP") as mock_fast_mcp:
            # Configure mock
            mock_instance = MagicMock()
            mock_fast_mcp.return_value = mock_instance

            # Call create method
            server = MCPServerFactory.create()

            # Verify FastMCP was instantiated correctly
            mock_fast_mcp.assert_called_once()

            # Verify the returned instance is the mock
            assert server is mock_instance

            # Verify the global instance is set
            import clickup_mcp.mcp_server.app as app_module

            assert app_module._MCP_SERVER_INSTANCE is mock_instance

    def test_get_mcp_server(self):
        """Test getting an existing MCP server instance."""
        # Create a server first using a mock
        with patch("clickup_mcp.mcp_server.app.FastMCP") as mock_fast_mcp:
            mock_instance = MagicMock()
            mock_fast_mcp.return_value = mock_instance

            # Create the instance
            created_server = MCPServerFactory.create()

            # Now get the instance
            retrieved_server = MCPServerFactory.get()

            # Verify both are the same instance
            assert created_server is retrieved_server
            assert retrieved_server is mock_instance

    def test_create_fails_when_already_created(self):
        """Test that creating a server when one already exists raises an error."""
        # Create a server first
        with patch("clickup_mcp.mcp_server.app.FastMCP"):
            # Create the first instance
            MCPServerFactory.create()

            # Attempting to create again should raise an AssertionError
            with pytest.raises(AssertionError) as excinfo:
                MCPServerFactory.create()

            assert "not allowed to create more than one instance" in str(excinfo.value)

    def test_get_fails_when_not_created(self):
        """Test that getting a server before creating one raises an error."""
        # Attempting to get before creating should raise an AssertionError
        with pytest.raises(AssertionError) as excinfo:
            MCPServerFactory.get()

        assert "must be created FastMCP first" in str(excinfo.value)

    def test_backward_compatibility_global_mcp(self):
        """Test that the global mcp instance is created for backward compatibility."""
        # We need to test that the module-level 'mcp' variable exists and is a FastMCP instance
        import clickup_mcp.mcp_server.app

        # Verify the module has a global 'mcp' variable
        assert hasattr(clickup_mcp.mcp_server.app, "mcp")

        # Verify it's an instance of FastMCP (or at least has the same class name)
        mcp_instance = clickup_mcp.mcp_server.app.mcp
        assert mcp_instance.__class__.__name__ == "FastMCP"

        # Verify that get() returns this same instance
        # First reset our instance to make sure we're testing the module's instance
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = mcp_instance
        assert MCPServerFactory.get() is mcp_instance
