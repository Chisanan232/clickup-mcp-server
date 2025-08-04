"""
Unit tests for the WebServerFactory.

This module tests the factory pattern for creating and managing the Web server instance.
"""

from typing import Any, Dict, Generator, Optional, Union
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from clickup_mcp.models.cli import MCPTransportType
from clickup_mcp.web_server.app import WebServerFactory, mount_service
from clickup_mcp.mcp_server.app import MCPServerFactory


class TestWebServerFactory:
    """Test suite for the WebServerFactory class."""

    original_instance: Optional[Any]
    original_mcp_instance: Optional[Any]

    @pytest.fixture(autouse=True)
    def reset_web_server(self) -> Generator[None, None, None]:
        """Reset the global web server instance before and after each test."""
        # Import here to avoid circular imports
        import clickup_mcp.web_server.app
        import clickup_mcp.mcp_server.app

        # Store original instances
        self.original_instance = clickup_mcp.web_server.app._WEB_SERVER_INSTANCE
        self.original_mcp_instance = clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE

        # Reset before test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = None
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = None

        # Run the test
        yield

        # Restore original after test to avoid affecting other tests
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = self.original_instance
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = self.original_mcp_instance

    @pytest.fixture
    def mock_mcp_server(self) -> MagicMock:
        """Fixture to create a mock MCP server."""
        mock = MagicMock()
        mock.session_manager = MagicMock()
        mock.session_manager.run = MagicMock()
        return mock

    def test_create_web_server(self, mock_mcp_server: MagicMock) -> None:
        """Test creating a new web server instance."""
        # Create MCP server instance first
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp_server):
            MCPServerFactory.create()

        # Patch MCPServerFactory.lifespan to return mock lifespan
        with patch("clickup_mcp.mcp_server.app.MCPServerFactory.lifespan", return_value=mock_mcp_server.session_manager.run):
            # Need to patch where FastAPI is imported, not where it's defined
            with patch("clickup_mcp.web_server.app.FastAPI") as mock_fastapi:
                # Configure mock
                mock_instance = MagicMock(spec=FastAPI)
                mock_fastapi.return_value = mock_instance

                # Call create method
                server = WebServerFactory.create()

                # Verify FastAPI was instantiated correctly
                mock_fastapi.assert_called_once()

                # Verify the correct title and description were used
                mock_fastapi.assert_called_once_with(
                    title="ClickUp MCP Server",
                    description="A FastAPI web server that hosts a ClickUp MCP server for interacting with ClickUp API",
                    version="0.1.0",
                    lifespan=mock_mcp_server.session_manager.run,
                )

                # Verify CORS middleware was added
                mock_instance.add_middleware.assert_called_once()

                # Verify the returned instance is the mock
                assert server is mock_instance

                # Verify the global instance is set
                import clickup_mcp.web_server.app as app_module

                assert app_module._WEB_SERVER_INSTANCE is mock_instance

    def test_get_web_server(self, mock_mcp_server: MagicMock) -> None:
        """Test getting an existing web server instance."""
        # Create MCP server instance first
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp_server):
            MCPServerFactory.create()

        # Create a server first using a mock
        with patch("clickup_mcp.web_server.app.FastAPI") as mock_fastapi:
            mock_instance = MagicMock(spec=FastAPI)
            mock_fastapi.return_value = mock_instance

            # Create the instance
            created_server = WebServerFactory.create()

            # Now get the instance
            retrieved_server = WebServerFactory.get()

            # Verify both are the same instance
            assert created_server is retrieved_server
            assert retrieved_server is mock_instance

    def test_create_fails_when_already_created(self, mock_mcp_server: MagicMock) -> None:
        """Test that creating a server when one already exists raises an error."""
        # Create MCP server instance first
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp_server):
            MCPServerFactory.create()
            
        # Create a server first
        WebServerFactory.create()

        # Attempting to create again should raise an AssertionError
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.create()

        assert "not allowed to create more than one instance" in str(excinfo.value)

    def test_get_fails_when_not_created(self) -> None:
        """Test that getting a server when none exists raises an error."""
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.get()

        assert "It must be created web server first" in str(excinfo.value)
        
    def test_backward_compatibility_global_web(self) -> None:
        """Test that the global web variable exists and is a FastAPI instance."""
        # We need to test that the module-level 'web' variable exists and is a FastAPI instance
        import clickup_mcp.web_server.app

        # Verify the module has a global 'web' variable
        assert hasattr(clickup_mcp.web_server.app, "web")

        # Reset the web server instance to make sure we're testing the module's instance
        # We need to temporarily store the 'web' instance before resetting _WEB_SERVER_INSTANCE
        web_instance = clickup_mcp.web_server.app.web

        # Verify it has the expected type
        assert isinstance(web_instance, FastAPI) or web_instance.__class__.__name__ == "FastAPI"

        # For the backward compatibility test, we need to make sure the module's 'web'
        # instance is what's returned by get()
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = web_instance
        assert WebServerFactory.get() is web_instance

    @pytest.mark.parametrize(
        "transport_type, expected_app_calls",
        [
            (
                MCPTransportType.SSE.value,
                {"sse_app": 1, "streamable_http_app": 0, "endpoint_path": "/sse"},
            ),
            (
                MCPTransportType.HTTP_STREAMING.value,
                {"sse_app": 0, "streamable_http_app": 1, "endpoint_path": "/mcp"},
            ),
        ],
    )
    def test_mount_service_parameterized(
        self,
        transport_type: str,
        expected_app_calls: Dict[str, Union[int, str]],
        mock_mcp_server: MagicMock,
    ) -> None:
        """Test that mount_service correctly mounts the specified server types."""
        # Create mock web server and get MCP server mock from fixture
        mock_web = MagicMock(spec=FastAPI)

        # First create the MCP server instance
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp_server):
            MCPServerFactory.create()

        # Set up the patching for the test
        with patch("clickup_mcp.web_server.app.web", mock_web):
            with patch("clickup_mcp.web_server.app.mcp_factory.get", return_value=mock_mcp_server):
                # Call the function under test
                mount_service(transport=transport_type)

        # Verify SSE app was called the expected number of times
        assert mock_mcp_server.sse_app.call_count == expected_app_calls["sse_app"]
        
        # Verify HTTP streaming app was called the expected number of times
        assert mock_mcp_server.streamable_http_app.call_count == expected_app_calls["streamable_http_app"]
        
        # Verify mount was called correctly
        mock_web.mount.assert_called_once()
        args, kwargs = mock_web.mount.call_args
        assert args[0] == expected_app_calls["endpoint_path"]
        
        # Verify the correct app was passed
        if transport_type == MCPTransportType.SSE.value:
            assert args[1] == mock_mcp_server.sse_app.return_value
        else:
            assert args[1] == mock_mcp_server.streamable_http_app.return_value

    @pytest.mark.parametrize(
        "invalid_transport_type",
        [
            "invalid_type",
            123,
            None,
        ],
    )
    def test_mount_service_invalid_type_parameterized(
        self, invalid_transport_type: Any, mock_mcp_server: MagicMock
    ) -> None:
        """Test that mount_service raises ValueError with invalid server types."""
        # Create MCP server instance first
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp_server):
            MCPServerFactory.create()

        # Create a mock web server
        mock_web = MagicMock(spec=FastAPI)

        # Patch the web app and mcp_factory.get
        with patch("clickup_mcp.web_server.app.web", mock_web):
            with patch("clickup_mcp.web_server.app.mcp_factory.get", return_value=mock_mcp_server):
                # Test that invalid server type raises ValueError
                with pytest.raises(ValueError) as excinfo:
                    mount_service(transport=invalid_transport_type)

                assert "Unknown transport protocol:" in str(excinfo.value)
