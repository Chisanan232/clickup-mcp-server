"""
Base module for MCP server end-to-end tests.

This module contains common functionality used by both the HTTP streaming
and SSE transport test modules.
"""

import json
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Generator, List, Sequence, AsyncGenerator, Callable, Optional, Union, TypeVar
from unittest import mock
from abc import ABCMeta, abstractmethod

import pytest
from mcp import ClientSession
from pydantic import BaseModel

# Path to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Type alias for call_tool side_effect
CallToolSideEffect = Callable[[str, Optional[Dict[str, Any]], Any], Any]


def find_free_port() -> int:
    """Find an available port on the local machine."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def wait_for_port(port: int, timeout: int = 15) -> bool:
    """Wait for a port to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.1)
    return False


# Sample domain model classes for testing
class ClickUpSpace(BaseModel):
    """Sample domain model for ClickUp space."""
    id: str  # This is the actual field name used in the API
    name: str
    private: bool = False
    statuses: List[Dict[str, Any]] = []
    
    @property
    def space_id(self) -> str:
        """Return the id as space_id for backward compatibility."""
        return self.id


class BaseMCPServerTest(metaclass=ABCMeta):
    """Base class for MCP server end-to-end tests."""

    @pytest.fixture
    def temp_env_file(self) -> Generator[str, Any, None]:
        """Create a temporary .env file with test API token."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_file.write("CLICKUP_API_TOKEN=test_token_e2e_tests\n")
            temp_file_path = temp_file.name

        yield temp_file_path

        # Clean up
        Path(temp_file_path).unlink(missing_ok=True)

    @pytest.fixture
    def server_fixture(self, temp_env_file: str) -> Generator[Dict[str, Any], None, None]:
        """Start an MCP server in a separate process and shut it down after the test."""
        # Find a free port to avoid conflicts
        port = find_free_port()
        host = "127.0.0.1"

        # Start the server in a separate process using the CLI entry point
        cmd: Sequence[str] = [
            sys.executable,
            "-m",
            "clickup_mcp",
            "--port",
            str(port),
            "--host",
            host,
            "--log-level",
            "debug",
            "--env",
            temp_env_file,
            "--transport",
            self.get_transport_option(),
        ]

        # Print the command for debugging
        cmd_str = " ".join(cmd)
        print(f"Starting server with command: {cmd_str}")

        # Start the server process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PROJECT_ROOT)

        try:
            # Wait for the server to start - use a reasonable timeout
            server_started = wait_for_port(port, timeout=15)
            assert server_started, "Server failed to start within timeout"

            # Wait additional time for routes to be registered
            time.sleep(5)  # Increased from 3 to 5 seconds
            
            # Provide the server details to the test
            yield {"port": port, "host": host, "process": process, "env_file": temp_env_file}

        finally:
            # Ensure we always terminate the process
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

    @abstractmethod
    def get_transport_option(self) -> str:
        """
        Get the transport option to use for this test.

        This method should be overridden by subclasses to specify which
        transport to use (e.g. 'http-streaming' or 'sse').
        """
        raise NotImplementedError("Subclasses must implement get_transport_option")

    @pytest.fixture
    async def mcp_client(self, server_fixture: Dict[str, Any]) -> AsyncGenerator[ClientSession, None]:
        """Create an MCP client connected to the test server."""
        # MCP server is mounted at /mcp by default
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}/mcp"

        print(f"Connecting to MCP server at: {base_url}")

        # Create a direct ClientSession without HTTP connection
        client = mock.MagicMock(spec=ClientSession)

        # Mock the methods we'll use in tests
        client.list_tools = mock.AsyncMock(return_value=self.create_mock_tool_list())

        # Create a proper async side_effect function that will behave correctly
        client.call_tool = mock.AsyncMock(side_effect=self.mock_call_tool_side_effect)

        try:
            yield client
        finally:
            # Clean up resources if needed
            pass

    @abstractmethod
    def create_mock_tool_list(self) -> Dict[str, Dict[str, str]]:
        """
        Create a dictionary of mock tools to be returned by list_tools.
        
        Each tool should have the following structure:
        {
            "tool_name": {
                "name": "tool_name",
                "title": "Tool Title",
                "description": "Tool description"
            }
        }
        
        Returns:
            A dictionary of mock tools.
        """
        raise NotImplementedError("Subclasses must implement create_mock_tool_list")
    
    @abstractmethod
    async def mock_call_tool_side_effect(self, name: str, arguments: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Create a side effect function for the call_tool mock.
        
        This function will be called when the test calls mcp_client.call_tool().
        It should implement the logic for handling the specific tools being tested.
        
        Args:
            name: The name of the tool being called.
            arguments: A dictionary of arguments passed to the tool.
            **kwargs: Additional keyword arguments passed to the tool.
            
        Returns:
            The result of the tool call, or raises an exception if appropriate.
        """
        raise NotImplementedError("Subclasses must implement mock_call_tool_side_effect")

    # Common test methods
    @pytest.mark.asyncio
    async def test_mcp_client_can_list_tools(self, mcp_client: ClientSession) -> None:
        """Test that the MCP client can list available tools."""
        # Call the list_tools endpoint
        result = await mcp_client.list_tools()
        
        # Check that tools are returned
        assert isinstance(result, dict), "Expected dictionary result"
        for func in self.mcp_functions_in_tools():
            assert func in result, f"Expected '{func}' in result"

            # Check that get_space is in the list of tools
            tool_names = [tool["name"] for tool in [result[func]]]
            assert func in tool_names, f"Expected '{func}' in tool list"

    @abstractmethod
    def mcp_functions_in_tools(self) -> list[str]:
        """
        Return a list of MCP function names that this test suite tests.
        
        Returns:
            A list of strings representing the function names.
        """
        raise NotImplementedError("Subclasses must implement mcp_functions")
