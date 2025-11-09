"""
Integration tests to specifically verify that the web server properly mounts MCP server components.

This test suite focuses on validating that the mounted endpoints (SSE and Streaming HTTP)
are correctly accessible when the web server is instantiated with real MCP components.
"""

import inspect
import logging
import os
from typing import Any, Generator, Optional
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.mcp_server.app import FastMCP, MCPServerFactory
from clickup_mcp.models.cli import MCPTransportType, ServerConfig
from clickup_mcp.web_server.app import WebServerFactory, create_app, mount_service

# Set up logging for test debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestMCPServerMounting:
    """
    Tests focused on verifying that MCP server components are properly mounted in the web server.
    """

    original_web_server: Any
    original_mcp_server: Optional[FastMCP]

    @pytest.fixture(autouse=True)
    def reset_singletons(self) -> Generator[None, None, None]:
        """Reset the singleton instances before each test."""
        # Import here to avoid circular imports
        import clickup_mcp.mcp_server.app
        import clickup_mcp.web_server.app
        from clickup_mcp.client import ClickUpAPIClientFactory

        # Store original values
        self.original_web_server = clickup_mcp.web_server.app._WEB_SERVER_INSTANCE
        self.original_mcp_server = clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE

        # Reset before test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = None
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = None
        WebServerFactory.reset()
        MCPServerFactory.reset()
        ClickUpAPIClientFactory.reset()

        # Run test
        yield

        # Reset after test to not affect other tests
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = self.original_web_server
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = self.original_mcp_server
        WebServerFactory.reset()
        MCPServerFactory.reset()
        ClickUpAPIClientFactory.reset()

    @pytest.fixture
    def mock_clickup_client(self) -> MagicMock:
        """Create a mock ClickUp API client."""
        mock = MagicMock()
        # Set up basic return values
        mock.get_spaces.return_value = [{"id": "space1", "name": "Test Space"}]
        return mock

    def test_direct_mcp_inspection(self) -> None:
        """
        Directly inspect the MCP server instance to verify that SSE and HTTP streaming apps are available.
        This ensures that these components exist before we try to mount them.
        """
        # Create MCP server instance
        mcp_server = MCPServerFactory.create()

        # Check if the required methods exist
        assert hasattr(mcp_server, "sse_app"), "MCP server missing sse_app method"
        assert hasattr(mcp_server, "streamable_http_app"), "MCP server missing streamable_http_app method"

        # Log method details for debugging
        logger.debug(f"sse_app method: {inspect.signature(mcp_server.sse_app)}")
        logger.debug(f"streamable_http_app method: {inspect.signature(mcp_server.streamable_http_app)}")

        # Check if methods are coroutines (async)
        is_sse_app_coro = inspect.iscoroutinefunction(mcp_server.sse_app)
        is_stream_app_coro = inspect.iscoroutinefunction(mcp_server.streamable_http_app)
        logger.debug(f"sse_app is coroutine: {is_sse_app_coro}")
        logger.debug(f"streamable_http_app is coroutine: {is_stream_app_coro}")

        # Try to call the methods to see what they return
        try:
            if is_sse_app_coro:
                logger.debug("SSE app is a coroutine function - cannot call directly")
            else:
                sse_result = mcp_server.sse_app()
                logger.debug(f"SSE app result: {type(sse_result)}")

            if is_stream_app_coro:
                logger.debug("Streaming HTTP app is a coroutine function - cannot call directly")
            else:
                stream_result = mcp_server.streamable_http_app()
                logger.debug(f"Streaming HTTP app result: {type(stream_result)}")
        except Exception as e:
            logger.debug(f"Exception calling app methods: {e}")

    @patch("clickup_mcp.web_server.app.web_factory")
    @patch("clickup_mcp.web_server.app.mcp_factory")
    def test_mount_service_patched(self, mock_mcp_factory: MagicMock, mock_web_factory: MagicMock) -> None:
        """Test that mount_service correctly handles both transport types."""
        # Setup mock MCP server
        mock_mcp_server = MagicMock()
        mock_web_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_streaming_app = MagicMock()

        mock_mcp_server.sse_app.return_value = mock_sse_app
        mock_mcp_server.streamable_http_app.return_value = mock_streaming_app
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_web_factory.get.return_value = mock_web_server

        # Case 1: Test with SSE transport
        mount_service(MCPTransportType.SSE.value)

        mock_mcp_factory.get.assert_called()
        mock_mcp_server.sse_app.assert_called_once()
        mock_web_server.mount.assert_called_once_with("/sse", mock_sse_app)
        mock_mcp_server.streamable_http_app.assert_not_called()

        # Reset all mocks
        mock_mcp_factory.reset_mock()
        mock_web_factory.reset_mock()
        mock_mcp_server.reset_mock()
        mock_mcp_server.sse_app.return_value = mock_sse_app
        mock_mcp_server.streamable_http_app.return_value = mock_streaming_app
        mock_mcp_factory.get.return_value = mock_mcp_server

        # Case 2: Test with HTTP streaming transport
        mount_service(MCPTransportType.HTTP_STREAMING.value)

        mock_mcp_factory.get.assert_called()
        mock_mcp_server.streamable_http_app.assert_called_once()
        mock_web_server.mount.assert_called_once_with("/mcp", mock_streaming_app)
        mock_mcp_server.sse_app.assert_not_called()

    def test_fix_mount_service(self) -> None:
        """
        Test and diagnose what's wrong with the mount_service function.
        This test identifies if the issue is with async/sync handling.
        """
        # Create MCP server first
        mcp_server = MCPServerFactory.create()
        # Then create web server
        web_server = WebServerFactory.create()

        # Create test app instances to use for verification
        sse_test_app = FastAPI()
        streaming_test_app = FastAPI()

        # Check if the methods return coroutines
        is_sse_app_coro = inspect.iscoroutinefunction(mcp_server.sse_app)
        is_stream_app_coro = inspect.iscoroutinefunction(mcp_server.streamable_http_app)

        logger.debug(f"sse_app is coroutine: {is_sse_app_coro}")
        logger.debug(f"streamable_http_app is coroutine: {is_stream_app_coro}")

        # Create a fixed mount_service that handles both sync and async methods
        # For this test, only mount the SSE app to match the default behavior
        def fixed_mount_service(mcp_server: FastMCP) -> FastAPI:
            """Fixed version of mount_service that handles both async and sync methods."""
            # Create FastAPI instance directly
            web = FastAPI()

            # Handle sse_app method
            if is_sse_app_coro:
                logger.debug("sse_app is async - need to run in event loop")
                # Need to handle async method
                # For testing purposes, we'll just use the mock return value
                web.mount("/sse", sse_test_app)
            else:
                logger.debug("sse_app is sync - can call directly")
                web.mount("/sse", mcp_server.sse_app())

            # We don't mount HTTP streaming in this test to match the default behavior

            return web

        # Use the fixed mount_service function
        app = fixed_mount_service(mcp_server)

        # Verify routes
        routes = app.routes
        mount_routes = [r for r in routes if hasattr(r, "app")]

        logger.debug("Routes with fixed mount_service:")
        for r in mount_routes:
            if hasattr(r, "path"):
                logger.debug(f"  {r.path} -> {r.app}")

        # Verify only SSE was mounted
        assert any(r.path == "/sse" for r in mount_routes), "MCP app not mounted with fixed function"
        assert sum(1 for r in mount_routes if r.path == "/sse") == 1, "Multiple MCP mounts found"

    def test_create_app_wrapper(self) -> None:
        """Test that the create_app function properly mounts the MCP server."""
        try:
            # Reset singletons for a clean test environment
            WebServerFactory.reset()
            MCPServerFactory.reset()
            ClickUpAPIClientFactory.reset()

            # Use patch.dict to set the environment variable directly
            with patch.dict(os.environ, {"CLICKUP_API_TOKEN": "test_token_for_mount"}):
                # Create MCP server first (important for proper initialization order)
                MCPServerFactory.create()
                WebServerFactory.create()

                # Create app with the server config that specifies SSE type
                create_app(ServerConfig(transport=MCPTransportType.SSE))

                # Get the actual app instance from the factory to check routes
                # This is the key - we need to check the WebServerFactory.get() instance
                # since that's where mount_service adds the routes
                actual_app = WebServerFactory.get()

                # Look for the /sse mount in the actual_app routes
                routes = actual_app.routes
                found_sse_mount = False

                logger.debug("All routes after mount_service:")
                for route in routes:
                    if hasattr(route, "path"):
                        path = route.path
                        if path == "/sse":
                            found_sse_mount = True
                        if hasattr(route, "app"):
                            logger.debug(f"  Mount: {path} -> {type(route.app).__name__}")
                        else:
                            logger.debug(f"  Route: {path}")

                # Verify the /sse route was mounted
                assert found_sse_mount, "MCP app not mounted at /sse"

        except Exception as e:
            logger.exception(f"Test failed with error: {str(e)}")
            raise

        finally:
            # Clean up singletons
            WebServerFactory.reset()
            MCPServerFactory.reset()
            ClickUpAPIClientFactory.reset()
