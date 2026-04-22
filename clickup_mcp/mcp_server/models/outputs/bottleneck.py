"""MCP output models for bottleneck detection operations.

These models define the structure for bottleneck detection results returned by MCP tools.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class BottleneckDetectionResult(BaseModel):
    """Result for bottleneck detection operations."""

    id: str = Field(description="Detection ID")
    team_id: str = Field(description="Team/workspace ID")
    list_id: Optional[str] = Field(default=None, description="List ID for filtered detection")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    bottleneck_type: str = Field(description="Type of bottleneck")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    affected_tasks: int = Field(default=0, description="Number of tasks affected by the bottleneck")
    threshold: Optional[float] = Field(default=None, description="Threshold value that triggered the detection")
    current_value: Optional[float] = Field(default=None, description="Current value that exceeded the threshold")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations to resolve the bottleneck")
    date_detected: Optional[int] = Field(default=None, description="Detection date in epoch milliseconds")
    date_resolved: Optional[int] = Field(default=None, description="Resolution date in epoch milliseconds")
