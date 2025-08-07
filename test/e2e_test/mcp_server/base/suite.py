"""
Test suite base classes for MCP server end-to-end tests.

This module provides the foundation for running end-to-end tests against
MCP server endpoints with different transport types.
"""

import os
import select
import subprocess
import sys
import tempfile
import time
import socket
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator, Any, Sequence, Type, Optional, cast

import pytest
from abc import ABCMeta, ABC
from dotenv import load_dotenv
from mcp import ClientSession

from .client import SSEClient, StreamingHTTPClient, EndpointClient

# Load any .env file in current directory if present
load_dotenv()

# Path to the project root
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent

# Maximum time to wait for server to start (seconds)
SERVER_START_TIMEOUT: int = 3

# Additional time to wait for routes to be registered (seconds)
ROUTES_REGISTRATION_TIME: float = 2.0

# Timeout for operations (seconds)
OPERATION_TIMEOUT: float = 5.0

# Free port detected for server use
_FREE_PORT: int | None = None


def find_free_port() -> int:
    """
    Find an available port on the local machine.

    Returns:
        An available port number
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        global _FREE_PORT
        _FREE_PORT = s.getsockname()[1]
        return _FREE_PORT


@dataclass
class MCPClientParameterValue:
    """
    Data object for fixture parameters.

    Attributes:
        client: The client class to instantiate for testing
        url_suffix: The URL suffix for connecting to the MCP server
        transport: The transport option for MCP server command line
    """
    client: Type[EndpointClient]
    url_suffix: str
    transport: str


@dataclass
class MCPClientFixtureValue:
    """
    Data object returned by the client fixture.

    Attributes:
        client: The instantiated client object for testing
        url_suffix: The URL suffix for connecting to the MCP server
        transport: The transport option for MCP server command line
    """
    client: EndpointClient
    url_suffix: str
    transport: str


class MCPClientFixture(metaclass=ABCMeta):
    """
    Base fixture class for MCP client testing.
    
    This class provides a client fixture that can be parameterized to test
    with different transport types (SSE and HTTP streaming).
    """

    @pytest.fixture(
        params=[
            MCPClientParameterValue(client=SSEClient, url_suffix="/sse/sse", transport="sse"),
            MCPClientParameterValue(client=StreamingHTTPClient, url_suffix="/mcp/mcp", transport="http-streaming"),
        ],
        ids=["sse", "streaming-http"],
    )
    async def client(self, request: pytest.FixtureRequest) -> AsyncGenerator[MCPClientFixtureValue, None]:
        """
        Provide a client instance for MCP server testing.
        
        This fixture creates an instance of either SSEClient or StreamingHTTPClient,
        connects it to the MCP server, and yields a fixture value containing the client
        and its transport information.
        
        Args:
            request: The pytest fixture request
            
        Yields:
            MCPClientFixtureValue containing the client and transport information
        """
        cls: MCPClientParameterValue = request.param
        mcp_server_url = f"http://localhost:{_FREE_PORT}{cls.url_suffix}"
        c = cls.client(url=mcp_server_url)
        await c.connect()
        yield MCPClientFixtureValue(client=c, url_suffix=cls.url_suffix, transport=cls.transport)
        await c.close()


def is_port_in_use(port: int) -> bool:
    """
    Check if a port is in use.
    
    Args:
        port: The port number to check
        
    Returns:
        True if the port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def wait_for_port(port: int, timeout: int = SERVER_START_TIMEOUT) -> bool:
    """
    Wait for a port to become available.
    
    Args:
        port: The port number to wait for
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if the port became available, False if timed out
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.1)
    return False


class BaseMCPServerFunctionTest(MCPClientFixture, ABC):
    """Base class for MCP server end-to-end tests."""

    @pytest.fixture
    def temp_env_file(self) -> Generator[str, None, None]:
        """
        Create a temporary .env file with test API token.
        
        Yields:
            Path to the temporary .env file
            
        Skips the test if the CLICKUP_API_TOKEN environment variable is not set.
        """
        # Get API token from environment
        api_token = os.environ.get("CLICKUP_API_TOKEN")
        if not api_token:
            pytest.skip("CLICKUP_API_TOKEN environment variable is required for this test")

        # Create a temporary file with the token
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_file.write(f"CLICKUP_API_TOKEN={api_token}\n")
            temp_file_path = temp_file.name

        yield temp_file_path

        # Clean up
        Path(temp_file_path).unlink(missing_ok=True)

    @pytest.fixture
    def server_fixture(self, temp_env_file: str, client: MCPClientFixtureValue) -> Generator[Dict[str, Any], None, None]:
        """
        Start an MCP server in a separate process and shut it down after the test.
        
        Args:
            temp_env_file: Path to the temporary .env file
            client: Client fixture value containing transport information
            
        Yields:
            Dictionary containing server details (port, host, process, env_file)
            
        Raises:
            pytest.fail: If the server fails to start or terminates prematurely
        """
        # Find a free port to avoid conflicts
        port = find_free_port()
        host = "127.0.0.1"
        process = None

        try:
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
                "debug",  # Ensure debug logging is enabled
                "--env",
                temp_env_file,
                "--transport",
                client.transport,
            ]

            print(f"[DEBUG] Starting server with command: {' '.join(cmd)}")
            print(f"[DEBUG] Transport type: {client.transport}")

            # Start the server process with non-blocking I/O
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=PROJECT_ROOT,
                text=True,
                bufsize=1,
            )

            # Wait for the server to start
            server_started = wait_for_port(port)
            if not server_started:
                if process.poll() is not None:
                    # Process has terminated prematurely
                    stdout, stderr = process.communicate(timeout=1)
                    error_msg = f"Server process terminated with exit code {process.returncode}\n"
                    error_msg += f"STDOUT: {stdout}\n"
                    error_msg += f"STDERR: {stderr}"
                    pytest.fail(error_msg)
                else:
                    pytest.fail(f"Server failed to start within {SERVER_START_TIMEOUT} seconds")

            # Small additional delay to ensure routes are registered
            time.sleep(ROUTES_REGISTRATION_TIME)

            print(f"[DEBUG] Server started successfully at http://{host}:{port}")

            # Capture initial server output for debugging
            if process.stdout and process.stderr:
                # Use select to read without blocking
                stdout_data, stderr_data = "", ""
                readable_streams, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)

                if process.stdout in readable_streams:
                    stdout_data = process.stdout.readline()
                if process.stderr in readable_streams:
                    stderr_data = process.stderr.readline()

                if stdout_data:
                    print(f"[SERVER STDOUT] {stdout_data}")
                if stderr_data:
                    print(f"[SERVER STDERR] {stderr_data}")

            # Provide the server details to the test
            yield {"port": port, "host": host, "process": process, "env_file": temp_env_file}

        finally:
            # Ensure we always terminate the process
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        pass  # We've tried our best to kill it
