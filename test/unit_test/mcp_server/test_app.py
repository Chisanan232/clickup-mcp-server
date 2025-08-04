"""
Unit tests for the MCPServerFactory.

This module tests the factory pattern for creating and managing the MCP server instance.
"""

from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock, patch

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


class TestMCPServerLifespan:
    """Test suite for the MCPServerFactory.lifespan method."""

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

    async def test_lifespan_successful_creation(self):
        """Test that lifespan returns a valid context manager when server exists."""
        # Create a mock MCP server with a session manager
        mock_mcp = MagicMock()
        mock_session_manager = MagicMock()
        mock_run_context = AsyncMock()
        mock_session_manager.run.return_value = mock_run_context
        mock_mcp.session_manager = mock_session_manager

        # Setup the MCPServerFactory to return our mock
        with patch("clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE", mock_mcp):
            # Get the lifespan function that FastAPI will call
            lifespan_func = MCPServerFactory.lifespan()

            # Verify it's a callable function
            assert callable(lifespan_func)

            # Call the function to get the actual context manager
            mock_app = MagicMock(spec=FastAPI)
            lifespan_cm = lifespan_func(mock_app)

            # Verify the result is an async context manager
            assert hasattr(lifespan_cm, '__aenter__')
            assert hasattr(lifespan_cm, '__aexit__')

            # Use the context manager
            async with lifespan_cm:
                # Verify session manager run was called
                mock_session_manager.run.assert_called_once()
                mock_run_context.__aenter__.assert_called_once()

    async def test_lifespan_without_server_creation(self):
        """Test that lifespan raises an appropriate error when no server exists."""
        # Don't create a server instance first
        with pytest.raises(AssertionError) as excinfo:
            # Call lifespan - this should raise an AssertionError
            MCPServerFactory.lifespan()

        # Verify the error message is developer-friendly
        assert "Please create a FastMCP instance first by calling *MCPServerFactory.create()*." in str(excinfo.value)

    async def test_lifespan_context_manager_behavior(self):
        """Test that the lifespan context manager yields appropriately."""
        # Create a mock MCP server
        mock_mcp = MagicMock()

        # Create a special mock for the session manager that tracks context entry/exit
        context_entered = False
        context_exited = False

        class MockAsyncContextManager:
            async def __aenter__(self):
                nonlocal context_entered
                context_entered = True
                return None

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                nonlocal context_exited
                context_exited = True
                return None

        mock_session_manager = MagicMock()
        mock_session_manager.run.return_value = MockAsyncContextManager()
        mock_mcp.session_manager = mock_session_manager

        # Setup the MCPServerFactory to return our mock
        with patch("clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE", mock_mcp):
            # Get the lifespan function
            lifespan_func = MCPServerFactory.lifespan()

            # Call the function with a mock app to get the context manager
            mock_app = MagicMock(spec=FastAPI)
            lifespan_cm = lifespan_func(mock_app)

            # Track if yield was reached
            yield_reached = False

            # Use the context manager
            async with lifespan_cm:
                # If we get here, the context manager has yielded
                yield_reached = True
                # Verify the session manager context was entered
                assert context_entered, "Session manager context should be entered before yield"

            # Verify the yield was reached
            assert yield_reached, "Context manager should yield control"
            # Verify context was exited
            assert context_exited, "Session manager context should be exited after yield"

    def test_lifespan_handles_get_exceptions(self):
        """Test that lifespan properly wraps and enhances any exceptions from get()."""
        # Create a patch that forces MCPServerFactory.get() to raise an AssertionError
        with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get",
                   side_effect=AssertionError("It must be created FastMCP first.")):
            with pytest.raises(AssertionError) as excinfo:
                MCPServerFactory.lifespan()

            # Verify the error message is enhanced with helpful instruction
            error_message = str(excinfo.value)
            assert "Please create a FastMCP instance first" in error_message
            assert "*MCPServerFactory.create()*" in error_message

    def test_lifespan_function_signature(self):
        """Test that the lifespan function has the correct signature for FastAPI."""
        # Create a mock MCP server
        mock_mcp = MagicMock()

        # Setup the MCPServerFactory to return our mock
        with patch("clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE", mock_mcp):
            # Get the lifespan function
            lifespan_func = MCPServerFactory.lifespan()

            # Lifespan functions in FastAPI should accept a single app parameter
            import inspect
            signature = inspect.signature(lifespan_func)

            # Should have one parameter
            assert len(signature.parameters) == 1

            # The parameter should be for the app
            app_param = list(signature.parameters.values())[0]
            assert app_param.name == "_", "The parameter should be named '_' as in the implementation"
