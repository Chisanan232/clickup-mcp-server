"""
Unit tests for FastAPI web server integration with MCP server.

This module tests the functionality of mounting an MCP server on FastAPI.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from clickup_mcp.web_server.app import create_app, WebServerFactory


class TestWebServer:
    """Test suite for the FastAPI web server integration."""

    @pytest.fixture(autouse=True)
    def reset_web_server(self):
        """Reset the global web server instance before and after each test."""
        # Import here to avoid circular imports
        import clickup_mcp.web_server.app
        
        # Store original instance
        self.original_web_instance = clickup_mcp.web_server.app._WEB_SERVER_INSTANCE
        
        # Reset before test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = None
        
        # Run the test
        yield
        
        # Restore original after test to avoid affecting other tests
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = self.original_web_instance

    @pytest.fixture
    def mock_mcp(self) -> MagicMock:
        """Fixture to create a mock MCP server."""
        mock = MagicMock()
        # Set up synchronous method returns
        mock.list_resources.return_value = ["resource1", "resource2"]
        mock.list_tools.return_value = ["tool1", "tool2"]

        # Set up execute method (potentially async)
        mock.execute = AsyncMock(return_value={"success": True, "data": "result"})

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
