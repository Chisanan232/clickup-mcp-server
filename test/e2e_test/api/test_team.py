"""
End-to-end tests for the Team API.

This module contains tests that make real API calls to the ClickUp API
using the TeamAPI client. These tests require a valid ClickUp API token.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Generator

import pytest
from dotenv import load_dotenv

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.domain import ClickUpTeam


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
        
        This fixture requires that CLICKUP_API_TOKEN is set in the environment.
        """
        api_token = os.environ.get("CLICKUP_API_TOKEN")
        
        # Skip tests if no API token is available
        if not api_token:
            pytest.skip("CLICKUP_API_TOKEN environment variable is required for this test")
            
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
