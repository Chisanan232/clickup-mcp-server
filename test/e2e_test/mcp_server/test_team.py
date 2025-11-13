"""
End-to-end tests for MCP team functions.

This module tests the MCP functions for team operations by connecting to a running
MCP server instance using both HTTP streaming and SSE transports.
"""

import asyncio
from test.e2e_test.base import (
    OPERATION_TIMEOUT,
    BaseMCPServerFunctionTest,
    EndpointClient,
)
from test.e2e_test.base.dto import FunctionPayloadDto

import pytest
from mcp import ClientSession


class TestClickUpTeam(BaseMCPServerFunctionTest):
    """Base test suite for end-to-end tests for MCP functions related to teams."""

    @pytest.mark.asyncio
    async def test_functions_in_tools(self, mcp_session: ClientSession) -> None:
        """Test successful retrieval of authorized teams."""
        # Call the MCP function with real server connection with timeout
        result = await asyncio.wait_for(mcp_session.list_tools(), timeout=OPERATION_TIMEOUT)
        tools = [r.name for r in result.tools]
        assert "get_authorized_teams" in tools

    @pytest.mark.asyncio
    async def test_get_authorized_teams_success(self, client: EndpointClient) -> None:
        """Test successful retrieval of authorized teams."""
        # Call the MCP function with real server connection with timeout
        result = await asyncio.wait_for(
            client.call_function(FunctionPayloadDto(function="get_authorized_teams", arguments={})),
            timeout=OPERATION_TIMEOUT,
        )

        # Check the response structure (WorkspaceListResult as dict)
        assert result is not None
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        assert "items" in result, "items field missing in WorkspaceListResult"

        items = result.get("items") or []
        if len(items) > 0:
            first = items[0]
            assert isinstance(first, dict)
            # Verify the item has expected fields
            assert "team_id" in first, "team_id field missing"
            assert "name" in first, "name field missing"
