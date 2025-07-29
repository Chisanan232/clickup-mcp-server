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

        # Create mock Pydantic model objects with model_dump method
        resource1 = MagicMock()
        resource1.model_dump.return_value = {"id": "resource1", "name": "Resource 1"}
        resource2 = MagicMock()
        resource2.model_dump.return_value = {"id": "resource2", "name": "Resource 2"}

        tool1 = MagicMock()
        tool1.model_dump.return_value = {"name": "tool1", "description": "Tool 1"}
        tool2 = MagicMock()
        tool2.model_dump.return_value = {"name": "tool2", "description": "Tool 2"}

        prompt1 = MagicMock()
        prompt1.model_dump.return_value = {"name": "prompt1", "content": "Prompt 1 content"}
        prompt2 = MagicMock()
        prompt2.model_dump.return_value = {"name": "prompt2", "content": "Prompt 2 content"}

        template1 = MagicMock()
        template1.model_dump.return_value = {"id": "template1", "name": "Template 1", "schema": {"type": "object"}}
        template2 = MagicMock()
        template2.model_dump.return_value = {"id": "template2", "name": "Template 2", "schema": {"type": "object"}}

        # Set up asynchronous method returns
        mock.list_resources = AsyncMock()
        mock.list_resources.return_value = [resource1, resource2]

        mock.list_tools = AsyncMock()
        mock.list_tools.return_value = [tool1, tool2]

        mock.list_prompts = AsyncMock()
        mock.list_prompts.return_value = [prompt1, prompt2]

        mock.list_resource_templates = AsyncMock()
        mock.list_resource_templates.return_value = [template1, template2]

        # Set up proper mock for the execute method
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
        # Create mock resource objects with model_dump method
        resource1 = MagicMock()
        resource1.model_dump.return_value = {"id": "test_resource_1", "name": "Test Resource 1"}
        resource2 = MagicMock()
        resource2.model_dump.return_value = {"id": "test_resource_2", "name": "Test Resource 2"}

        # Set up mock resources
        mock_mcp.list_resources = AsyncMock()
        mock_mcp.list_resources.return_value = [resource1, resource2]

        # Test endpoint
        response = test_client.get("/mcp-utils/resources")
        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert "resources" in data
        assert data["resources"] == [
            {"id": "test_resource_1", "name": "Test Resource 1"},
            {"id": "test_resource_2", "name": "Test Resource 2"},
        ]

        # Verify the method was called
        mock_mcp.list_resources.assert_called_once()

    def test_mcp_tools_endpoint(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test the MCP tools listing endpoint."""
        # Create mock tool objects with model_dump method
        tool1 = MagicMock()
        tool1.model_dump.return_value = {"name": "test_tool_1", "description": "Test Tool 1"}
        tool2 = MagicMock()
        tool2.model_dump.return_value = {"name": "test_tool_2", "description": "Test Tool 2"}

        # Set up mock tools
        mock_mcp.list_tools = AsyncMock()
        mock_mcp.list_tools.return_value = [tool1, tool2]

        # Test endpoint
        response = test_client.get("/mcp-utils/tools")
        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert "tools" in data
        assert data["tools"] == [
            {"name": "test_tool_1", "description": "Test Tool 1"},
            {"name": "test_tool_2", "description": "Test Tool 2"},
        ]

        # Verify the method was called
        mock_mcp.list_tools.assert_called_once()

    def test_mcp_prompts_endpoint(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test the MCP prompts listing endpoint."""
        # Create mock prompt objects with model_dump method
        prompt1 = MagicMock()
        prompt1.model_dump.return_value = {"name": "test_prompt_1", "content": "Test Prompt 1 content"}
        prompt2 = MagicMock()
        prompt2.model_dump.return_value = {"name": "test_prompt_2", "content": "Test Prompt 2 content"}

        # Set up mock prompts
        mock_mcp.list_prompts = AsyncMock()
        mock_mcp.list_prompts.return_value = [prompt1, prompt2]

        # Test endpoint
        response = test_client.get("/mcp-utils/prompts")
        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert "prompts" in data
        assert data["prompts"] == [
            {"name": "test_prompt_1", "content": "Test Prompt 1 content"},
            {"name": "test_prompt_2", "content": "Test Prompt 2 content"},
        ]

        # Verify the method was called
        mock_mcp.list_prompts.assert_called_once()

    def test_mcp_resource_templates_endpoint(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
        """Test the MCP resource templates listing endpoint."""
        # Create mock template objects with model_dump method
        template1 = MagicMock()
        template1.model_dump.return_value = {
            "id": "test_template_1",
            "name": "Test Template 1",
            "schema": {"type": "object"},
        }
        template2 = MagicMock()
        template2.model_dump.return_value = {
            "id": "test_template_2",
            "name": "Test Template 2",
            "schema": {"type": "object"},
        }

        # Set up mock templates
        mock_mcp.list_resource_templates = AsyncMock()
        mock_mcp.list_resource_templates.return_value = [template1, template2]

        # Test endpoint
        response = test_client.get("/mcp-utils/resource_templates")
        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert "resource_templates" in data
        assert data["resource_templates"] == [
            {"id": "test_template_1", "name": "Test Template 1", "schema": {"type": "object"}},
            {"id": "test_template_2", "name": "Test Template 2", "schema": {"type": "object"}},
        ]

        # Verify the method was called
        mock_mcp.list_resource_templates.assert_called_once()

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
        
        # Mock router
        mock_router = MagicMock()
        mock_router.add_api_route = MagicMock()

        # Patch both the web global and the mcp_server global
        with (
            patch("clickup_mcp.web_server.app.web", mock_web_instance),
            patch("clickup_mcp.web_server.app.mcp_server", mock_mcp),
            patch("clickup_mcp.web_server.app.APIRouter", return_value=mock_router),
        ):
            # Import mount_service within the patch context
            # Call mount_service directly with the default server type
            from clickup_mcp.models.cli import MCPTransportType
            from clickup_mcp.web_server.app import mount_service

            mount_service(MCPTransportType.SSE)

            # Verify SSE app was called
            mock_mcp.sse_app.assert_called_once()
            mock_mcp.streamable_http_app.assert_not_called()
            
            # Verify that add_api_route was called with correct path and app
            mock_router.add_api_route.assert_called_once()
            args, kwargs = mock_router.add_api_route.call_args
            assert args[0] == "/mcp"  # Both transports now use the same endpoint
            assert args[1] == mock_sse  # App is second positional arg, not a kwarg
            assert kwargs["methods"] == ["GET", "POST"]
            
            # Verify that the router was included in the web app
            mock_web_instance.include_router.assert_called_once_with(mock_router)
