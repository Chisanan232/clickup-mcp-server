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

        # Simply check if the endpoint exists - we'll get a 200 or 307 if it's mounted
        with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
            # Try HEAD request first to check if endpoint exists
            response = client.head(mcp_url)
            status_code = response.status_code

        # If the endpoint is mounted, we should get a (200,307) status
        # If the endpoint is not mounted, we would get a 404 Not Found
        assert status_code != 404, f"Expected status non-(404) for {server_fixture.url_suffix}, got {status_code}"
        assert status_code in (200, 307), f"Expected status (200,307) for {server_fixture.url_suffix}, got {status_code}"
