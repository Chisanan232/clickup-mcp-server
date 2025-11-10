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
from clickup_mcp.models.dto.folder import FolderCreate, FolderUpdate


class TestFolderCRUDE2E:
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
    async def test_folder_crud_operations(self, api_client: ClickUpAPIClient) -> None:
        """Test Folder CRUD operations: Create, Read, Update, Delete."""
        team_id = os.environ.get("CLICKUP_TEST_TEAM_ID", "")
        space_id = os.environ.get("CLICKUP_TEST_SPACE_ID", "")

        if not team_id or not space_id:
            pytest.skip("CLICKUP_TEST_TEAM_ID and CLICKUP_TEST_SPACE_ID environment variables are required")

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
    async def test_get_all_folders(self, api_client: ClickUpAPIClient) -> None:
        """Test getting all folders in a space."""
        space_id = os.environ.get("CLICKUP_TEST_SPACE_ID", "")
        if not space_id:
            pytest.skip("CLICKUP_TEST_SPACE_ID environment variable is required")

        folders = await api_client.folder.get_all(space_id)

        assert folders is not None
        assert isinstance(folders, list)
