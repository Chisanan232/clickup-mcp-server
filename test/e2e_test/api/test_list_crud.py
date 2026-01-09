"""
End-to-end tests for List CRUD operations.

This module contains tests that make real API calls to the ClickUp API
using the List API client. These tests require a valid ClickUp API token,
team ID, space ID, and folder ID. Space/Folder creation is not covered here.

Environment variables required:
- E2E_TEST_API_TOKEN: Valid ClickUp API token
- CLICKUP_TEST_TEAM_ID: Team ID for testing
- CLICKUP_TEST_SPACE_ID: Space ID containing test folders
- CLICKUP_TEST_FOLDER_ID: Folder ID where lists will be created
"""

import uuid
from typing import AsyncGenerator

import pytest

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.config import TestSettings as E2ETestSettings
from clickup_mcp.models.dto.list import ListCreate, ListUpdate


class TestListCRUDE2E:
    """End-to-end tests for List CRUD operations."""

    @pytest.fixture
    def test_settings(self) -> E2ETestSettings:
        """Get test settings."""
        return E2ETestSettings()

    @pytest.fixture
    async def api_client(self, test_settings: E2ETestSettings) -> AsyncGenerator[ClickUpAPIClient, None]:
        """Create a real ClickUpAPIClient using the API token from settings."""
        if not test_settings.e2e_test_api_token:
            pytest.skip("E2E_TEST_API_TOKEN is required for this test")

        api_token = test_settings.e2e_test_api_token.get_secret_value()
        async with ClickUpAPIClient(api_token=api_token) as client:
            yield client

    @pytest.mark.asyncio
    async def test_list_crud_operations(self, api_client: ClickUpAPIClient, test_settings: E2ETestSettings) -> None:
        """Test List CRUD operations: Create, Read, Update, Delete."""
        team_id = test_settings.clickup_test_team_id
        space_id = test_settings.clickup_test_space_id
        folder_id = test_settings.clickup_test_folder_id

        if not team_id or not space_id or not folder_id:
            pytest.skip("Test environment variables are required")

        # Create a list with a unique name to avoid collisions
        suffix = uuid.uuid4().hex[:8]
        list_name = f"[TEST] List CRUD Test {suffix}"
        list_create = ListCreate(name=list_name)
        created_list = await api_client.list.create(folder_id, list_create)

        assert created_list is not None
        assert created_list.name == list_name
        list_id = created_list.id

        try:
            # Read the list
            retrieved_list = await api_client.list.get(list_id)
            assert retrieved_list is not None
            assert retrieved_list.id == list_id

            # Update the list with a unique name to avoid collisions
            updated_name = f"[TEST] Updated List {suffix}"
            list_update = ListUpdate(name=updated_name)
            updated_list = await api_client.list.update(list_id, list_update)
            assert updated_list is not None
            assert updated_list.name == updated_name

        finally:
            # Delete the list
            delete_result = await api_client.list.delete(list_id)
            assert delete_result is True

    @pytest.mark.asyncio
    async def test_get_all_lists_in_folder(self, api_client: ClickUpAPIClient, test_settings: E2ETestSettings) -> None:
        """Test getting all lists in a folder."""
        folder_id = test_settings.clickup_test_folder_id
        if not folder_id:
            pytest.skip("CLICKUP_TEST_FOLDER_ID is required")

        lists = await api_client.list.get_all_in_folder(folder_id)

        assert lists is not None
        assert isinstance(lists, list)

    @pytest.mark.asyncio
    async def test_get_all_folderless_lists(self, api_client: ClickUpAPIClient, test_settings: E2ETestSettings) -> None:
        """Test getting all folderless lists in a space."""
        space_id = test_settings.clickup_test_space_id
        if not space_id:
            pytest.skip("CLICKUP_TEST_SPACE_ID is required")

        lists = await api_client.list.get_all_folderless(space_id)

        assert lists is not None
        assert isinstance(lists, list)
