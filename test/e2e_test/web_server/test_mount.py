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
from typing import Any, Dict, Generator

import httpx
import pytest
from dotenv import load_dotenv

from clickup_mcp.models.cli import MCPTransportType
from test.e2e_test.base.suite import BaseE2ETestWithRunningServer, MCPServerFixtureValue, OPERATION_TIMEOUT


class TestWebServerMountMcpServer(BaseE2ETestWithRunningServer):
    # Test SSE Transport and HTTP Streaming Transport


    def test_mcp_endpoint(self, server_fixture: MCPServerFixtureValue) -> None:
        """Test if the MCP server endpoint is correctly mounted for every transports."""
        mcp_url = f"http://{server_fixture.host}:{server_fixture.port}{server_fixture.url_suffix}"

        # Simply check if the endpoint exists - we'll get a 307 if it's mounted
        with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
            if server_fixture.transport == "sse":
                # mcp_url = f"http://{server_fixture.host}:{server_fixture.port}/sse"
                response = client.get(mcp_url)
            else:
                response = client.post(mcp_url)

        # If the endpoint is mounted, we should get a (200,307) status
        # If the endpoint is not mounted, we would get a 404 Not Found
        assert response.status_code != 404, f"Expected status non-(404) for {server_fixture.url_suffix}, got {response.status_code}"
        assert response.status_code in (200, 307), f"Expected status non-(200,307) for {server_fixture.url_suffix}, got {response.status_code}"


    # Test Common Endpoints (regardless of transport)


    @pytest.mark.parametrize(
        "endpoint",
        [
            "/health",  # Root health check
        ],
    )
    def test_common_endpoints(self, server_fixture: MCPServerFixtureValue, endpoint: str) -> None:
        """Test that common endpoints are available regardless of transport type."""
        base_url = f"http://{server_fixture.host}:{server_fixture.port}"
        url = f"{base_url}{endpoint}"

        with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
            response = client.get(url)

        assert response.status_code == 200, f"Expected status 200 for {endpoint}, got {response.status_code}"

        # Verify root endpoint response
        if endpoint == "/health":
            json_response = response.json()
            assert "status" in json_response, "Missing status field in response"
            assert json_response.get("status") == "ok", "Invalid status in response"
            assert "server" in json_response, "Missing server field in response"
            assert json_response.get("server") == "ClickUp MCP Server", "Invalid server in response"
