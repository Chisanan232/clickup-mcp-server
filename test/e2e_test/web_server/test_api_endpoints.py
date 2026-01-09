"""
End-to-end tests for API endpoints to ensure they are accessible and working correctly.

This module tests all the API endpoints to ensure there are no routing conflicts
and that both the mounted MCP server and explicit API routes are working correctly.
"""

from test.e2e_test.base.suite import (
    OPERATION_TIMEOUT,
    BaseE2ETestWithRunningServer,
    MCPServerFixtureValue,
)

import httpx
import pytest


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

    def test_cors_headers(self, server_fixture: MCPServerFixtureValue) -> None:
        """Test that CORS headers are returned correctly."""
        base_url = f"http://{server_fixture.host}:{server_fixture.port}"
        url = f"{base_url}/health"

        headers = {"Origin": "http://example.com"}

        with httpx.Client(timeout=OPERATION_TIMEOUT) as client:
            response = client.get(url, headers=headers)

        assert response.status_code == 200
        # Check for CORS headers
        # Note: FastAPI/Starlette CORSMiddleware defaults to echoing the origin if allowed,
        # but with allow_origins=["*"], it returns "*"
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
