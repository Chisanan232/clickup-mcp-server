"""
Integration tests for API components.

This module tests the integration of different API components to ensure
they work together properly in a realistic scenario with minimal mocking.
"""

import pytest
from unittest.mock import MagicMock

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.api.task import TaskAPI
from clickup_mcp.api.time import TimeAPI
from clickup_mcp.api.goal import GoalAPI
from clickup_mcp.api.workflow import WorkflowAPI
from clickup_mcp.api.analytics import AnalyticsAPI
from clickup_mcp.models.http import APIResponse


class TestAPIIntegration:
    """Integration test suite for API components."""

    @pytest.mark.asyncio
    async def test_task_and_time_integration(self):
        """Test integration between task and time tracking APIs."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)
        time_api = TimeAPI(mock_client)

        # Mock responses
        mock_client.post.side_effect = [
            APIResponse(
                success=True,
                status_code=200,
                data={
                    "id": "task_123",
                    "name": "Test Task",
                    "description": "Test Description",
                },
                headers={},
            ),
            APIResponse(
                success=True,
                status_code=200,
                data={
                    "id": "entry_123",
                    "task_id": "task_123",
                    "user_id": 789,
                    "team_id": "team_001",
                    "description": "Test work",
                    "duration": 3600000,
                },
                headers={},
            ),
        ]

        # Act - Create a task and log time against it
        from clickup_mcp.models.dto.task import TaskCreate
        from clickup_mcp.models.dto.time import TimeEntryCreate

        task = await task_api.create(TaskCreate(name="Test Task", list_id="list_123"))
        time_entry = await time_api.create(
            "team_001",
            TimeEntryCreate(task_id="task_123", description="Test work", duration=3600000),
        )

        # Assert - Both operations should succeed
        assert task is not None
        assert time_entry is not None
        assert time_entry.task_id == "task_123"

    @pytest.mark.asyncio
    async def test_goal_and_key_result_integration(self):
        """Test integration between goal and key result APIs."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        goal_api = GoalAPI(mock_client)

        # Mock goal creation response
        mock_client.post.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "items": [
                    {
                        "id": "goal_123",
                        "team_id": "team_001",
                        "name": "Q1 Revenue Goal",
                        "description": "Achieve $1M in revenue",
                        "due_date": 1702080000000,
                        "status": "active",
                        "key_results": ["KR1", "KR2"],
                    }
                ]
            },
            headers={},
        )

        # Act - Create a goal with key results
        from clickup_mcp.models.dto.goal import GoalCreate

        goal = await goal_api.create(
            "team_001",
            GoalCreate(
                name="Q1 Revenue Goal",
                description="Achieve $1M in revenue",
                due_date=1702080000000,
                key_results=["KR1", "KR2"],
            ),
        )

        # Assert - Goal should be created with key results
        assert goal is not None
        assert len(goal.items) == 1
        assert goal.items[0].key_results == ["KR1", "KR2"]

    @pytest.mark.asyncio
    async def test_workflow_and_task_integration(self):
        """Test integration between workflow and task APIs."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        workflow_api = WorkflowAPI(mock_client)
        task_api = TaskAPI(mock_client)

        # Mock workflow creation response
        mock_client.post.side_effect = [
            APIResponse(
                success=True,
                status_code=200,
                data={
                    "items": [
                        {
                            "id": "wf_123",
                            "team_id": "team_001",
                            "name": "Auto-assign on create",
                            "trigger_type": "task_created",
                            "trigger_config": {"list_id": "456"},
                            "actions": [{"type": "assign", "user_id": "789"}],
                            "is_active": True,
                        }
                    ],
                    "page": 0,
                    "limit": 100,
                },
                headers={},
            ),
            APIResponse(
                success=True,
                status_code=200,
                data={
                    "id": "task_123",
                    "name": "Test Task",
                    "description": "Test Description",
                    "assignees": [{"id": 789}],
                },
                headers={},
            ),
        ]

        # Act - Create a workflow and then create a task that triggers it
        from clickup_mcp.models.dto.workflow import WorkflowCreate
        from clickup_mcp.models.dto.task import TaskCreate

        workflow = await workflow_api.create(
            "team_001",
            WorkflowCreate(
                name="Auto-assign on create",
                trigger_type="task_created",
                trigger_config={"list_id": "456"},
                actions=[{"type": "assign", "user_id": "789"}],
            ),
        )

        task = await task_api.create(TaskCreate(name="Test Task", list_id="456"))

        # Assert - Both operations should succeed
        assert workflow is not None
        assert task is not None
        assert workflow.items[0].trigger_type == "task_created"

    @pytest.mark.asyncio
    async def test_analytics_and_task_integration(self):
        """Test integration between analytics and task APIs."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        analytics_api = AnalyticsAPI(mock_client)
        task_api = TaskAPI(mock_client)

        # Mock responses
        mock_client.get.return_value = {"data": {"id": "a1", "team_id": "team_001", "total_tasks": 100}}
        mock_client.post.return_value = APIResponse(
            success=True,
            status_code=200,
            data={"id": "task_123", "name": "Test Task"},
            headers={},
        )

        # Act - Create tasks and then get analytics
        from clickup_mcp.models.dto.task import TaskCreate
        from clickup_mcp.models.dto.analytics import TaskAnalyticsQuery

        task1 = await task_api.create(TaskCreate(name="Task 1", list_id="list_123"))
        task2 = await task_api.create(TaskCreate(name="Task 2", list_id="list_123"))

        analytics = await analytics_api.get_task_analytics(
            "team_001",
            TaskAnalyticsQuery(start_date=1640995200000, end_date=1643673600000),
        )

        # Assert - Tasks should be created and analytics should be available
        assert task1 is not None
        assert task2 is not None
        assert analytics is not None
        assert analytics.total_tasks == 100

    @pytest.mark.asyncio
    async def test_multi_api_workflow(self):
        """Test a complete workflow using multiple APIs together."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)
        time_api = TimeAPI(mock_client)
        goal_api = GoalAPI(mock_client)

        # Mock responses
        call_count = [0]

        def mock_response_generator(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # Create task
                return APIResponse(
                    success=True,
                    status_code=200,
                    data={"id": "task_123", "name": "Test Task"},
                    headers={},
                )
            elif call_count[0] == 2:  # Start tracking
                return APIResponse(success=True, status_code=200, data=None, headers={})
            elif call_count[0] == 3:  # Stop tracking
                return APIResponse(success=True, status_code=200, data=None, headers={})
            elif call_count[0] == 4:  # Create goal
                return APIResponse(
                    success=True,
                    status_code=200,
                    data={
                        "items": [
                            {
                                "id": "goal_123",
                                "team_id": "team_001",
                                "name": "Complete Project",
                                "status": "active",
                            }
                        ]
                    },
                    headers={},
                )
            return APIResponse(success=True, status_code=200, data=None, headers={})

        mock_client.post.side_effect = mock_response_generator

        # Act - Complete workflow: create task, track time, create goal
        from clickup_mcp.models.dto.task import TaskCreate
        from clickup_mcp.models.dto.goal import GoalCreate

        task = await task_api.create(TaskCreate(name="Test Task", list_id="list_123"))
        tracking_started = await time_api.start_tracking("task_123")
        tracking_stopped = await time_api.stop_tracking("task_123", "Completed work")
        goal = await goal_api.create(
            "team_001",
            GoalCreate(
                name="Complete Project",
                description="Complete the project on time",
                due_date=1702080000000,
            ),
        )

        # Assert - All operations should succeed
        assert task is not None
        assert tracking_started is True
        assert tracking_stopped is True
        assert goal is not None
        assert goal.items[0].name == "Complete Project"
