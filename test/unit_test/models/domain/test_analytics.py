"""Unit tests for Analytics domain models."""

import pytest

from clickup_mcp.models.domain.analytics import (
    ListAnalytics,
    SpaceAnalytics,
    TaskAnalytics,
    TeamAnalytics,
)


class TestTaskAnalytics:
    """Test suite for TaskAnalytics domain model."""

    def test_task_analytics_creation(self):
        """Test creating task analytics with valid data."""
        analytics = TaskAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=100,
            completed_tasks=75,
        )

        assert analytics.analytics_id == "analytics_123"
        assert analytics.team_id == "team_456"
        assert analytics.total_tasks == 100
        assert analytics.completed_tasks == 75

    def test_backward_compatible_id_property(self):
        """Test that the id property returns analytics_id."""
        analytics = TaskAnalytics(
            id="analytics_123", team_id="team_456", start_date=1640995200000, end_date=1643673600000
        )
        assert analytics.id == "analytics_123"
        assert analytics.id == analytics.analytics_id

    def test_get_completion_rate(self):
        """Test calculating completion rate."""
        analytics = TaskAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=100,
            completed_tasks=75,
        )
        assert analytics.get_completion_rate() == 75.0

    def test_get_completion_rate_zero_tasks_raises_error(self):
        """Test that calculating completion rate with zero tasks raises ValueError."""
        analytics = TaskAnalytics(
            id="analytics_123", team_id="team_456", start_date=1640995200000, end_date=1643673600000
        )
        with pytest.raises(ValueError, match="Cannot calculate completion rate with zero total tasks"):
            analytics.get_completion_rate()

    def test_get_average_completion_time_hours(self):
        """Test getting average completion time in hours."""
        analytics = TaskAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            average_completion_time=86400000,  # 24 hours in milliseconds
        )
        assert analytics.get_average_completion_time_hours() == 24.0

    def test_get_average_completion_time_hours_none(self):
        """Test getting average completion time when None."""
        analytics = TaskAnalytics(
            id="analytics_123", team_id="team_456", start_date=1640995200000, end_date=1643673600000
        )
        assert analytics.get_average_completion_time_hours() is None


class TestTeamAnalytics:
    """Test suite for TeamAnalytics domain model."""

    def test_team_analytics_creation(self):
        """Test creating team analytics with valid data."""
        analytics = TeamAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=500,
            completed_tasks=400,
        )

        assert analytics.analytics_id == "analytics_123"
        assert analytics.team_id == "team_456"
        assert analytics.total_tasks == 500
        assert analytics.completed_tasks == 400

    def test_backward_compatible_id_property(self):
        """Test that the id property returns analytics_id."""
        analytics = TeamAnalytics(
            id="analytics_123", team_id="team_456", start_date=1640995200000, end_date=1643673600000
        )
        assert analytics.id == "analytics_123"
        assert analytics.id == analytics.analytics_id

    def test_get_completion_rate(self):
        """Test calculating completion rate."""
        analytics = TeamAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=500,
            completed_tasks=400,
        )
        assert analytics.get_completion_rate() == 80.0

    def test_get_completion_rate_zero_tasks_raises_error(self):
        """Test that calculating completion rate with zero tasks raises ValueError."""
        analytics = TeamAnalytics(
            id="analytics_123", team_id="team_456", start_date=1640995200000, end_date=1643673600000
        )
        with pytest.raises(ValueError, match="Cannot calculate completion rate with zero total tasks"):
            analytics.get_completion_rate()

    def test_get_tasks_per_user(self):
        """Test calculating tasks per user."""
        analytics = TeamAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=500,
            active_users=10,
        )
        assert analytics.get_tasks_per_user() == 50.0

    def test_get_tasks_per_user_zero_users_returns_none(self):
        """Test getting tasks per user when no active users."""
        analytics = TeamAnalytics(
            id="analytics_123",
            team_id="team_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=500,
            active_users=0,
        )
        assert analytics.get_tasks_per_user() is None


