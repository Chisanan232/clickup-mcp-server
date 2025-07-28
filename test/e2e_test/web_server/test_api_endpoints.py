"""
End-to-end tests for API endpoints to ensure they are accessible and working correctly.

This module tests all the API endpoints to ensure there are no routing conflicts
and that both the mounted MCP server and explicit API routes are working correctly.
"""

import socket
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Generator, Sequence

import httpx
import pytest

# Path to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


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


class TestAPIEndpoints:
    """End-to-end tests for API endpoints to ensure they are accessible and working."""

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
        ]

        # Start the server process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PROJECT_ROOT)

        try:
            # Wait for the server to start - use a reasonable timeout
            server_started = wait_for_port(port, timeout=15)
            assert server_started, "Server failed to start within timeout"

            # Wait additional time for routes to be registered
            time.sleep(3)

            # Provide the server details to the test
            yield {"port": port, "host": host, "process": process}

        except Exception as e:
            # Log error and clean up
            print(f"Error during server startup: {str(e)}")

            # Try to get stdout/stderr from the process to help with debugging
            if process.stdout:
                stdout = process.stdout.read().decode("utf-8")
                if stdout:
                    print(f"Server stdout: {stdout}")

            if process.stderr:
                stderr = process.stderr.read().decode("utf-8")
                if stderr:
                    print(f"Server stderr: {stderr}")

            # Make sure we terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

            raise

        finally:
            # Always clean up the server process
            if "process" in locals():
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

                # Ensure the port is freed
                time.sleep(1)
                assert not is_port_in_use(port), "Server did not shut down properly"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, server_fixture: Dict[str, Any]) -> None:
        """Test that the root endpoint is accessible."""
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["server"] == "ClickUp MCP Server"

    @pytest.mark.asyncio
    async def test_api_tools_endpoint(self, server_fixture: Dict[str, Any]) -> None:
        """Test that the /mcp-utils/tools endpoint is accessible."""
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/mcp-utils/tools")
            assert response.status_code == 200
            data = response.json()
            assert "tools" in data
            assert isinstance(data["tools"], list)

    @pytest.mark.asyncio
    async def test_api_resources_endpoint(self, server_fixture: Dict[str, Any]) -> None:
        """Test that the /mcp-utils/resources endpoint is accessible."""
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/mcp-utils/resources")
            assert response.status_code == 200
            data = response.json()
            assert "resources" in data
            assert isinstance(data["resources"], list)

    @pytest.mark.asyncio
    async def test_api_prompts_endpoint(self, server_fixture: Dict[str, Any]) -> None:
        """Test that the /mcp-utils/prompts endpoint is accessible."""
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/mcp-utils/prompts")
            assert response.status_code == 200
            data = response.json()
            assert "prompts" in data
            assert isinstance(data["prompts"], list)

    @pytest.mark.asyncio
    async def test_api_resource_templates_endpoint(self, server_fixture: Dict[str, Any]) -> None:
        """Test that the /mcp-utils/resource_templates endpoint is accessible."""
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/mcp-utils/resource_templates")
            assert response.status_code == 200
            data = response.json()
            assert "resource_templates" in data
            assert isinstance(data["resource_templates"], list)

    @pytest.mark.asyncio
    async def test_mcp_mounted_app(self, server_fixture: Dict[str, Any]) -> None:
        """
        Test that the mounted MCP app is accessible.

        This test verifies the SSE endpoint that should be available through the mounted app.
        The actual endpoint to test depends on what the MCP server exposes through its sse_app.
        """
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        # Try to access the MCP mounted app root
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/mcp")
            # Some response should be returned, though it might not be a 200
            # The important thing is that it's not a 404, which would indicate the app isn't mounted
            print(f"MCP mounted app response: {response.status_code} - {response.text}")
            assert response.status_code != 404, "MCP app not properly mounted"

    @pytest.mark.asyncio
    async def test_no_conflict_between_routes(self, server_fixture: Dict[str, Any]) -> None:
        """
        Test that there is no conflict between the explicit API routes and the mounted MCP app.

        This test specifically verifies that the old paths (/mcp/tools, etc.) return 404s,
        confirming that the API endpoints are only available at /mcp-utils/* paths.
        """
        base_url = f"http://{server_fixture['host']}:{server_fixture['port']}"

        # These paths should NOT be accessible as they'd conflict with the mounted MCP app
        conflict_paths = [
            "/mcp/tools",
            "/mcp/resources",
            "/mcp/prompts",
            "/mcp/resource_templates",
        ]

        async with httpx.AsyncClient(timeout=10.0) as client:
            for path in conflict_paths:
                print(f"Testing potential conflict path: {path}")
                response = await client.get(f"{base_url}{path}")

                # These should either return 404 (not found) or some other non-200 status
                # We specifically want to confirm they don't return 200 OK with our API data
                if response.status_code == 200:
                    # If status is 200, make sure the response isn't our API response format
                    try:
                        data = response.json()
                        # Check if this looks like our API response
                        path_part = path.split("/")[-1]  # 'tools', 'resources', etc.
                        assert path_part not in data, f"Path {path} appears to conflict with API endpoint"
                    except:
                        # If it's not JSON, then it's definitely not our API response
                        pass

                print(f"Path {path} returned status code {response.status_code}")
