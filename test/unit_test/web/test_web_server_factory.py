"""
Unit tests for the WebServerFactory.

This module tests the factory pattern for creating and managing the Web server instance.
"""

import pytest
from unittest.mock import patch, MagicMock

from fastapi import FastAPI
from clickup_mcp.web_server.app import WebServerFactory


class TestWebServerFactory:
    """Test suite for the WebServerFactory class."""
    
    @pytest.fixture(autouse=True)
    def reset_web_server(self):
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
    
    def test_create_web_server(self):
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
                version="0.1.0"
            )
            
            # Verify CORS middleware was added
            mock_instance.add_middleware.assert_called_once()
            
            # Verify the returned instance is the mock
            assert server is mock_instance
            
            # Verify the global instance is set
            import clickup_mcp.web_server.app as app_module
            assert app_module._WEB_SERVER_INSTANCE is mock_instance
    
    def test_get_web_server(self):
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
    
    def test_create_fails_when_already_created(self):
        """Test that creating a server when one already exists raises an error."""
        # Create a server first
        WebServerFactory.create()
        
        # Attempting to create again should raise an AssertionError
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.create()
        
        assert "not allowed to create more than one instance" in str(excinfo.value)
    
    def test_get_fails_when_not_created(self):
        """Test that getting a server before creating one raises an error."""
        # Attempting to get before creating should raise an AssertionError
        with pytest.raises(AssertionError) as excinfo:
            WebServerFactory.get()
        
        assert "must be created web server first" in str(excinfo.value)
    
    def test_backward_compatibility_global_web(self):
        """Test that the global web variable exists and is a FastAPI instance."""
        # We need to test that the module-level 'web' variable exists and is a FastAPI instance
        import clickup_mcp.web_server.app
        
        # Verify the module has a global 'web' variable
        assert hasattr(clickup_mcp.web_server.app, 'web')
        
        # Reset the web server instance to make sure we're testing the module's instance
        # We need to temporarily store the 'web' instance before resetting _WEB_SERVER_INSTANCE
        web_instance = clickup_mcp.web_server.app.web
        
        # Verify it has the expected type
        assert isinstance(web_instance, FastAPI) or web_instance.__class__.__name__ == 'FastAPI'
        
        # For the backward compatibility test, we need to make sure the module's 'web'
        # instance is what's returned by get()
        clickup_mcp.web_server.app._WEB_SERVER_INSTANCE = web_instance
        assert WebServerFactory.get() is web_instance
