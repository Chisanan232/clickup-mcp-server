"""
Tests for the server type CLI option.
"""

import pytest
from unittest.mock import MagicMock, patch

from clickup_mcp.entry import parse_args
from clickup_mcp.models.cli import MCPServerType, ServerConfig
from clickup_mcp.web_server.app import create_app, mount_service


class TestCliServerTypeOption:
    """Test cases for server type CLI option."""

    def test_server_type_enum(self):
        """Test that the ServerType enum has expected values."""
        assert MCPServerType.SSE.value == "sse"
        assert MCPServerType.HTTP_STREAMING.value == "http-streaming"
        assert not hasattr(MCPServerType, "BOTH")

    def test_default_server_type(self):
        """Test that the default server type is 'sse'."""
        with patch("sys.argv", ["program"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.SSE.value

    def test_sse_server_type(self):
        """Test that '--server-type sse' sets server_type to SSE."""
        with patch("sys.argv", ["program", "--server-type", "sse"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.SSE.value

    def test_http_streaming_server_type(self):
        """Test that '--server-type http-streaming' sets server_type to HTTP_STREAMING."""
        with patch("sys.argv", ["program", "--server-type", "http-streaming"]):
            config = parse_args()
            assert config.mcp_server_type == MCPServerType.HTTP_STREAMING.value

    def test_invalid_server_type(self):
        """Test that an invalid server type raises a system exit."""
        with patch("sys.argv", ["program", "--server-type", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_mount_service_sse_only(self):
        """Test that only SSE endpoints are mounted when server_type is SSE."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_web = MagicMock()
        
        # Test direct mount_service function
        with patch("clickup_mcp.web_server.app.web", mock_web):
            mount_service(mock_mcp_server, MCPServerType.SSE.value)
                
        # Verify that only SSE endpoint was mounted
        mock_mcp_server.sse_app.assert_called_once()
        mock_mcp_server.streamable_http_app.assert_not_called()
        assert mock_web.mount.call_count == 1
        mock_web.mount.assert_called_with("/mcp", mock_mcp_server.sse_app.return_value)

    def test_mount_service_http_streaming_only(self):
        """Test that only HTTP_STREAMING endpoints are mounted when server_type is HTTP_STREAMING."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_web = MagicMock()
        
        # Test direct mount_service function
        with patch("clickup_mcp.web_server.app.web", mock_web):
            mount_service(mock_mcp_server, MCPServerType.HTTP_STREAMING.value)
                
        # Verify that only HTTP_STREAMING endpoint was mounted
        mock_mcp_server.sse_app.assert_not_called()
        mock_mcp_server.streamable_http_app.assert_called_once()
        assert mock_web.mount.call_count == 1
        mock_web.mount.assert_called_with("/mcp", mock_mcp_server.streamable_http_app.return_value)

    @patch("clickup_mcp.mcp_server.app.MCPServerFactory.get")
    def test_create_app_with_sse_server_type(self, mock_mcp_factory, monkeypatch):
        """Test create_app with SSE server type config."""
        # Setup
        mock_mcp_server = MagicMock()
        mock_mcp_factory.return_value = mock_mcp_server
        mock_web = MagicMock()
        
        # Set up API token in environment
        monkeypatch.setenv("CLICKUP_API_TOKEN", "test_token_for_server_type")
        
        # Create a ServerConfig with SSE server type
        config = ServerConfig(mcp_server_type=MCPServerType.SSE.value)
        
        with patch("clickup_mcp.web_server.app.WebServerFactory.get", return_value=mock_web):
            with patch("clickup_mcp.web_server.app.mount_service") as mock_mount:
                # Reset client factory to ensure it will create a new instance with our token
                from clickup_mcp.client import ClickUpAPIClientFactory
                ClickUpAPIClientFactory.reset()
                
                create_app(config)
                mock_mount.assert_called_once_with(mock_mcp_server, MCPServerType.SSE.value)
