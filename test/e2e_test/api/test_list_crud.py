"""
End-to-end tests for Space, Folder, and List CRUD operations.

This module contains tests that make real API calls to the ClickUp API
using the Space, Folder, and List API clients. These tests require a valid
ClickUp API token and a test team ID.

Environment variables required:
- E2E_TEST_API_TOKEN: Valid ClickUp API token
- CLICKUP_TEST_TEAM_ID: Team ID for testing
"""

import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from dotenv import load_dotenv

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.dto.list import ListCreate, ListUpdate


class TestListCRUDE2E:
    """End-to-end tests for Space, Folder, and List CRUD operations."""

    @pytest.fixture
    def env_setup(self) -> Generator[None, None, None]:
        """Load environment variables from .env file."""
        env_path = None
        current_dir = Path.cwd()

        for _ in range(4):
            test_path = current_dir / ".env"
            if test_path.exists():
                env_path = test_path
                break
            current_dir = current_dir.parent

        if env_path:
            load_dotenv(env_path)

        original_env = os.environ.copy()
        yield
        os.environ.clear()
        os.environ.update(original_env)

    @pytest.fixture
    async def api_client(self, env_setup) -> AsyncGenerator[ClickUpAPIClient, None]:
        """Create a real ClickUpAPIClient using the API token from environment variables."""
        api_token = os.environ.get("E2E_TEST_API_TOKEN", "")

        if not api_token:
            pytest.skip("E2E_TEST_API_TOKEN environment variable is required for this test")

        async with ClickUpAPIClient(api_token=api_token) as client:
            yield client

    @pytest.mark.asyncio
    async def test_list_crud_operations(self, api_client: ClickUpAPIClient) -> None:
        """Test List CRUD operations: Create, Read, Update, Delete."""
        team_id = os.environ.get("CLICKUP_TEST_TEAM_ID", "")
        space_id = os.environ.get("CLICKUP_TEST_SPACE_ID", "")
        folder_id = os.environ.get("CLICKUP_TEST_FOLDER_ID", "")

        if not team_id or not space_id or not folder_id:
            pytest.skip("Test environment variables are required")

        # Create a list
        list_create = ListCreate(name="[TEST] List CRUD Test")
        created_list = await api_client.list.create(folder_id, list_create)

        assert created_list is not None
        assert created_list.name == "[TEST] List CRUD Test"
        list_id = created_list.id

        try:
            # Read the list
            retrieved_list = await api_client.list.get(list_id)
            assert retrieved_list is not None
            assert retrieved_list.id == list_id

            # Update the list
            list_update = ListUpdate(name="[TEST] Updated List")
            updated_list = await api_client.list.update(list_id, list_update)
            assert updated_list is not None
            assert updated_list.name == "[TEST] Updated List"

        finally:
            # Delete the list
            delete_result = await api_client.list.delete(list_id)
            assert delete_result is True

    @pytest.mark.asyncio
    async def test_get_all_lists_in_folder(self, api_client: ClickUpAPIClient) -> None:
        """Test getting all lists in a folder."""
        folder_id = os.environ.get("CLICKUP_TEST_FOLDER_ID", "")
        if not folder_id:
            pytest.skip("CLICKUP_TEST_FOLDER_ID environment variable is required")

        lists = await api_client.list.get_all_in_folder(folder_id)

        assert lists is not None
        assert isinstance(lists, list)

    @pytest.mark.asyncio
    async def test_get_all_folderless_lists(self, api_client: ClickUpAPIClient) -> None:
        """Test getting all folderless lists in a space."""
        space_id = os.environ.get("CLICKUP_TEST_SPACE_ID", "")
        if not space_id:
            pytest.skip("CLICKUP_TEST_SPACE_ID environment variable is required")

        lists = await api_client.list.get_all_folderless(space_id)

        assert lists is not None
        assert isinstance(lists, list)
