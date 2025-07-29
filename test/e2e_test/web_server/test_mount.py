"""
End-to-end tests for MCP server API path mounting.

This module tests whether the MCP server endpoints are correctly mounted
and accessible at the expected API paths.
"""

import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Generator, Any

import httpx
import pytest
from dotenv import load_dotenv

from clickup_mcp.models.cli import MCPTransportType

# Load any .env file in current directory if present
load_dotenv()

# Path to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Maximum time to wait for server to start (seconds)
SERVER_START_TIMEOUT = 10

# Additional time to wait for routes to be registered (seconds)
ROUTES_REGISTRATION_TIME = 2

# Operation timeout (seconds)
OPERATION_TIMEOUT = 10.0


def find_free_port() -> int:
    """Find an available port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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


@pytest.fixture
def temp_env_file() -> Generator[str, None, None]:
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
def server_fixture(temp_env_file: str, request) -> Generator[Dict[str, Any], None, None]:
    """Start an MCP server in a separate process and shut it down after the test."""
    # Get transport type from the test parameter or fixture
    transport_type = request.param if hasattr(request, "param") else "http-streaming"
    
    # Find a free port to avoid conflicts
    port = find_free_port()
    host = "127.0.0.1"
    process = None

    try:
        # Start the server in a separate process using the CLI entry point
        cmd = [
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
            transport_type,
        ]

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

        # Provide the server details to the test
        yield {"port": port, "host": host, "process": process, "transport": transport_type}

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


# Test HTTP Streaming Transport

@pytest.mark.parametrize("server_fixture", [MCPTransportType.HTTP_STREAMING], indirect=True)
def test_http_streaming_mcp_endpoint(server_fixture: Dict[str, Any]) -> None:
    """Test if the MCP server endpoint is correctly mounted for HTTP streaming transport."""
    base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"
    mcp_url = f"{base_url}/mcp"
    
    # Simply check if the endpoint exists - we'll get a non-(307,404) if it's mounted but parameters are missing
    with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
        response = client.post(mcp_url)
    
    # If the endpoint is mounted, we should get a non-(307,404) status
    # If the endpoint is not mounted, we would get a 404 Not Found
    # TODO: Need to adjust the test criteria here
    assert response.status_code not in (307, 404), f"Expected status non-(307,404) for /mcp, got {response.status_code}"
    
    # Verify response contains parameter validation errors, indicating the endpoint exists
    if response.status_code == 200:
        json_response = response.json()
        assert "detail" in json_response, "Missing detail field in response"
        assert isinstance(json_response["detail"], list), "Detail field should be a list of validation errors"


@pytest.mark.parametrize("server_fixture", [MCPTransportType.HTTP_STREAMING], indirect=True)
def test_http_streaming_tools_endpoint(server_fixture: Dict[str, Any]) -> None:
    """Test if the MCP utils tools endpoint is correctly mounted."""
    base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"
    tools_url = f"{base_url}/mcp-utils/tools"
    
    with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
        response = client.get(tools_url)
    
    assert response.status_code == 200, f"Expected status 200 for /mcp-utils/tools, got {response.status_code}"
    
    # Verify response structure
    json_response = response.json()
    assert "tools" in json_response, "Missing tools field in response"
    assert isinstance(json_response["tools"], list), "Tools field should be a list"


# Test SSE Transport

@pytest.mark.parametrize("server_fixture", [MCPTransportType.SSE], indirect=True)
def test_sse_mcp_endpoint(server_fixture: Dict[str, Any]) -> None:
    """Test if the MCP server endpoint is correctly mounted for SSE transport."""
    base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"
    mcp_url = f"{base_url}/sse"  # SSE endpoint is now mounted at '/sse'
    
    # Simply check if the endpoint exists - we'll get a 422 if it's mounted but parameters are missing
    with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
        response = client.post(mcp_url)
    
    # If the endpoint is mounted, we should get a 422 Unprocessable Entity (missing required parameters)
    # If the endpoint is not mounted, we would get a 404 Not Found
    assert response.status_code == 422, f"Expected status 422 for /sse, got {response.status_code}"
    
    # Verify response contains parameter validation errors, indicating the endpoint exists
    json_response = response.json()
    assert "detail" in json_response, "Missing detail field in response"
    assert isinstance(json_response["detail"], list), "Detail field should be a list of validation errors"


@pytest.mark.parametrize("server_fixture", [MCPTransportType.SSE], indirect=True)
def test_sse_tools_endpoint(server_fixture: Dict[str, Any]) -> None:
    """Test if the MCP utils tools endpoint is correctly mounted with SSE transport."""
    base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"
    tools_url = f"{base_url}/mcp-utils/tools"
    
    with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
        response = client.get(tools_url)
    
    assert response.status_code == 200, f"Expected status 200 for /mcp-utils/tools, got {response.status_code}"
    
    # Verify response structure
    json_response = response.json()
    assert "tools" in json_response, "Missing tools field in response"
    assert isinstance(json_response["tools"], list), "Tools field should be a list"


# Test Common Endpoints (regardless of transport)

@pytest.mark.parametrize("server_fixture", [MCPTransportType.HTTP_STREAMING], indirect=True)
@pytest.mark.parametrize(
    "endpoint",
    [
        "/",  # Root health check
        "/mcp-utils/resources",  # Resources endpoint
        "/mcp-utils/prompts",  # Prompts endpoint
        "/mcp-utils/resource_templates",  # Resource templates endpoint
    ],
)
def test_common_endpoints(server_fixture: Dict[str, Any], endpoint: str) -> None:
    """Test that common endpoints are available regardless of transport type."""
    base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"
    url = f"{base_url}{endpoint}"
    
    with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
        response = client.get(url)
    
    assert response.status_code == 200, f"Expected status 200 for {endpoint}, got {response.status_code}"
    
    # Verify root endpoint response
    if endpoint == "/":
        json_response = response.json()
        assert "status" in json_response, "Missing status field in response"
        assert json_response.get("status") == "ok", "Invalid status in response"
        assert "server" in json_response, "Missing server field in response"
        assert json_response.get("server") == "ClickUp MCP Server", "Invalid server in response"
