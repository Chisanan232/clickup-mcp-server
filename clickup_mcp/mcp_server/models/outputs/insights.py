"""MCP output models for insights generation operations.

These models define the structure for insights generation results returned by MCP tools.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class InsightsGenerationResult(BaseModel):
    """Result for insights generation operations."""

    id: str = Field(description="Insights ID")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    insight_type: str = Field(description="Type of insight")
    priority: str = Field(description="Priority level (low, medium, high)")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Key metrics used to generate insights")
    confidence_score: int = Field(default=0, description="Confidence score of the insights (0-100)")
    date_generated: Optional[int] = Field(default=None, description="Generation date in epoch milliseconds")
