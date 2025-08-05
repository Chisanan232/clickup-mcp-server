"""
Integration tests for MCP team functions.

This module tests the MCP functions for team operations by connecting to a running
MCP server instance using both HTTP streaming and SSE transports.
"""

from abc import ABC
from typing import Any, Dict, List

import pytest
from mcp import ClientSession
from pydantic import BaseModel

from .base_test import BaseMCPServerTest


# Sample domain models for testing
class ClickUpUser(BaseModel):
    """Sample domain model for ClickUp user."""

    user_id: int | None = None
    username: str | None = None
    email: str | None = None

    # For backward compatibility
    id: int | None = None


class ClickUpTeamMember(BaseModel):
    """Sample domain model for ClickUp team member."""

    user: ClickUpUser | None = None


class ClickUpTeam(BaseModel):
    """Sample domain model for ClickUp team."""

    team_id: str
    name: str
    color: str | None = None
    avatar: str | None = None
    members: List[ClickUpTeamMember] | None = None

    # For backward compatibility
    id: str | None = None


class BaseTeamMCPFunctionsTestSuite(BaseMCPServerTest, ABC):
    """Base test suite for integration tests for MCP functions related to teams."""

    def mcp_functions_in_tools(self) -> list[str]:
        """Return the list of MCP functions tested in this suite."""
        return ["get_authorized_teams"]

    def create_mock_tool_list(self) -> Dict[str, Dict[str, str]]:
        """Create a dictionary of mock tools for testing."""
        return {
            "get_authorized_teams": {
                "name": "get_authorized_teams",
                "title": "Get ClickUp Teams",
                "description": "Retrieve all teams/workspaces that the authenticated user has access to.",
            }
        }

    async def mock_call_tool_side_effect(self, name: str, arguments: Dict[str, Any] | None = None, **kwargs) -> Any:
        """Mock the behavior of call_tool for testing."""
        if name != "get_authorized_teams":
            return None

        # For the get_authorized_teams function
        if name == "get_authorized_teams":
            # Create sample teams for testing
            team1 = ClickUpTeam(
                team_id="team1",
                name="Team One",
                color="#000000",
                members=[
                    ClickUpTeamMember(user=ClickUpUser(user_id=1234, username="test_user", email="user@example.com"))
                ],
            )

            team2 = ClickUpTeam(team_id="team2", name="Team Two", color="#FFFFFF")

            # Check for special test cases in the arguments
            if arguments and arguments.get("test_case") == "empty":
                # Return empty list for testing empty results
                return []
            elif arguments and arguments.get("test_case") == "error":
                # Raise exception for testing error handling
                raise ValueError("Error retrieving teams: Test error")

            # Default case: return sample teams
            return [team1.model_dump(), team2.model_dump()]

    @pytest.mark.asyncio
    async def test_get_authorized_teams_success(self, mcp_client: ClientSession) -> None:
        """Test successful retrieval of authorized teams."""
        # Call the MCP function
        result = await mcp_client.call_tool("get_authorized_teams")

        # Check the response structure
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2

        # Check first team data
        assert result[0]["team_id"] == "team1"
        assert result[0]["name"] == "Team One"
        assert result[0]["color"] == "#000000"

        # Check members data in first team
        assert len(result[0]["members"]) == 1
        assert result[0]["members"][0]["user"]["user_id"] == 1234
        assert result[0]["members"][0]["user"]["username"] == "test_user"
        assert result[0]["members"][0]["user"]["email"] == "user@example.com"

        # Check second team
        assert result[1]["team_id"] == "team2"
        assert result[1]["name"] == "Team Two"
        assert result[1]["color"] == "#FFFFFF"

    @pytest.mark.asyncio
    async def test_get_authorized_teams_empty_result(self, mcp_client: ClientSession) -> None:
        """Test getting authorized teams when none are available."""
        # Call the MCP function with the empty test case
        result = await mcp_client.call_tool("get_authorized_teams", {"test_case": "empty"})

        # Should return an empty list
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_authorized_teams_error_handling(self, mcp_client: ClientSession) -> None:
        """Test that get_authorized_teams properly handles and reports errors."""
        # This will hit our error case in the mock's side_effect
        with pytest.raises(ValueError) as exc_info:
            await mcp_client.call_tool("get_authorized_teams", {"test_case": "error"})

        # Should include the error message from the mock
        assert "Error retrieving teams" in str(exc_info.value)


class TestTeamByHTTPStreamingTransport(BaseTeamMCPFunctionsTestSuite):
    """Integration tests for MCP team functions using the HTTP streaming transport."""

    def get_transport_option(self) -> str:
        """Return the HTTP streaming transport option."""
        return "http-streaming"


class TestTeamBySSETransport(BaseTeamMCPFunctionsTestSuite):
    """Integration tests for MCP team functions using the SSE transport."""

    def get_transport_option(self) -> str:
        """Return the SSE transport option."""
        return "sse"
