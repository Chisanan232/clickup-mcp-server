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


class TestWebServerFactory:
    """Test suite for the WebServerFactory class."""

    original_instance: Optional[Any]

    @pytest.fixture(autouse=True)
    def reset_web_server(self) -> Generator[None, None, None]:
        """Reset the global web server instance before and after each test."""
        # Import here to avoid circular imports
        import clickup_mcp.web_server.app

        # Store original instance
        self.original_instance = clickup_mcp.web_server.app._WEB_SERVER_INSTANCE

        # Reset before test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = None

        # Run the test
        yield

        # Restore original after test to avoid affecting other tests
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = self.original_instance

    def test_create_web_server(self) -> None:
        """Test creating a new web server instance."""
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
            )

            # Verify CORS middleware was added
            mock_instance.add_middleware.assert_called_once()

            # Verify the returned instance is the mock
            assert server is mock_instance

            # Verify the global instance is set
            import clickup_mcp.web_server.app as app_module

            assert app_module._WEB_SERVER_INSTANCE is mock_instance

    def test_get_web_server(self) -> None:
        """Test getting an existing web server instance."""
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

    def test_create_fails_when_already_created(self) -> None:
        """Test that creating a server when one already exists raises an error."""
        # Create a server first
        WebServerFactory.create()

        # Attempting to create again should raise an AssertionError
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.create()

        assert "not allowed to create more than one instance" in str(excinfo.value)

    def test_get_fails_when_not_created(self) -> None:
        """Test that getting a server before creating one raises an error."""
        # Attempting to get before creating should raise an AssertionError
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.get()

        assert "must be created web server first" in str(excinfo.value)

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
            # TODO: Not support yet
            # (
            #     f"{MCPTransportType.SSE.value},{MCPTransportType.HTTP_STREAMING.value}",
            #     {"sse_app": 1, "streamable_http_app": 1, "endpoint_path": None},
            # ),
        ],
    )
    def test_mount_service_parameterized(
        self,
        transport_type: str,
        expected_app_calls: Dict[str, Union[int, str]],
    ) -> None:
        """Test that mount_service correctly mounts the specified server types."""
        # Create mock web server and MCP server
        mock_web = MagicMock(spec=FastAPI)
        mock_mcp_server = MagicMock()
        
        # Create mock router
        mock_router = MagicMock()
        mock_router.add_api_route = MagicMock()

        # Define the expected calls based on the transport type
        with (
            patch("clickup_mcp.web_server.app.web", mock_web),
            patch("clickup_mcp.web_server.app.mcp_server", mock_mcp_server),
            patch("clickup_mcp.web_server.app.APIRouter", return_value=mock_router),
        ):
            # Import and call mount_service within patch context
            from clickup_mcp.web_server.app import mount_service
            mount_service(transport_type)

        # Verify SSE app was called the expected number of times
        assert mock_mcp_server.sse_app.call_count == expected_app_calls["sse_app"]
        
        # Verify HTTP streaming app was called the expected number of times
        assert mock_mcp_server.streamable_http_app.call_count == expected_app_calls["streamable_http_app"]
        
        # For specific transport types (not combined), verify path is correct
        if expected_app_calls["endpoint_path"] is not None:
            mock_router.add_api_route.assert_called_once()
            args, kwargs = mock_router.add_api_route.call_args
            assert args[0] == expected_app_calls["endpoint_path"]
            assert kwargs["methods"] == ["GET", "POST"]
        
        # If both transport types are enabled, verify both endpoints were added
        if transport_type == f"{MCPTransportType.SSE.value},{MCPTransportType.HTTP_STREAMING.value}":
            assert mock_router.add_api_route.call_count == 2
            call_args_list = mock_router.add_api_route.call_args_list
            
            # Check both paths were added
            paths = [args[0] for args, _ in call_args_list]
            assert "/sse" in paths
            assert "/mcp" in paths
        
        # Verify router was included in the web app
        mock_web.include_router.assert_called_once_with(mock_router)

    @pytest.mark.parametrize(
        "invalid_transport_type",
        [
            "invalid_type",
            123,
            None,
        ],
    )
    def test_mount_service_invalid_type_parameterized(self, invalid_transport_type: Any) -> None:
        """Test that mount_service raises ValueError with invalid server types."""
        # Create a web server instance
        with patch("clickup_mcp.web_server.app.FastAPI") as mock_fastapi:
            mock_web_instance = MagicMock(spec=FastAPI)
            mock_fastapi.return_value = mock_web_instance

            # Create the web server instance
            WebServerFactory.create()

            # Create a mock MCP server
            mock_mcp_server = MagicMock()

            # Patch the global web variable to use our mock_web_instance
            # and the global mcp_server to use our mock
            with (
                patch("clickup_mcp.web_server.app.web", mock_web_instance),
                patch("clickup_mcp.web_server.app.mcp_server", mock_mcp_server),
            ):
                # Test that invalid server type raises ValueError
                from clickup_mcp.web_server.app import mount_service

                with pytest.raises(ValueError) as excinfo:
                    mount_service(invalid_transport_type)

                assert "Unknown transport protocol:" in str(excinfo.value)
