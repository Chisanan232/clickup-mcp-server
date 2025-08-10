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

        # Check the response structure
        assert result is not None
        assert isinstance(result, list), f"Expected list result, got {type(result)}"

        # Since we're testing with real data, we can only make general assertions
        if len(result) > 0:
            team = result[0]
            # Verify the team has the expected fields based on our domain model
            assert "team_id" in team, "team_id field missing"
            assert "name" in team, "name field missing"

            # Verify backward compatibility fields
            assert "id" in team, "id field missing (backward compatibility)"
            assert team["id"] == team["team_id"], "id should match team_id for backward compatibility"

            # Test members field if present
            if team.get("members") and len(team["members"]) > 0:
                member = team["members"][0]
                assert "user" in member, "user field missing in member"

                if member["user"]:
                    user = member["user"]
                    assert "user_id" in user, "user_id field missing in user"
                    if "id" in user:
                        assert user["id"] == user["user_id"], "user id should match user_id for backward compatibility"
