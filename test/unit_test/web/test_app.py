"""
Unit tests for FastAPI web server integration with MCP server.

This module tests the functionality of mounting an MCP server on FastAPI.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from clickup_mcp.web_server import create_app


class TestWebServer:
    """Test suite for the FastAPI web server integration."""

    @pytest.fixture
    def mock_mcp(self):
        """Fixture to create a mock MCP server."""
        mock = MagicMock()
        mock.get_resource.return_value = {"name": "test_resource"}
        return mock

    @pytest.fixture
    def test_client(self, mock_mcp):
        """Fixture to create a FastAPI test client with mock MCP."""
        with patch("clickup_mcp.web_server.get_mcp_server", return_value=mock_mcp):
            app = create_app()
            return TestClient(app)

    def test_root_endpoint(self, test_client):
        """Test the root endpoint returns proper status."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "ok"
    
    def test_docs_endpoint(self, test_client):
        """Test that Swagger UI docs are available."""
        response = test_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_mcp_resource_endpoint(self, test_client, mock_mcp):
        """Test accessing MCP resources through FastAPI."""
        response = test_client.get("/mcp/resources")
        assert response.status_code == 200
        
        # Verify the MCP server was called to list resources
        mock_mcp.list_resources.assert_called_once()
    
    def test_mcp_integration(self, test_client, mock_mcp):
        """Test that MCP server is properly integrated and mounted."""
        test_client.get("/mcp/tools")
        # Verify the MCP tools endpoint was accessed
        mock_mcp.get_tools.assert_called_once()
