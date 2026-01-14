"""
End-to-end tests for Folder CRUD operations.

This module contains tests that make real API calls to the ClickUp API
using the Folder API client. These tests require a valid ClickUp API token,
team ID, and space ID. Space/List interactions are not covered here.

Environment variables required:
- E2E_TEST_API_TOKEN: Valid ClickUp API token
- CLICKUP_TEST_TEAM_ID: Team ID for testing
- CLICKUP_TEST_SPACE_ID: Space ID where folders will be created
"""

from test.config import TestSettings
from typing import AsyncGenerator

import pytest

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.dto.folder import FolderCreate, FolderUpdate


class TestFolderCRUDE2E:
    """End-to-end tests for Folder CRUD operations."""

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
    async def test_folder_crud_operations(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test Folder CRUD operations: Create, Read, Update, Delete."""
        team_id = test_settings.clickup_test_team_id
        space_id = test_settings.clickup_test_space_id
        assert (
            team_id and space_id
        ), "Miss property from dotenv file: *CLICKUP_TEST_TEAM_ID* and *CLICKUP_TEST_SPACE_ID* are required"

        # Create a folder
        folder_create = FolderCreate(name="[TEST] Folder CRUD Test")
        created_folder = await api_client.folder.create(space_id, folder_create)

        assert created_folder is not None
        assert created_folder.name == "[TEST] Folder CRUD Test"
        folder_id = created_folder.id

        try:
            # Read the folder
            retrieved_folder = await api_client.folder.get(folder_id)
            assert retrieved_folder is not None
            assert retrieved_folder.id == folder_id

            # Update the folder
            folder_update = FolderUpdate(name="[TEST] Updated Folder")
            updated_folder = await api_client.folder.update(folder_id, folder_update)
            assert updated_folder is not None
            assert updated_folder.name == "[TEST] Updated Folder"

        finally:
            # Delete the folder
            delete_result = await api_client.folder.delete(folder_id)
            assert delete_result is True

    @pytest.mark.asyncio
    async def test_get_all_folders(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test getting all folders in a space."""
        space_id = test_settings.clickup_test_space_id
        assert space_id, "Miss property from dotenv file: *CLICKUP_TEST_SPACE_ID* is required"

        folders = await api_client.folder.get_all(space_id)

        assert folders is not None
        assert isinstance(folders, list)
