"""
End-to-end tests for MCP server API path mounting.

This module tests whether the MCP server endpoints are correctly mounted
and accessible at the expected API paths.
"""

from test.e2e_test.base.suite import (
    OPERATION_TIMEOUT,
    BaseE2ETestWithRunningServer,
    MCPServerFixtureValue,
)

import httpx


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

        # If the endpoint is mounted, we should get a (200,307,405) status
        # 200: Direct route (SSE /sse/sse)
        # 307: Redirect (HTTP streaming /mcp, SSE /sse)
        # 405: Method not allowed but route exists (HTTP streaming /mcp/mcp)
        # If the endpoint is not mounted, we would get a 404 Not Found
        assert status_code != 404, f"Expected status non-(404) for {server_fixture.url_suffix}, got {status_code}"
        assert status_code in (
            200,
            307,
            405,
        ), f"Expected status (200,307,405) for {server_fixture.url_suffix}, got {status_code}"
