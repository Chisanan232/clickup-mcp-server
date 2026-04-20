"""
Domain model for ClickUp Bottleneck Detection.

Represents bottleneck detection aggregates with business behaviors and invariants.
Bottleneck detection identifies process bottlenecks in task workflows and team productivity.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants (e.g., threshold validation)
- References other aggregates by ID only (no nested objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create a bottleneck detection domain entity
    from clickup_mcp.models.domain.bottleneck import BottleneckDetection

    detection = BottleneckDetection(
        id="bd_123",
        team_id="team_001",
        start_date=1640995200000,
        end_date=1643673600000,
        bottleneck_type="status_stuck",
        severity="high"
    )

    # Python - Use domain behaviors
    is_critical = detection.is_critical()
"""

from typing import Dict, List, Optional

from pydantic import Field

from .base import BaseDomainModel


class BottleneckDetection(BaseDomainModel):
    """
    Domain model for bottleneck detection with core behaviors and invariants.

    This model represents detected bottlenecks in task workflows and team productivity.
    It includes metrics for identifying and categorizing bottlenecks.

    In ClickUp's hierarchy:
    - Team (workspace) → Bottleneck Detection

    Attributes:
        detection_id: The unique identifier for the detection (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace
        list_id: Optional list ID for filtered detection
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        bottleneck_type: Type of bottleneck (e.g., status_stuck, assignee_overload, list_backlog)
        severity: Severity level (low, medium, high, critical)
        affected_tasks: Number of tasks affected by the bottleneck
        threshold: Threshold value that triggered the detection
        current_value: Current value that exceeded the threshold
        recommendations: List of recommendations to resolve the bottleneck
        date_detected: Detection date in epoch milliseconds
        date_resolved: Resolution date in epoch milliseconds (if resolved)

    Key Design Features:
    - Backward-compatible 'id' property that returns detection_id
    - Behavior methods for severity assessment
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.bottleneck import BottleneckDetection

        detection = BottleneckDetection(
            id="bd_123",
            team_id="team_001",
            start_date=1640995200000,
            end_date=1643673600000,
            bottleneck_type="status_stuck",
            severity="high",
            affected_tasks=25
        )

        # Python - Use domain behaviors
        is_critical = detection.is_critical()
    """

    detection_id: str = Field(alias="id", description="The unique identifier for the detection")
    team_id: str = Field(description="Team/workspace ID")
    list_id: Optional[str] = Field(default=None, description="List ID for filtered detection")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    bottleneck_type: str = Field(description="Type of bottleneck (e.g., 'status_stuck', 'assignee_overload', 'list_backlog')")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    affected_tasks: int = Field(default=0, description="Number of tasks affected by the bottleneck")
    threshold: Optional[float] = Field(default=None, description="Threshold value that triggered the detection")
    current_value: Optional[float] = Field(default=None, description="Current value that exceeded the threshold")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations to resolve the bottleneck")
    date_detected: int | None = Field(default=None, description="Detection date in epoch milliseconds")
    date_resolved: int | None = Field(default=None, description="Resolution date in epoch milliseconds")

    @property
    def id(self) -> str:
        """Get the detection ID for backward compatibility."""
        return self.detection_id

    def is_critical(self) -> bool:
        """
        Check if the bottleneck is critical.

        Returns:
            bool: True if severity is critical

        Usage Examples:
            detection = BottleneckDetection(id="bd_1", team_id="t1", start_date=1, end_date=2, severity="critical")
            detection.is_critical()  # True
        """
        return self.severity.lower() == "critical"

    def is_high_severity(self) -> bool:
        """
        Check if the bottleneck has high severity or higher.

        Returns:
            bool: True if severity is high or critical

        Usage Examples:
            detection = BottleneckDetection(id="bd_1", team_id="t1", start_date=1, end_date=2, severity="high")
            detection.is_high_severity()  # True
        """
        return self.severity.lower() in ["high", "critical"]

    def is_resolved(self) -> bool:
        """
        Check if the bottleneck has been resolved.

        Returns:
            bool: True if date_resolved is set

        Usage Examples:
            detection = BottleneckDetection(id="bd_1", team_id="t1", start_date=1, end_date=2, date_resolved=3)
            detection.is_resolved()  # True
        """
        return self.date_resolved is not None

    def get_affected_task_percentage(self, total_tasks: int) -> float:
        """
        Calculate the percentage of tasks affected by the bottleneck.

        Args:
            total_tasks: Total number of tasks in the scope

        Returns:
            float: Percentage of affected tasks (0-100)

        Raises:
            ValueError: If total_tasks is zero

        Usage Examples:
            detection = BottleneckDetection(id="bd_1", team_id="t1", start_date=1, end_date=2, affected_tasks=25)
            percentage = detection.get_affected_task_percentage(100)  # 25.0
        """
        if total_tasks == 0:
            raise ValueError("Cannot calculate percentage with zero total tasks")
        return (self.affected_tasks / total_tasks) * 100
