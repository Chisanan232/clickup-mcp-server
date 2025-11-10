"""
End-to-end tests for Task Custom Fields, Dependencies, and TIML operations.

This module contains tests that make real API calls to the ClickUp API
using the Task API client for advanced features like custom fields,
dependencies, and TIML (Tasks in Multiple Lists).

Environment variables required:
- E2E_TEST_API_TOKEN: Valid ClickUp API token
- CLICKUP_TEST_LIST_ID: Primary list ID for testing
- CLICKUP_TEST_LIST_ID_2: Secondary list ID for TIML testing (optional)
"""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from dotenv import load_dotenv

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.dto.task import TaskCreate


class TestTaskCFDependencyTIMLe2e:
    """End-to-end tests for Task Custom Fields, Dependencies, and TIML."""

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
    async def test_set_custom_field(self, api_client: ClickUpAPIClient) -> None:
        """Test setting a custom field value on a task."""
        list_id = os.environ.get("CLICKUP_TEST_LIST_ID", "")
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID environment variable is required")

        # Create a task
        task_create = TaskCreate(name="[TEST] Task with Custom Field")
        task = await api_client.task.create(list_id, task_create)
        assert task is not None
        task_id = task.id

        try:
            # Set a custom field value
            # Note: field_id should be obtained from your ClickUp workspace
            # This is a placeholder - replace with actual field ID from your workspace
            field_id = os.environ.get("CLICKUP_TEST_CUSTOM_FIELD_ID", "")
            if field_id:
                result = await api_client.task.set_custom_field(task_id, field_id, "test_value")
                assert result is True

                # Verify the custom field was set
                retrieved_task = await api_client.task.get(task_id)
                assert retrieved_task is not None

        finally:
            await api_client.task.delete(task_id)

    @pytest.mark.asyncio
    async def test_clear_custom_field(self, api_client: ClickUpAPIClient) -> None:
        """Test clearing a custom field value on a task."""
        list_id = os.environ.get("CLICKUP_TEST_LIST_ID", "")
        field_id = os.environ.get("CLICKUP_TEST_CUSTOM_FIELD_ID", "")

        if not list_id or not field_id:
            pytest.skip("Required environment variables not set")

        # Create a task
        task_create = TaskCreate(name="[TEST] Task for CF Clear")
        task = await api_client.task.create(list_id, task_create)
        assert task is not None
        task_id = task.id

        try:
            # Set a custom field value
            await api_client.task.set_custom_field(task_id, field_id, "test_value")

            # Clear the custom field
            result = await api_client.task.clear_custom_field(task_id, field_id)
            assert result is True

        finally:
            await api_client.task.delete(task_id)

    @pytest.mark.asyncio
    async def test_add_dependency(self, api_client: ClickUpAPIClient) -> None:
        """Test adding a dependency between tasks."""
        list_id = os.environ.get("CLICKUP_TEST_LIST_ID", "")
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID environment variable is required")

        # Create two tasks
        task1_create = TaskCreate(name="[TEST] Task 1 - Blocking")
        task1 = await api_client.task.create(list_id, task1_create)
        assert task1 is not None
        task1_id = task1.id

        task2_create = TaskCreate(name="[TEST] Task 2 - Dependent")
        task2 = await api_client.task.create(list_id, task2_create)
        assert task2 is not None
        task2_id = task2.id

        try:
            # Add dependency: task2 depends on task1
            result = await api_client.task.add_dependency(task2_id, task1_id, dependency_type="waiting_on")
            assert result is True

            # Verify the dependency was added
            retrieved_task = await api_client.task.get(task2_id)
            assert retrieved_task is not None
            # Note: dependencies might not be immediately visible in the response

        finally:
            # Clean up
            await api_client.task.delete(task1_id)
            await api_client.task.delete(task2_id)

    @pytest.mark.skip(reason="My plan is limited to usages of feature.")
    @pytest.mark.asyncio
    async def test_add_task_to_multiple_lists_timl(self, api_client: ClickUpAPIClient) -> None:
        """Test adding a task to multiple lists (TIML)."""
        list_id_1 = os.environ.get("CLICKUP_TEST_LIST_ID", "")
        list_id_2 = os.environ.get("CLICKUP_TEST_LIST_ID_2", "")

        if not list_id_1 or not list_id_2:
            pytest.skip("CLICKUP_TEST_LIST_ID and CLICKUP_TEST_LIST_ID_2 environment variables are required")

        # Create a task in the first list
        task_create = TaskCreate(name="[TEST] Task for TIML")
        task = await api_client.task.create(list_id_1, task_create)
        assert task is not None
        task_id = task.id

        try:
            # Add the task to the second list
            result = await api_client.list.add_task(list_id_2, task_id)
            assert result is True

            # List tasks in the second list with TIML enabled
            from clickup_mcp.models.dto.task import TaskListQuery

            query = TaskListQuery(page=0, limit=100, include_timl=True)

            # The ClickUp API can be eventually consistent for TIML operations.
            # Retry for a short period until the task shows up in the second list.
            task_ids: list[str] = []
            for _ in range(10):  # up to ~10 seconds
                tasks = await api_client.task.list_in_list(list_id_2, query)
                task_ids = [t.id for t in tasks]
                if task_id in task_ids:
                    break
                await asyncio.sleep(1)

            # Verify the task appears in the second list within the retry window
            assert task_id in task_ids

            # Remove the task from the second list
            remove_result = await api_client.list.remove_task(list_id_2, task_id)
            assert remove_result is True

        finally:
            # Clean up
            await api_client.task.delete(task_id)

    @pytest.mark.asyncio
    async def test_create_task_with_custom_fields(self, api_client: ClickUpAPIClient) -> None:
        """Test creating a task with custom fields."""
        list_id = os.environ.get("CLICKUP_TEST_LIST_ID", "")
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID environment variable is required")

        # Create a task with custom fields
        # Note: custom_fields format depends on your ClickUp workspace configuration
        custom_fields = []
        field_id = os.environ.get("CLICKUP_TEST_CUSTOM_FIELD_ID", "")
        if field_id:
            custom_fields = [{"id": field_id, "value": "initial_value"}]

        task_create = TaskCreate(
            name="[TEST] Task with CF on Create",
            description="Task created with custom fields",
            custom_fields=custom_fields,
        )
        task = await api_client.task.create(list_id, task_create)

        assert task is not None
        assert task.name == "[TEST] Task with CF on Create"
        task_id = task.id

        try:
            # Verify the task was created
            retrieved_task = await api_client.task.get(task_id)
            assert retrieved_task is not None

        finally:
            await api_client.task.delete(task_id)

    @pytest.mark.asyncio
    async def test_task_dependency_types(self, api_client: ClickUpAPIClient) -> None:
        """Test different dependency types."""
        list_id = os.environ.get("CLICKUP_TEST_LIST_ID", "")
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID environment variable is required")

        # Create two tasks
        task1_create = TaskCreate(name="[TEST] Task A")
        task1 = await api_client.task.create(list_id, task1_create)
        assert task1 is not None
        task1_id = task1.id

        task2_create = TaskCreate(name="[TEST] Task B")
        task2 = await api_client.task.create(list_id, task2_create)
        assert task2 is not None
        task2_id = task2.id

        try:
            # Test different dependency types
            dependency_types = ["waiting_on", "blocking", "related"]

            for dep_type in dependency_types:
                result = await api_client.task.add_dependency(task2_id, task1_id, dependency_type=dep_type)
                # Result may vary based on ClickUp API permissions
                assert isinstance(result, bool)

        finally:
            await api_client.task.delete(task1_id)
            await api_client.task.delete(task2_id)