class TestListAnalytics:
    """Test suite for ListAnalytics domain model."""

    def test_list_analytics_creation(self):
        """Test creating list analytics with valid data."""
        analytics = ListAnalytics(
            id="analytics_123",
            list_id="list_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=50,
            completed_tasks=40,
        )

        assert analytics.analytics_id == "analytics_123"
        assert analytics.list_id == "list_456"
        assert analytics.total_tasks == 50
        assert analytics.completed_tasks == 40

    def test_backward_compatible_id_property(self):
        """Test that the id property returns analytics_id."""
        analytics = ListAnalytics(
            id="analytics_123", list_id="list_456", start_date=1640995200000, end_date=1643673600000
        )
        assert analytics.id == "analytics_123"
        assert analytics.id == analytics.analytics_id

    def test_get_completion_rate(self):
        """Test calculating completion rate."""
        analytics = ListAnalytics(
            id="analytics_123",
            list_id="list_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=50,
            completed_tasks=40,
        )
        assert analytics.get_completion_rate() == 80.0

    def test_get_completion_rate_zero_tasks_raises_error(self):
        """Test that calculating completion rate with zero tasks raises ValueError."""
        analytics = ListAnalytics(
            id="analytics_123", list_id="list_456", start_date=1640995200000, end_date=1643673600000
        )
        with pytest.raises(ValueError, match="Cannot calculate completion rate with zero total tasks"):
            analytics.get_completion_rate()

    def test_get_overdue_rate(self):
        """Test calculating overdue rate."""
        analytics = ListAnalytics(
            id="analytics_123",
            list_id="list_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=50,
            overdue_tasks=5,
        )
        assert analytics.get_overdue_rate() == 10.0

    def test_get_overdue_rate_zero_tasks_raises_error(self):
        """Test that calculating overdue rate with zero tasks raises ValueError."""
        analytics = ListAnalytics(
            id="analytics_123", list_id="list_456", start_date=1640995200000, end_date=1643673600000
        )
        with pytest.raises(ValueError, match="Cannot calculate overdue rate with zero total tasks"):
            analytics.get_overdue_rate()


class TestSpaceAnalytics:
    """Test suite for SpaceAnalytics domain model."""

    def test_space_analytics_creation(self):
        """Test creating space analytics with valid data."""
        analytics = SpaceAnalytics(
            id="analytics_123",
            space_id="space_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=200,
            completed_tasks=150,
        )

        assert analytics.analytics_id == "analytics_123"
        assert analytics.space_id == "space_456"
        assert analytics.total_tasks == 200
        assert analytics.completed_tasks == 150

    def test_backward_compatible_id_property(self):
        """Test that the id property returns analytics_id."""
        analytics = SpaceAnalytics(
            id="analytics_123", space_id="space_456", start_date=1640995200000, end_date=1643673600000
        )
        assert analytics.id == "analytics_123"
        assert analytics.id == analytics.analytics_id

    def test_get_completion_rate(self):
        """Test calculating completion rate."""
        analytics = SpaceAnalytics(
            id="analytics_123",
            space_id="space_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=200,
            completed_tasks=150,
        )
        assert analytics.get_completion_rate() == 75.0

    def test_get_completion_rate_zero_tasks_raises_error(self):
        """Test that calculating completion rate with zero tasks raises ValueError."""
        analytics = SpaceAnalytics(
            id="analytics_123", space_id="space_456", start_date=1640995200000, end_date=1643673600000
        )
        with pytest.raises(ValueError, match="Cannot calculate completion rate with zero total tasks"):
            analytics.get_completion_rate()

    def test_get_average_tasks_per_list(self):
        """Test calculating average tasks per list."""
        analytics = SpaceAnalytics(
            id="analytics_123",
            space_id="space_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=200,
            total_lists=10,
        )
        assert analytics.get_average_tasks_per_list() == 20.0

    def test_get_average_tasks_per_list_zero_lists_returns_none(self):
        """Test getting average tasks per list when no lists."""
        analytics = SpaceAnalytics(
            id="analytics_123",
            space_id="space_456",
            start_date=1640995200000,
            end_date=1643673600000,
            total_tasks=200,
            total_lists=0,
        )
        assert analytics.get_average_tasks_per_list() is None
