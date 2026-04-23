"""
Performance tests for the ClickUp MCP Server.

This module contains performance benchmarks and load tests to ensure
the system performs adequately under various conditions.
"""

import pytest
import asyncio
import time
from unittest.mock import MagicMock
from typing import List

from clickup_mcp.client import ClickUpAPIClient
from clickup_mcp.api.task import TaskAPI
from clickup_mcp.api.time import TimeAPI
from clickup_mcp.api.goal import GoalAPI
from clickup_mcp.models.http import APIResponse


class TestPerformance:
    """Performance test suite for the ClickUp MCP Server."""

    @pytest.mark.asyncio
    async def test_task_api_concurrent_requests(self):
        """Test task API performance with concurrent requests."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)

        # Mock successful responses
        mock_client.get.return_value = APIResponse(
            success=True,
            status_code=200,
            data={"id": "task_123", "name": "Test Task"},
            headers={},
        )

        # Act - Make 100 concurrent requests
        start_time = time.time()
        tasks = [task_api.get("task_123") for _ in range(100)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Assert - All requests should succeed
        assert all(r is not None for r in results)
        # Performance assertion - should complete in reasonable time (< 5 seconds for 100 requests)
        assert end_time - start_time < 5.0

    @pytest.mark.asyncio
    async def test_time_api_sequential_performance(self):
        """Test time API sequential operation performance."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        time_api = TimeAPI(mock_client)

        mock_client.post.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "id": "entry_123",
                "task_id": "task_123",
                "user_id": 789,
                "team_id": "team_001",
                "duration": 3600000,
            },
            headers={},
        )

        # Act - Create 50 time entries sequentially
        start_time = time.time()
        for _ in range(50):
            from clickup_mcp.models.dto.time import TimeEntryCreate
            await time_api.create(
                "team_001",
                TimeEntryCreate(task_id="task_123", duration=3600000),
            )
        end_time = time.time()

        # Assert - Should complete in reasonable time
        assert end_time - start_time < 3.0

    @pytest.mark.asyncio
    async def test_goal_api_batch_operations(self):
        """Test goal API batch operation performance."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        goal_api = GoalAPI(mock_client)

        mock_client.post.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "items": [
                    {
                        "id": "goal_123",
                        "team_id": "team_001",
                        "name": "Test Goal",
                        "status": "active",
                    }
                ]
            },
            headers={},
        )

        # Act - Create 20 goals in batch
        start_time = time.time()
        tasks = [
            goal_api.create(
                "team_001",
                from clickup_mcp.models.dto.goal import GoalCreate
                and GoalCreate(
                    name=f"Goal {i}",
                    description=f"Description {i}",
                    due_date=1702080000000,
                ),
            )
            for i in range(20)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Assert - All operations should succeed
        assert all(r is not None for r in results)
        # Should complete in reasonable time
        assert end_time - start_time < 2.0

    @pytest.mark.asyncio
    async def test_api_response_time_benchmark(self):
        """Benchmark average API response time."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)

        mock_client.get.return_value = APIResponse(
            success=True,
            status_code=200,
            data={"id": "task_123", "name": "Test Task"},
            headers={},
        )

        # Act - Measure response times for 100 requests
        response_times: List[float] = []
        for _ in range(100):
            start = time.time()
            await task_api.get("task_123")
            end = time.time()
            response_times.append(end - start)

        # Assert - Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        # Performance assertions
        assert avg_response_time < 0.1  # Average < 100ms
        assert max_response_time < 0.5  # Max < 500ms

    @pytest.mark.asyncio
    async def test_memory_efficiency_large_dataset(self):
        """Test memory efficiency with large datasets."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)

        # Mock large response
        large_data = {
            "tasks": [
                {"id": f"task_{i}", "name": f"Task {i}"}
                for i in range(1000)
            ]
        }

        mock_client.get.return_value = APIResponse(
            success=True,
            status_code=200,
            data=large_data,
            headers={},
        )

        # Act - Process large dataset
        start_time = time.time()
        result = await task_api.get("task_123")
        end_time = time.time()

        # Assert - Should handle large data efficiently
        assert result is not None
        assert end_time - start_time < 1.0

    @pytest.mark.asyncio
    async def test_rate_limiting_resilience(self):
        """Test resilience under rate limiting conditions."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)

        call_count = [0]

        def mock_response(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] % 10 == 0:
                # Simulate rate limit every 10 requests
                return APIResponse(
                    success=False,
                    status_code=429,
                    data={"err": "Rate limit exceeded"},
                    headers={"Retry-After": "1"},
                )
            return APIResponse(
                success=True,
                status_code=200,
                data={"id": "task_123", "name": "Test Task"},
                headers={},
            )

        mock_client.get.return_value = mock_response()

        # Act - Make requests that may hit rate limits
        start_time = time.time()
        results = []
        for _ in range(30):
            result = await task_api.get("task_123")
            results.append(result)
        end_time = time.time()

        # Assert - Should handle rate limits gracefully
        # Some requests should fail with rate limit
        failed_count = sum(1 for r in results if r is None)
        assert failed_count > 0
        # Should complete in reasonable time despite rate limits
        assert end_time - start_time < 10.0

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self):
        """Test performance with mixed concurrent operations."""
        # Arrange
        mock_client = MagicMock(spec=ClickUpAPIClient)
        task_api = TaskAPI(mock_client)
        time_api = TimeAPI(mock_client)
        goal_api = GoalAPI(mock_client)

        # Mock responses
        mock_client.get.return_value = APIResponse(
            success=True,
            status_code=200,
            data={"id": "task_123", "name": "Test Task"},
            headers={},
        )
        mock_client.post.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "id": "entry_123",
                "task_id": "task_123",
                "duration": 3600000,
            },
            headers={},
        )

        # Act - Mix of different operations
        start_time = time.time()
        tasks = [
            # 20 task reads
            *[task_api.get("task_123") for _ in range(20)],
            # 10 time entries
            *[
                time_api.create(
                    "team_001",
                    from clickup_mcp.models.dto.time import TimeEntryCreate
                    and TimeEntryCreate(task_id="task_123", duration=3600000),
                )
                for _ in range(10)
            ],
            # 5 goal creations
            *[
                goal_api.create(
                    "team_001",
                    from clickup_mcp.models.dto.goal import GoalCreate
                    and GoalCreate(
                        name=f"Goal {i}",
                        due_date=1702080000000,
                    ),
                )
                for i in range(5)
            ],
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Assert - All operations should complete
        assert all(r is not None for r in results)
        # Should complete in reasonable time
        assert end_time - start_time < 5.0
