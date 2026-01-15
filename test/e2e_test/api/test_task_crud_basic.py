"""
End-to-end tests for Task CRUD operations.

This module contains tests that make real API calls to the ClickUp API
using the Task API client. These tests require a valid ClickUp API token
and test list ID.

Environment variables required:
- E2E_TEST_API_TOKEN: Valid ClickUp API token
- CLICKUP_TEST_LIST_ID: List ID for testing
"""

from test.config import TestSettings
from typing import AsyncGenerator

import pytest

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.models.dto.task import TaskCreate, TaskListQuery, TaskUpdate


class TestTaskCRUDE2E:
    """End-to-end tests for Task CRUD operations."""

    @pytest.fixture
    async def api_client(self, test_settings: TestSettings) -> AsyncGenerator[ClickUpAPIClient, None]:
        """Create a real ClickUpAPIClient using the API token from settings."""
        if not test_settings.e2e_test_api_token:
            pytest.skip("E2E_TEST_API_TOKEN is required for this test")

        assert test_settings.e2e_test_api_token
        api_token = test_settings.e2e_test_api_token.get_secret_value()
        async with ClickUpAPIClient(api_token=api_token) as client:
            yield client

    @pytest.mark.asyncio
    async def test_task_crud_operations(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test Task CRUD operations: Create, Read, Update, Delete."""
        list_id = test_settings.clickup_test_list_id
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID is required")
        assert list_id

        # Create a task
        task_create = TaskCreate(
            name="[TEST] Task CRUD Test",
            description="Test task for CRUD operations",
            priority=2,
            assignees=[],
        )
        created_task = await api_client.task.create(list_id, task_create)

        assert created_task is not None
        assert created_task.name == "[TEST] Task CRUD Test"
        task_id = created_task.id

        try:
            # Read the task
            retrieved_task = await api_client.task.get(task_id)
            assert retrieved_task is not None
            assert retrieved_task.id == task_id
            assert retrieved_task.name == "[TEST] Task CRUD Test"

            # Update the task
            task_update = TaskUpdate(name="[TEST] Updated Task", status="in progress")
            updated_task = await api_client.task.update(task_id, task_update)
            assert updated_task is not None
            assert updated_task.name == "[TEST] Updated Task"

        finally:
            # Delete the task
            delete_result = await api_client.task.delete(task_id)
            assert delete_result is True

    @pytest.mark.asyncio
    async def test_create_subtask(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test creating a subtask."""
        list_id = test_settings.clickup_test_list_id
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID is required")
        assert list_id

        # Create a parent task
        parent_task_create = TaskCreate(name="[TEST] Parent Task")
        parent_task = await api_client.task.create(list_id, parent_task_create)
        assert parent_task is not None
        parent_task_id = parent_task.id

        try:
            # Create a subtask
            subtask_create = TaskCreate(name="[TEST] Subtask", parent=parent_task_id)
            subtask = await api_client.task.create(list_id, subtask_create)

            assert subtask is not None
            assert subtask.name == "[TEST] Subtask"
            assert subtask.parent == parent_task_id

            # Clean up subtask
            await api_client.task.delete(subtask.id)

        finally:
            # Clean up parent task
            await api_client.task.delete(parent_task_id)

    @pytest.mark.asyncio
    async def test_list_tasks_in_list(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test listing tasks in a list."""
        list_id = test_settings.clickup_test_list_id
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID is required")
        assert list_id

        query = TaskListQuery(page=0, limit=10, include_closed=False)
        tasks = await api_client.task.list_in_list(list_id, query)

        assert tasks is not None
        assert isinstance(tasks, list)

    @pytest.mark.asyncio
    async def test_list_tasks_with_timl(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test listing tasks with TIML (Tasks in Multiple Lists) included."""
        list_id = test_settings.clickup_test_list_id
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID is required")
        assert list_id

        query = TaskListQuery(page=0, limit=10, include_timl=True)
        tasks = await api_client.task.list_in_list(list_id, query)

        assert tasks is not None
        assert isinstance(tasks, list)

    @pytest.mark.asyncio
    async def test_get_task_with_subtasks(self, api_client: ClickUpAPIClient, test_settings: TestSettings) -> None:
        """Test getting a task with subtasks included."""
        list_id = test_settings.clickup_test_list_id
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID is required")
        assert list_id

        # Create a task
        task_create = TaskCreate(name="[TEST] Task with Subtasks")
        task = await api_client.task.create(list_id, task_create)
        assert task is not None
        task_id = task.id

        try:
            # Get task with subtasks
            retrieved_task = await api_client.task.get(task_id, subtasks=True)
            assert retrieved_task is not None
            assert retrieved_task.id == task_id

        finally:
            await api_client.task.delete(task_id)

    @pytest.mark.asyncio
    async def test_task_with_due_date_and_time_estimate(
        self, api_client: ClickUpAPIClient, test_settings: TestSettings
    ) -> None:
        """Test creating a task with due date and time estimate."""
        list_id = test_settings.clickup_test_list_id
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID is required")
        assert list_id

        # Create a task with due date and time estimate
        import time

        due_date_ms = int((time.time() + 86400) * 1000)  # Tomorrow in milliseconds
        time_estimate_ms = 3600000  # 1 hour in milliseconds

        task_create = TaskCreate(
            name="[TEST] Task with Due Date",
            due_date=due_date_ms,
            time_estimate=time_estimate_ms,
        )
        task = await api_client.task.create(list_id, task_create)

        assert task is not None
        assert task.name == "[TEST] Task with Due Date"
        task_id = task.id

        try:
            # Verify the task was created with due date
            retrieved_task = await api_client.task.get(task_id)
            assert retrieved_task is not None
            assert retrieved_task.due_date is not None

        finally:
            await api_client.task.delete(task_id)
