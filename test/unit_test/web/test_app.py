"""
Unit tests for FastAPI web server integration with MCP server.

This module tests the functionality of mounting an MCP server on FastAPI.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from clickup_mcp.client import ClickUpAPIClientFactory
from clickup_mcp.models.cli import MCPTransportType, ServerConfig
from clickup_mcp.web_server.app import WebServerFactory, create_app


class TestWebServer:
    """Test cases for the FastAPI web server."""

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

        # Set up proper mock for the execute method
        # We need to use AsyncMock properly for the execute method
        mock.execute = AsyncMock()
        mock.execute.return_value = "result data"

        # Set up SSE and streaming HTTP apps
        mock_sse_app = MagicMock()
        mock_streamable_app = MagicMock()
        mock.sse_app.return_value = mock_sse_app
        mock.streamable_http_app.return_value = mock_streamable_app

        return mock

    @pytest.fixture
    def test_client(self, mock_mcp: MagicMock) -> TestClient:
        """Fixture to create a FastAPI test client with a mock MCP server."""
        # Create minimal server config to avoid NoneType.env_file error
        server_config = ServerConfig(
            host="localhost",
            port=8000,
            env_file=".env",
            transport=MCPTransportType.SSE,
        )

        # Create patchers for our test
        mcp_server_patcher = patch("clickup_mcp.web_server.app.mcp_server", mock_mcp)

        # Start the patchers
        mcp_server_patcher.start()

        try:
            # Create the web server instance first
            WebServerFactory.create()

            # Create the app with our server config
            app = create_app(server_config=server_config)

            # Create and return the test client
            client = TestClient(app)
            yield client
        finally:
            # Stop the patchers
            mcp_server_patcher.stop()

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
        """Test the MCP resource listing endpoint."""
        # Set up mock resources
        mock_mcp.list_resources.return_value = ["test_resource_1", "test_resource_2"]

        # Test endpoint
        response = test_client.get("/mcp/resources")
        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert "resources" in data
        assert data["resources"] == ["test_resource_1", "test_resource_2"]

        # Verify the method was called
        mock_mcp.list_resources.assert_called_once()

    def test_mcp_tools_endpoint(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test the MCP tools listing endpoint."""
        # Set up mock tools
        mock_mcp.list_tools.return_value = ["test_tool_1", "test_tool_2"]

        # Test endpoint
        response = test_client.get("/mcp/tools")
        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert "tools" in data
        assert data["tools"] == ["test_tool_1", "test_tool_2"]

        # Verify the method was called
        mock_mcp.list_tools.assert_called_once()

    def test_execute_tool(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test the tool execution endpoint."""
        # Define test params
        tool_name = "test_tool"
        params = {"param1": "value1", "param2": "value2"}

        # We must use a dictionary structure that matches the endpoint return
        mock_mcp.execute.return_value = "result data"

        # Test endpoint
        response = test_client.post(f"/mcp/execute/{tool_name}", json=params)
        assert response.status_code == 200

        # Verify the response matches what our endpoint returns
        data = response.json()
        assert data == {"result": "result data"}

        # Verify the method was called with correct parameters
        mock_mcp.execute.assert_awaited_once_with(tool_name, **params)

    def test_mount_service_integration(self, mock_mcp: MagicMock) -> None:
        """Test that mount_service is called during app initialization and mounts services correctly."""
        # First create a web server instance
        WebServerFactory.create()

        # Create a minimal ServerConfig object for testing
        from clickup_mcp.models.cli import ServerConfig

        test_config = ServerConfig()

        # Patch the mount_service function to verify it's called
        with patch("clickup_mcp.web_server.app.mount_service") as mock_mount_service:
            # Create a web app (which should call mount_service)
            with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp):
                create_app(server_config=test_config)

            # Check that mount_service was called
            mock_mount_service.assert_called_once()

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

        # Patch both the web global and the mcp_server global
        with (
            patch("clickup_mcp.web_server.app.web", mock_web_instance),
            patch("clickup_mcp.web_server.app.mcp_server", mock_mcp),
        ):
            # Import mount_service within the patch context
            # Call mount_service directly with the default server type
            from clickup_mcp.models.cli import MCPTransportType
            from clickup_mcp.web_server.app import mount_service

            mount_service(MCPTransportType.SSE)

            # Verify SSE app was mounted
            mock_mcp.sse_app.assert_called_once()
            mock_web_instance.mount.assert_called_once_with("/mcp", mock_sse)
