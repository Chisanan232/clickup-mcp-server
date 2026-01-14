"""
End-to-end tests for the Team API.

This module contains tests that make real API calls to the ClickUp API
using the TeamAPI client. These tests require a valid ClickUp API token.
"""

from test.config import TestSettings
from typing import AsyncGenerator

import pytest

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.domain import ClickUpTeam
from clickup_mcp.models.dto.space import SpaceFeatures, SpaceResp


class TestTeamAPIE2E:
    """End-to-end tests for TeamAPI that make real API calls."""

    @pytest.fixture
    async def api_client(self, test_settings: TestSettings) -> AsyncGenerator[ClickUpAPIClient, None]:
        """
        Create a real ClickUpAPIClient using the API token from settings.
        """
        if not test_settings.e2e_test_api_token:
            pytest.skip("E2E_TEST_API_TOKEN is required for this test")

        assert test_settings.e2e_test_api_token
        api_token = test_settings.e2e_test_api_token.get_secret_value()
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
    async def test_get_spaces_for_team(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test getting spaces for a specific team with a real API call."""
        team_id = test_settings.clickup_test_team_id

        if not team_id:
            pytest.skip("CLICKUP_TEST_TEAM_ID is required for this test")

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
                assert isinstance(space.features, SpaceFeatures)
