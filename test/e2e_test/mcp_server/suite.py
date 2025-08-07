import os
import select
import subprocess
import sys
import tempfile
import time
import socket
import time
import asyncio
from contextlib import closing, asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from abc import abstractmethod, ABCMeta
from pathlib import Path
from typing import Type, AsyncGenerator, Generator, Dict, Any, Sequence

import pytest
from dotenv import load_dotenv
from mcp import ClientSession

from .base.client import SSEClient, StreamingHTTPClient, EndpointClient

# Load any .env file in current directory if present
load_dotenv()


class MCPClientFixture(metaclass=ABCMeta):
    @pytest.fixture
    def mcp_server_url(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @pytest.fixture(params=[SSEClient, StreamingHTTPClient], ids=["sse", "streaming-http"])
    async def client(self, request: pytest.FixtureRequest, mcp_server_url: str) -> AsyncGenerator[EndpointClient, None]:
        cls: Type[EndpointClient] = request.param
        c = cls(url=mcp_server_url)
        await c.connect()
        yield c
        await c.close()


# Path to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Maximum time to wait for server to start (seconds)
SERVER_START_TIMEOUT = 3

# Additional time to wait for routes to be registered (seconds)
ROUTES_REGISTRATION_TIME = 2

# Timeout for operations (seconds)
OPERATION_TIMEOUT = 5.0


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


def wait_for_port(port: int, timeout: int = SERVER_START_TIMEOUT) -> bool:
    """Wait for a port to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.1)
    return False


class BaseMCPServerFunctionTest(metaclass=ABCMeta):
    """Base class for MCP server end-to-end tests."""

    @pytest.fixture
    def temp_env_file(self) -> Generator[str, None, None]:
        """Create a temporary .env file with test API token."""
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
    def server_fixture(self, temp_env_file: str) -> Generator[Dict[str, Any], None, None]:
        """Start an MCP server in a separate process and shut it down after the test."""
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
                self.get_transport_option(),
            ]

            print(f"[DEBUG] Starting server with command: {' '.join(cmd)}")
            print(f"[DEBUG] Transport type: {self.get_transport_option()}")

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

    @abstractmethod
    def get_transport_option(self) -> str:
        """
        Get the transport option to use for this test.

        This method should be overridden by subclasses to specify which
        transport to use (e.g. 'http-streaming' or 'sse').
        """
        raise NotImplementedError("Subclasses must implement get_transport_option")

    @pytest.fixture
    def mcp_server_url(self, server_fixture: Dict[str, Any]) -> str:
        return f"http://{server_fixture['host']}:{server_fixture['port']}"
