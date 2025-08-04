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
from clickup_mcp.mcp_server.app import MCPServerFactory


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
        mcp_factory_get_patcher = patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp)

        # Start the patchers
        mcp_server_patcher.start()
        mcp_factory_get_patcher.start()

        # First create the MCP server instance
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp):
            MCPServerFactory.create()

        try:
            # Now create the web server instance 
            WebServerFactory.create()

            # Create the app with our server config
            app = create_app(server_config=server_config)

            # Create and return the test client
            client = TestClient(app)
            yield client
        finally:
            # Stop the patchers
            mcp_server_patcher.stop()
            mcp_factory_get_patcher.stop()

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
        # First create an MCP server instance
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp):
            MCPServerFactory.create()
            
        # Now create a web server instance
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

        # First create an MCP server instance 
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp):
            MCPServerFactory.create()

        # Patch both the web global and the mcp_server global
        with (
            patch("clickup_mcp.web_server.app.web", mock_web_instance),
            patch("clickup_mcp.web_server.app.mcp_server", mock_mcp),
            patch("clickup_mcp.web_server.app.APIRouter", return_value=mock_router),
            patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp)
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
            assert args[0] == "/sse"  # SSE now uses /sse endpoint
            assert args[1] == mock_sse  # App is second positional arg, not a kwarg
            assert kwargs["methods"] == ["GET", "POST"]
            
            # Verify that the router was included in the web app
            mock_web_instance.include_router.assert_called_once_with(mock_router)


class TestWebServerLifespan:
    """Test suite for the WebServerFactory's lifespan property integration."""

    @pytest.fixture(autouse=True)
    def reset_factories(self):
        """Reset the global web server and MCP server instances before and after each test."""
        # Import here to avoid circular imports
        import clickup_mcp.mcp_server.app
        import clickup_mcp.web_server.app

        # Store original instances
        self.original_web_instance = clickup_mcp.web_server.app._WEB_SERVER_INSTANCE
        self.original_mcp_instance = clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE

        # Reset before test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = None
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = None

        # Run the test
        yield

        # Restore original instances after test
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = self.original_web_instance
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = self.original_mcp_instance

    def test_lifespan_correctly_passed_to_fastapi(self):
        """Test that the MCP server's lifespan function is correctly passed to FastAPI."""
        # Create a mock MCP server first since WebServerFactory.create() requires it
        with patch("clickup_mcp.mcp_server.app.FastMCP") as mock_fast_mcp:
            mock_mcp_instance = MagicMock()
            mock_fast_mcp.return_value = mock_mcp_instance
            MCPServerFactory.create()

            # Create a mock lifespan function
            mock_lifespan_fn = MagicMock()

            # Patch MCPServerFactory to use our mock
            with patch("clickup_mcp.web_server.app.mcp_factory") as mock_mcp_factory:
                mock_mcp_factory.lifespan.return_value = mock_lifespan_fn

                # Patch FastAPI to capture the arguments
                with patch("clickup_mcp.web_server.app.FastAPI") as mock_fastapi:
                    # Call the create method
                    WebServerFactory.create()

                    # Verify FastAPI was created with the correct lifespan
                    mock_fastapi.assert_called_once()
                    kwargs = mock_fastapi.call_args.kwargs
                    assert "lifespan" in kwargs, "lifespan should be included in FastAPI arguments"
                    assert kwargs["lifespan"] is mock_lifespan_fn, "MCP factory's lifespan should be used"

    def test_lifespan_integration_with_mcp_server(self):
        """Test the actual integration between web server and MCP server lifespan."""
        # Create a mock MCP server with a session manager
        mock_mcp = MagicMock()
        mock_session_manager = MagicMock()
        mock_run_context = AsyncMock()
        mock_session_manager.run.return_value = mock_run_context
        mock_mcp.session_manager = mock_session_manager

        # Set up the MCPServerFactory with our mock
        with patch("clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE", mock_mcp):
            # Create the web server (which should get the lifespan from MCP factory)
            web_app = WebServerFactory.create()

            # Get the lifespan function from the web app
            lifespan = web_app.router.lifespan_context

            # Test that the lifespan function exists and is callable
            assert lifespan is not None, "Lifespan should be set on the FastAPI app"
            assert callable(lifespan), "Lifespan should be callable"

    async def test_lifespan_context_manager_behavior(self):
        """Test that the web app's lifespan context manager functions correctly."""
        # Create a mock MCP server with special tracking for the context manager
        mock_mcp = MagicMock()
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

        # Set up MCPServerFactory to return our mock
        with patch("clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE", mock_mcp):
            # Create the web app and get its lifespan context manager
            web_app = WebServerFactory.create()
            lifespan_cm_func = web_app.router.lifespan_context

            # Create the test app (which should be a FastAPI) and get its actual context manager
            mock_app = MagicMock(spec=FastAPI)
            lifespan_cm = lifespan_cm_func(mock_app)

            # Use the context manager
            async with lifespan_cm:
                # Verify session manager's context was entered
                assert context_entered, "Session manager context should be entered when using lifespan"

            # Verify context was exited
            assert context_exited, "Session manager context should be exited after lifespan context"

    def test_web_server_creation_requires_mcp_server_first(self):
        """Test that web server creation properly requires MCP server to be created first."""
        # Don't create an MCP server instance first

        # Trying to create the web server should raise an error with a clear message
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.create()

        # Verify the error message is developer-friendly
        error_message = str(excinfo.value)
        assert "create a FastMCP instance first" in error_message, "Error should guide developer to create MCP server first"
        assert "MCPServerFactory.create()" in error_message, "Error should mention the correct function to call"

    def test_lifespan_parameter_in_create_app_function(self):
        """Test that the create_app function properly passes the lifespan parameter."""
        from clickup_mcp.models.cli import ServerConfig
        from clickup_mcp.web_server.app import create_app

        # First create an MCP server to avoid assertion errors
        with patch("clickup_mcp.mcp_server.app.FastMCP") as mock_fast_mcp:
            mock_mcp_instance = MagicMock()
            mock_session_manager = MagicMock()
            mock_mcp_instance.session_manager = mock_session_manager
            mock_fast_mcp.return_value = mock_mcp_instance
            MCPServerFactory.create()

            # Create a mock lifespan function
            mock_lifespan_fn = MagicMock()

            # Patch MCPServerFactory to use our mock
            with patch("clickup_mcp.web_server.app.mcp_factory") as mock_mcp_factory:
                mock_mcp_factory.lifespan.return_value = mock_lifespan_fn

                # Create the web server first since create_app relies on it
                WebServerFactory.create()

                # Create minimal server config
                server_config = ServerConfig(host="localhost", port=8000)

                # Create the app
                app = create_app(server_config=server_config)

                # Verify the app has a lifespan context that ultimately comes from our mock
                assert hasattr(app.router, "lifespan_context")

    def test_lifespan_error_handling(self):
        """Test that the web server's lifespan properly handles MCP server errors."""
        # Test that errors from the MCP server's session manager are properly handled in the lifespan

        # Create a mock for the MCP server's get method that raises an exception
        with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get") as mock_get:
            # Use the same exception type that the real code would raise
            mock_get.side_effect = Exception("MCP server error")

            # The lifespan function should properly wrap and raise the error
            with pytest.raises(Exception) as excinfo:
                # Call lifespan() which should raise the exception from our mock
                MCPServerFactory.lifespan()

            # Verify the error contains our original error message
            assert "MCP server error" in str(excinfo.value), "Original error message should be preserved"
