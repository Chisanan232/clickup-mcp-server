"""
End-to-end tests for the Team API.

This module contains tests that make real API calls to the ClickUp API
using the TeamAPI client. These tests require a valid ClickUp API token.
"""

import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from dotenv import load_dotenv

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.domain import ClickUpTeam
from clickup_mcp.models.dto.space import SpaceResp


class TestTeamAPIE2E:
    """End-to-end tests for TeamAPI that make real API calls."""

    @pytest.fixture
    def env_setup(self) -> Generator[None, None, None]:
        """
        Load environment variables from .env file.

        This fixture looks for a .env file in the project root or parent directories
        and loads the variables, making them available through os.environ.
        """
        # Try to find and load .env file from current directory or parent directories
        env_path = None
        current_dir = Path.cwd()

        # Try current directory and up to 3 parent directories
        for _ in range(4):
            test_path = current_dir / ".env"
            if test_path.exists():
                env_path = test_path
                break
            current_dir = current_dir.parent

        if env_path:
            load_dotenv(env_path)

        # Store original environment variables
        original_env = os.environ.copy()

        yield

        # Restore original environment variables
        os.environ.clear()
        os.environ.update(original_env)

    @pytest.fixture
    async def api_client(self, env_setup) -> AsyncGenerator[ClickUpAPIClient, None]:
        """
        Create a real ClickUpAPIClient using the API token from environment variables.

        This fixture requires that E2E_TEST_API_TOKEN is set in the environment.
        """
        api_token = os.environ.get("E2E_TEST_API_TOKEN")

        # Skip tests if no API token is available
        if not api_token:
            pytest.skip("E2E_TEST_API_TOKEN environment variable is required for this test")

        assert api_token
        async with ClickUpAPIClient(api_token=api_token) as client:
            yield client

    @pytest.mark.asyncio
    async def test_get_authorized_teams(self, api_client: ClickUpAPIClient) -> None:
        """
        Test getting authorized teams with a real API call.

        This test makes an actual API call to the ClickUp API to get teams.
        It requires a valid API token with access to at least one team.
        """
        # Make the actual API call
        teams = await api_client.team.get_authorized_teams()

        # Basic validation
        assert teams is not None
        assert isinstance(teams, list)

        # Skip further assertions if no teams are returned
        if not teams:
            pytest.skip("No teams found - API token may not have access to any teams")

        # Validate team data structure
        for team in teams:
            assert isinstance(team, ClickUpTeam)
            assert team.team_id is not None
            assert team.id == team.team_id  # Test backward compatibility
            assert team.name is not None

            # Members might be None or empty in some cases, but if present they should be structured correctly
            if team.members:
                for member in team.members:
                    assert member.user is not None
                    if member.user.user_id:
                        assert member.user.id == member.user.user_id  # Test backward compatibility

    @pytest.mark.asyncio
    async def test_get_spaces_for_team(self, api_client: ClickUpAPIClient) -> None:
        """Test getting spaces for a specific team with a real API call."""
        team_id = os.environ.get("CLICKUP_TEST_TEAM_ID")

        if not team_id:
            pytest.skip("CLICKUP_TEST_TEAM_ID environment variable is required for this test")

        assert team_id
        spaces = await api_client.team.get_spaces(team_id)

        # Basic validation
        assert spaces is not None
        assert isinstance(spaces, list)

        if not spaces:
            pytest.skip("No spaces found for the given team ID")

        # Validate space data structure is mapped to SpaceResp DTO
        for space in spaces:
            assert isinstance(space, SpaceResp)
            assert isinstance(space.id, str) and space.id != ""
            assert isinstance(space.name, str) and space.name != ""
            assert isinstance(space.private, bool)
            # Optional fields may or may not exist depending on workspace config
            if space.statuses is not None:
                assert isinstance(space.statuses, list)
            if space.features is not None:
                assert isinstance(space.features, dict)
