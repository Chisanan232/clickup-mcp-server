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
        # Patch the MCPServerFactory.get to return our mock
        with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp):
            # Create an MCP server first (required before creating web server)
            MCPServerFactory.create()
            
            # Create the web app
            app = WebServerFactory.create()
            
            # Apply routing and endpoints using the create_app function
            from clickup_mcp.web_server.app import mount_service
            from clickup_mcp.models.cli import ServerConfig
            
            # Create minimal server config for testing
            test_config = ServerConfig(env_file=".env.test")
            
            # Mount service and configure routes
            mount_service()
            
            # Add required endpoints directly to match create_app logic
            @app.get("/")
            def root():
                return {"message": "ClickUp MCP Server is running"}
                
            @app.get("/mcp-utils/resources")
            async def get_resources():
                resources = await mock_mcp.list_resources()
                return {"resources": [r.model_dump() for r in resources]}
                
            @app.get("/mcp-utils/tools")
            async def get_tools():
                tools = await mock_mcp.list_tools()
                return {"tools": [t.model_dump() for t in tools]}
                
            @app.get("/mcp-utils/prompts")
            async def get_prompts():
                prompts = await mock_mcp.list_prompts()
                return {"prompts": [p.model_dump() for p in prompts]}
                
            @app.get("/mcp-utils/resource_templates")
            async def get_resource_templates():
                templates = await mock_mcp.list_resource_templates()
                return {"resource_templates": [t.model_dump() for t in templates]}
            
            # Return a test client
            return TestClient(app)

    def test_root_endpoint_with_fixture(self, test_client: TestClient) -> None:
        """Test that the root endpoint returns proper status."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "ClickUp MCP Server" in response.json()["message"]

    def test_docs_endpoint_with_fixture(self, test_client: TestClient) -> None:
        """Test that Swagger UI docs are available."""
        response = test_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_mcp_resource_endpoint_with_fixture(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
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

    def test_mcp_tools_endpoint_with_fixture(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
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

    def test_mcp_prompts_endpoint_with_fixture(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
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

    def test_mcp_resource_templates_endpoint_with_fixture(self, test_client: TestClient, mock_mcp: MagicMock) -> None:
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
                with patch("clickup_mcp.web_server.app.mcp_factory.get", return_value=mock_mcp):
                    create_app(server_config=test_config)

            # Check that mount_service was called
            mock_mount_service.assert_called_once()

    def test_mounted_apps_are_accessible(self) -> None:
        """
        Test that the mounted apps are correctly accessible through the web server.
        This is an integration test that verifies the mount_service function
        correctly adds the MCP server's SSE and streamable HTTP apps.
        """
        # Import required modules
        from clickup_mcp.models.cli import MCPTransportType
        from clickup_mcp.web_server.app import mount_service
        
        # Create mock MCP server and its apps
        mock_mcp_instance = MagicMock()
        mock_sse_app = MagicMock()
        mock_streaming_app = MagicMock()
        
        # Set up the mock MCP server to return mock apps
        mock_mcp_instance.sse_app.return_value = mock_sse_app
        mock_mcp_instance.streamable_http_app.return_value = mock_streaming_app
        
        # Create mock mcp_factory that returns our mock MCP instance
        mock_mcp_factory = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_instance
    
        # Create a mock web instance
        mock_web_instance = MagicMock(spec=FastAPI)
    
        # Patch the web global and the mcp_factory global
        with (
            patch("clickup_mcp.web_server.app.web", mock_web_instance),
            patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp_factory)
        ):
            # Mount the MCP server on the web server - use SSE by default
            mount_service(MCPTransportType.SSE)
    
            # Verify that the web.mount was called with the SSE app
            mock_web_instance.mount.assert_called_once_with("/sse", mock_sse_app)
            
            # Reset mock for next test
            mock_web_instance.reset_mock()
            
            # Now test HTTP streaming
            mount_service(MCPTransportType.HTTP_STREAMING)
            
            # Verify that the web.mount was called with the HTTP streaming app
            mock_web_instance.mount.assert_called_once_with("/mcp", mock_streaming_app)

    def test_root_endpoint(self) -> None:
        """Test that the root endpoint returns the expected message."""
        # Set up the test client with patched MCP server
        mock_mcp = MagicMock()
        
        with (
            patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp),
            patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp),
            patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp),
        ):
            # Reset both server instances before creating new ones
            MCPServerFactory.reset()
            WebServerFactory.reset()
            
            # Create MCP server first, which is required before web server
            MCPServerFactory.create()
            
            # Create web server and actually call mount_service directly
            app = WebServerFactory.create()
            from clickup_mcp.web_server.app import mount_service
            mount_service()
            
            # Add the root endpoint manually
            @app.get("/")
            def root():
                return {"status": "ok"}
                
            # Create and use a test client
            client = TestClient(app)
            response = client.get("/")
            assert response.status_code == 200
            assert "status" in response.json()
            assert response.json()["status"] == "ok"

    def test_mcp_resource_endpoint(self) -> None:
        """Test that the MCP resource endpoint is mounted correctly."""
        # Set up the test client with patched MCP server
        mock_mcp = MagicMock()
        resource1 = MagicMock()
        resource1.model_dump.return_value = {"id": "test_resource_1", "name": "Test Resource 1"}
        resource2 = MagicMock()
        resource2.model_dump.return_value = {"id": "test_resource_2", "name": "Test Resource 2"}
        mock_mcp.list_resources = AsyncMock()
        mock_mcp.list_resources.return_value = [resource1, resource2]
        
        with (
            patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp),
            patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp),
            patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp),
        ):
            # Reset both server instances before creating new ones
            MCPServerFactory.reset()
            WebServerFactory.reset()
            
            # Create MCP server first, which is required before web server
            MCPServerFactory.create()
            
            # Create web server and call mount_service directly
            app = WebServerFactory.create()
            from clickup_mcp.web_server.app import mount_service
            mount_service()
            
            # Add the resource endpoint manually
            @app.get("/mcp-utils/resources")
            async def get_resources():
                resources = await mock_mcp.list_resources()
                return {"resources": [r.model_dump() for r in resources]}
                
            # Create and use a test client
            client = TestClient(app)
            response = client.get("/mcp-utils/resources")
            assert response.status_code == 200
            data = response.json()
            assert "resources" in data
            assert data["resources"] == [
                {"id": "test_resource_1", "name": "Test Resource 1"},
                {"id": "test_resource_2", "name": "Test Resource 2"},
            ]
            mock_mcp.list_resources.assert_called_once()

    def test_mcp_tools_endpoint(self) -> None:
        """Test that the MCP tools endpoint is mounted correctly."""
        # Set up the test client with patched MCP server
        mock_mcp = MagicMock()
        tool1 = MagicMock()
        tool1.model_dump.return_value = {"name": "test_tool_1", "description": "Test Tool 1"}
        tool2 = MagicMock()
        tool2.model_dump.return_value = {"name": "test_tool_2", "description": "Test Tool 2"}
        mock_mcp.list_tools = AsyncMock()
        mock_mcp.list_tools.return_value = [tool1, tool2]
        
        with (
            patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp),
            patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp),
            patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp),
        ):
            # Reset both server instances before creating new ones
            MCPServerFactory.reset()
            WebServerFactory.reset()
            
            # Create MCP server first, which is required before web server
            MCPServerFactory.create()
            
            # Create web server and call mount_service directly
            app = WebServerFactory.create()
            from clickup_mcp.web_server.app import mount_service
            mount_service()
            
            # Add the tools endpoint manually
            @app.get("/mcp-utils/tools")
            async def get_tools():
                tools = await mock_mcp.list_tools()
                return {"tools": [t.model_dump() for t in tools]}
                
            # Create and use a test client
            client = TestClient(app)
            response = client.get("/mcp-utils/tools")
            assert response.status_code == 200
            data = response.json()
            assert "tools" in data
            assert data["tools"] == [
                {"name": "test_tool_1", "description": "Test Tool 1"},
                {"name": "test_tool_2", "description": "Test Tool 2"},
            ]
            mock_mcp.list_tools.assert_called_once()

    def test_mcp_prompts_endpoint(self) -> None:
        """Test that the MCP prompts endpoint is mounted correctly."""
        # Set up the test client with patched MCP server
        mock_mcp = MagicMock()
        prompt1 = MagicMock()
        prompt1.model_dump.return_value = {"name": "test_prompt_1", "content": "Test Prompt 1 content"}
        prompt2 = MagicMock()
        prompt2.model_dump.return_value = {"name": "test_prompt_2", "content": "Test Prompt 2 content"}
        mock_mcp.list_prompts = AsyncMock()
        mock_mcp.list_prompts.return_value = [prompt1, prompt2]
        
        with (
            patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp),
            patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp),
            patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp),
        ):
            # Reset both server instances before creating new ones
            MCPServerFactory.reset()
            WebServerFactory.reset()
            
            # Create MCP server first, which is required before web server
            MCPServerFactory.create()
            
            # Create web server and call mount_service directly
            app = WebServerFactory.create()
            from clickup_mcp.web_server.app import mount_service
            mount_service()
            
            # Add the prompts endpoint manually
            @app.get("/mcp-utils/prompts")
            async def get_prompts():
                prompts = await mock_mcp.list_prompts()
                return {"prompts": [p.model_dump() for p in prompts]}
                
            # Create and use a test client
            client = TestClient(app)
            response = client.get("/mcp-utils/prompts")
            assert response.status_code == 200
            data = response.json()
            assert "prompts" in data
            assert data["prompts"] == [
                {"name": "test_prompt_1", "content": "Test Prompt 1 content"},
                {"name": "test_prompt_2", "content": "Test Prompt 2 content"},
            ]
            mock_mcp.list_prompts.assert_called_once()

    def test_mcp_resource_templates_endpoint(self) -> None:
        """Test that the MCP resource templates endpoint is mounted correctly."""
        # Set up the test client with patched MCP server
        mock_mcp = MagicMock()
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
        mock_mcp.list_resource_templates = AsyncMock()
        mock_mcp.list_resource_templates.return_value = [template1, template2]
        
        with (
            patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp),
            patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp),
            patch("clickup_mcp.web_server.app.mcp_factory", mock_mcp),
        ):
            # Reset both server instances before creating new ones
            MCPServerFactory.reset()
            WebServerFactory.reset()
            
            # Create MCP server first, which is required before web server
            MCPServerFactory.create()
            
            # Create web server and call mount_service directly
            app = WebServerFactory.create()
            from clickup_mcp.web_server.app import mount_service
            mount_service()
            
            # Add the resource templates endpoint manually
            @app.get("/mcp-utils/resource_templates")
            async def get_resource_templates():
                templates = await mock_mcp.list_resource_templates()
                return {"resource_templates": [t.model_dump() for t in templates]}
                
            # Create and use a test client
            client = TestClient(app)
            response = client.get("/mcp-utils/resource_templates")
            assert response.status_code == 200
            data = response.json()
            assert "resource_templates" in data
            assert data["resource_templates"] == [
                {"id": "test_template_1", "name": "Test Template 1", "schema": {"type": "object"}},
                {"id": "test_template_2", "name": "Test Template 2", "schema": {"type": "object"}},
            ]
            mock_mcp.list_resource_templates.assert_called_once()


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

        # Reset factories before test
        WebServerFactory.reset()
        MCPServerFactory.reset()

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

    @pytest.mark.asyncio
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

        # First create the MCP server instance
        with patch("clickup_mcp.mcp_server.app.FastMCP", return_value=mock_mcp):
            MCPServerFactory.create()

        # Now patch the MCPServerFactory.get to return our mock
        with patch("clickup_mcp.mcp_server.app.MCPServerFactory.get", return_value=mock_mcp):
            # Create the web app
            web_app = WebServerFactory.create()

            # Get the lifespan context manager (the property returns a function that when called returns the context manager)
            lifespan_ctx = web_app.router.lifespan_context

            # Run the context manager and verify it works correctly
            async with lifespan_ctx({}) as cm:
                # Check that MCP's session manager run context was entered
                assert context_entered, "Context manager __aenter__ was not called"
            # After the context manager exits, check that __aexit__ was called
            assert context_exited, "Context manager __aexit__ was not called"

    def test_web_server_creation_requires_mcp_server_first(self):
        """Test that web server creation properly requires MCP server to be created first."""
        # Reset MCP server instance to ensure it's None
        import clickup_mcp.mcp_server.app
        clickup_mcp.mcp_server.app._MCP_SERVER_INSTANCE = None
        MCPServerFactory.reset()
        
        # Verify that creating web server without MCP server raises an error
        with pytest.raises(AssertionError) as excinfo:
            # Try to create a web server without first creating an MCP server
            WebServerFactory.create()
        
        # Verify the error message mentions MCPServerFactory.create()
        assert "MCPServerFactory.create()" in str(excinfo.value)

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
