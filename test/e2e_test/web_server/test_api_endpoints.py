"""
End-to-end tests for API endpoints to ensure they are accessible and working correctly.

This module tests all the API endpoints to ensure there are no routing conflicts
and that both the mounted MCP server and explicit API routes are working correctly.
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


class TestAPIEndpoints(BaseE2ETestWithRunningServer):
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
