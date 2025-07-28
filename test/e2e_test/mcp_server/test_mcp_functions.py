"""
End-to-end tests for MCP functions using the HTTP streaming transport.

This module tests the MCP functions by connecting to a running
MCP server instance using the HTTP streaming transport.
"""

import json
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Generator, List, Sequence, AsyncGenerator, cast
from unittest import mock

import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import BaseModel
from test.e2e_test.mcp_server.base_test import BaseMCPServerTest


# Sample domain model classes for testing
class ClickUpSpace(BaseModel):
    """Sample domain model for ClickUp space."""
    id: str  # This is the actual field name used in the API
    name: str
    private: bool = False
    statuses: List[Dict[str, Any]] = []
    
    # For backward compatibility
    @property
    def space_id(self) -> str:
        """Return the id as space_id for backward compatibility."""
        return self.id


class TestMCPFunctions(BaseMCPServerTest):
    """End-to-end tests for MCP functions using the HTTP streaming transport."""

    def get_transport_option(self) -> str:
        """Return the HTTP streaming transport option."""
        return "http-streaming"

    def mcp_functions(self) -> list[str]:
        return ["get_space"]

    @pytest.mark.asyncio
    async def test_get_space_with_invalid_id(self, mcp_client: ClientSession) -> None:
        """Test that get_space returns None for an invalid space ID."""
        # Call the MCP function with an invalid space ID
        result = await mcp_client.call_tool("get_space", {"space_id": "invalid_id"})
        
        # Should return None for invalid space ID
        assert result is None, "Expected None for invalid space ID"

    @pytest.mark.asyncio
    async def test_get_space_with_empty_id(self, mcp_client: ClientSession) -> None:
        """Test that get_space raises an error for an empty space ID."""
        # Call the MCP function with an empty space ID
        with pytest.raises(ValueError) as exc_info:
            await mcp_client.call_tool("get_space", {"space_id": ""})
        
        # Check the error message
        assert "Space ID is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_space_with_mocked_response(self, mcp_client: ClientSession) -> None:
        """Test get_space with a mocked response."""
        # Call the MCP function with a valid space ID that our mock will handle
        result = await mcp_client.call_tool("get_space", {"space_id": "123456"})
        
        # Check the response matches our mock
        assert result is not None
        assert result["id"] == "123456"
        assert result["name"] == "Test Space"

    @pytest.mark.asyncio
    async def test_get_space_error_handling(self, mcp_client: ClientSession) -> None:
        """Test that get_space properly handles and reports errors."""
        # This will hit our error case in the mock's side_effect
        with pytest.raises(ValueError) as exc_info:
            await mcp_client.call_tool("get_space", {"space_id": "error_case"})
        
        # Should include the error message from the mock
        assert "Error retrieving space" in str(exc_info.value)
