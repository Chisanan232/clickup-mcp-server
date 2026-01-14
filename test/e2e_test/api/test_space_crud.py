"""
End-to-end tests for Space CRUD operations.

This module contains tests that make real API calls to the ClickUp API
using the Space API client. These tests require a valid ClickUp API token
and a test team ID. Folder/List interactions are not covered here.

Environment variables required:
- E2E_TEST_API_TOKEN: Valid ClickUp API token
- CLICKUP_TEST_TEAM_ID: Team ID for testing
"""

from test.config import TestSettings
from typing import AsyncGenerator

import pytest

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.dto.space import SpaceCreate, SpaceUpdate


class TestSpaceCRUDE2E:
    """End-to-end tests for Space, Folder, and List CRUD operations."""

    @pytest.fixture
    async def api_client(self, test_settings: TestSettings) -> AsyncGenerator[ClickUpAPIClient, None]:
        """Create a real ClickUpAPIClient using the API token from settings."""
        assert (
            test_settings.e2e_test_api_token
        ), "Miss property from dotenv file: *E2E_TEST_API_TOKEN* is required for this test"

        api_token = test_settings.e2e_test_api_token.get_secret_value()
        async with ClickUpAPIClient(api_token=api_token) as client:
            yield client

    @pytest.mark.asyncio
    async def test_space_crud_operations(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test Space CRUD operations: Create, Read, Update, Delete."""
        team_id = test_settings.clickup_test_team_id
        assert team_id, "Miss property from dotenv file: *CLICKUP_TEST_TEAM_ID* is required"

        # Create a space
        space_create = SpaceCreate(name="[TEST] Space CRUD Test", multiple_assignees=True)
        space_id: str | None = None
        created_space = await api_client.space.create(team_id, space_create)

        # If creation is not permitted (e.g., 403 due to insufficient permissions), skip this test gracefully
        if created_space is None:
            pytest.skip("Space creation not permitted with the provided token/team (likely insufficient permissions).")

        assert created_space is not None
        assert created_space.name == "[TEST] Space CRUD Test"
        space_id = created_space.id

        try:
            # Read the space
            retrieved_space = await api_client.space.get(space_id)
            assert retrieved_space is not None
            assert retrieved_space.id == space_id
            assert retrieved_space.name == "[TEST] Space CRUD Test"

            # Update the space
            space_update = SpaceUpdate(name="[TEST] Updated Space")
            updated_space = await api_client.space.update(space_id, space_update)
            assert updated_space is not None
            assert updated_space.name == "[TEST] Updated Space"

        finally:
            # Delete the space if it was created
            if space_id:
                delete_result = await api_client.space.delete(space_id)
                assert delete_result is True

    @pytest.mark.asyncio
    async def test_get_all_spaces(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test getting all spaces in a team."""
        team_id = test_settings.clickup_test_team_id
        assert team_id, "Miss property from dotenv file: *CLICKUP_TEST_TEAM_ID* is required"

        spaces = await api_client.space.get_all(team_id)

        assert spaces is not None
        assert isinstance(spaces, list)
        # Should have at least one space
        assert len(spaces) > 0
