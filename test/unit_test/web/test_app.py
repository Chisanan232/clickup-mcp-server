"""
Unit tests for FastAPI web server integration with MCP server.

This module tests the functionality of mounting an MCP server on FastAPI.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.web_server.app import WebServerFactory, create_app


class TestWebServer:
    """Test suite for the FastAPI web server integration."""

    @pytest.fixture(autouse=True)
    def reset_factories(self, monkeypatch):
        """Reset the global web server and client factory instances before and after each test."""
        # Import here to avoid circular imports
        import clickup_mcp.mcp_server.app
        import clickup_mcp.web_server.app

        # Store original instances
        self.original_web_instance = clickup_mcp.web_server.app._WEB_SERVER_INSTANCE
        self.original_mcp_instance = clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE

        # Set up environment for tests
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_for_web_server")

        # Reset factories before test
        WebServerFactory.reset()
        ClickUpAPIClientFactory.reset()
        clickup_mcp.mcp_server.app.MCPServerFactory.reset()

        yield

        # Restore original instances after test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = self.original_web_instance
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = self.original_mcp_instance

    @pytest.fixture
    def mock_mcp(self) -> MagicMock:
        """Fixture to create a mock MCP server."""
        mock = MagicMock()
        # Set up synchronous method returns
        mock.list_resources.return_value = ["resource1", "resource2"]
        mock.list_tools.return_value = ["tool1", "tool2"]

        # Set up execute method (potentially async)
        mock.execute = AsyncMock(return_value={"success": True, "data": "result"})

        # Set up SSE and streaming HTTP apps
        mock_sse_app = MagicMock()
        mock_streamable_app = MagicMock()
        mock.sse_app.return_value = mock_sse_app
        mock.streamable_http_app.return_value = mock_streamable_app

        return mock

    @pytest.fixture
    def test_client(self, mock_mcp: MagicMock) -> TestClient:
        """Fixture to create a FastAPI test client with mock MCP."""
        # First create a new web server instance
        WebServerFactory.create()

        # Then patch MCPServerFactory.get to return our mock
        with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp):
            # Important: We need to create the app after patching MCPServerFactory
            # so that the route handlers capture our mock in their closures
            app = create_app()
            return TestClient(app)

    def test_root_endpoint(self, test_client: TestClient) -> None:
        """Test the root endpoint returns proper status."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "ok"

    def test_docs_endpoint(self, test_client: TestClient) -> None:
        """Test that Swagger UI docs are available."""
        response = test_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_mcp_resource_endpoint(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test accessing MCP resources through FastAPI."""
        response = test_client.get("/mcp/resources")
        assert response.status_code == 200

        # Verify the MCP server was called to list resources
        mock_mcp.list_resources.assert_called_once()

    def test_mcp_tools_endpoint(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test that the MCP tools endpoint returns the expected tools."""
        response = test_client.get("/mcp/tools")
        assert response.status_code == 200

        # Verify the list_tools method was called
        mock_mcp.list_tools.assert_called_once()

        # Verify the response contains the expected tools
        assert response.json() == {"tools": ["tool1", "tool2"]}

    def test_execute_tool(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test executing an MCP tool through the API."""
        # Make the request
        response = test_client.post("/mcp/execute/test_tool", json={"param1": "value1", "param2": "value2"})

        # Verify response
        assert response.status_code == 200
        assert "result" in response.json()

        # Verify the tool was executed with correct parameters
        mock_mcp.execute.assert_awaited_once_with("test_tool", param1="value1", param2="value2")

    def test_mount_service_integration(self, mock_mcp: MagicMock) -> None:
        """Test that mount_service is called during app initialization and mounts services correctly."""
        # First create a web server instance
        WebServerFactory.create()

        # Patch the mount_service function to verify it's called
        with patch("clickup_mcp.web_server.app.mount_service") as mock_mount_service:
            # Create a web app (which should call mount_service)
            with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp):
                create_app()

            # Verify mount_service was called with the mock MCP server
            mock_mount_service.assert_called_once_with(mock_mcp, "sse")

    def test_mounted_apps_are_accessible(self) -> None:
        """
        Test that the mounted apps are correctly accessible through the web server.
        This is an integration test that verifies the mount_service function
        correctly adds the MCP server's SSE and streamable HTTP apps.
        """
        # Create mock MCP server and its apps
        mock_mcp = MagicMock()
        mock_sse = MagicMock()
        mock_streaming = MagicMock()
        mock_mcp.sse_app.return_value = mock_sse
        mock_mcp.streamable_http_app.return_value = mock_streaming

        # Create a mock web instance
        mock_web_instance = MagicMock(spec=FastAPI)

        # Patch both the web global and the WebServerFactory.get() method
        with patch("clickup_mcp.web_server.app.web", mock_web_instance):
            # Import mount_service within the patch context
            # Call mount_service directly with the default server type
            from clickup_mcp.models.cli import MCPServerType
            from clickup_mcp.web_server.app import mount_service

            mount_service(mock_mcp, MCPServerType.SSE)

            # Verify the MCP server apps were created
            mock_mcp.sse_app.assert_called_once()
            mock_mcp.streamable_http_app.assert_not_called()  # Should not be called for SSE type

            # Verify the web instance mounted the apps correctly
            assert mock_web_instance.mount.call_count == 1  # Only SSE app should be mounted
            mock_web_instance.mount.assert_any_call("/mcp", mock_sse)
