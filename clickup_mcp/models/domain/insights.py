"""
Domain model for ClickUp Insights Generation.

Represents insights generation aggregates with business behaviors and invariants.
Insights generation provides actionable recommendations based on analytics data.

Domain Model Principles:
- Represents the core business entity independent of transport details
- Encapsulates business logic and invariants
- References other aggregates by ID only (no nested objects)
- Provides behavior methods that enforce domain rules
- Uses epoch milliseconds for time fields (vendor-agnostic)

Usage Examples:
    # Python - Create an insights generation domain entity
    from clickup_mcp.models.domain.insights import InsightsGeneration

    insights = InsightsGeneration(
        id="insights_123",
        team_id="team_001",
        start_date=1640995200000,
        end_date=1643673600000,
        insight_type="productivity",
        recommendations=["Reduce task switching"]
    )
"""

from typing import Dict, List, Optional

from pydantic import Field

from .base import BaseDomainModel


class InsightsGeneration(BaseDomainModel):
    """
    Domain model for insights generation with core behaviors and invariants.

    This model represents generated insights based on analytics data.
    It includes actionable recommendations to improve productivity and efficiency.

    In ClickUp's hierarchy:
    - Team (workspace) → Insights Generation

    Attributes:
        insights_id: The unique identifier for the insights (aliased as 'id' for compatibility)
        team_id: The ID of the team/workspace
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        insight_type: Type of insight (e.g., productivity, efficiency, workload)
        priority: Priority level (low, medium, high)
        recommendations: List of actionable recommendations
        metrics: Key metrics used to generate insights
        confidence_score: Confidence score of the insights (0-100)
        date_generated: Generation date in epoch milliseconds

    Key Design Features:
    - Backward-compatible 'id' property that returns insights_id
    - Behavior methods for confidence assessment
    - References other aggregates by ID only (no nested objects)
    - Uses epoch milliseconds for time fields (vendor-agnostic)
    - Immutable once created (inherited from BaseDomainModel)

    Usage Examples:
        # Python - Create from API response
        from clickup_mcp.models.domain.insights import InsightsGeneration

        insights = InsightsGeneration(
            id="insights_123",
            team_id="team_001",
            start_date=1640995200000,
            end_date=1643673600000,
            insight_type="productivity",
            recommendations=["Reduce task switching"]
        )

        # Python - Use domain behaviors
        is_high_confidence = insights.is_high_confidence()
    """

    insights_id: str = Field(alias="id", description="The unique identifier for the insights")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    insight_type: str = Field(description="Type of insight (e.g., 'productivity', 'efficiency', 'workload')")
    priority: str = Field(description="Priority level (low, medium, high)")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Key metrics used to generate insights")
    confidence_score: int = Field(default=0, description="Confidence score of the insights (0-100)")
    date_generated: int | None = Field(default=None, description="Generation date in epoch milliseconds")

    @property
    def id(self) -> str:
        """Get the insights ID for backward compatibility."""
        return self.insights_id

    def is_high_confidence(self) -> bool:
        """
        Check if the insights have high confidence.

        Returns:
            bool: True if confidence score is 80 or higher

        Usage Examples:
            insights = InsightsGeneration(id="ins_1", team_id="t1", start_date=1, end_date=2, confidence_score=85)
            insights.is_high_confidence()  # True
        """
        return self.confidence_score >= 80

    def is_high_priority(self) -> bool:
        """
        Check if the insights are high priority.

        Returns:
            bool: True if priority is high

        Usage Examples:
            insights = InsightsGeneration(id="ins_1", team_id="t1", start_date=1, end_date=2, priority="high")
            insights.is_high_priority()  # True
        """
        return self.priority.lower() == "high"

    def get_recommendation_count(self) -> int:
        """
        Get the number of recommendations.

        Returns:
            int: Number of recommendations

        Usage Examples:
            insights = InsightsGeneration(id="ins_1", team_id="t1", start_date=1, end_date=2, recommendations=["A", "B"])
            insights.get_recommendation_count()  # 2
        """
        return len(self.recommendations)
