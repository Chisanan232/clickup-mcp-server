"""
Bottleneck detection DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Bottleneck
operations, including query parameters and response parsing. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create bottleneck detection query
    from clickup_mcp.models.dto.bottleneck import BottleneckDetectionQuery

    query = BottleneckDetectionQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    # => {"start_date": "1640995200000", "end_date": "1643673600000"}
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class BottleneckDetectionQuery(BaseRequestDTO):
    """
    DTO for bottleneck detection query parameters.

    API:
        GET /team/{team_id}/analytics/bottleneck

    Attributes:
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        list_id: Filter by list ID
        threshold: Threshold value for bottleneck detection
        bottleneck_type: Type of bottleneck to detect

    Examples:
        BottleneckDetectionQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    """

    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    list_id: str | None = Field(default=None, description="Filter by list ID")
    threshold: float | None = Field(default=None, description="Threshold value for bottleneck detection")
    bottleneck_type: str | None = Field(default=None, description="Type of bottleneck to detect")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        query["start_date"] = str(self.start_date)
        query["end_date"] = str(self.end_date)
        if self.list_id is not None:
            query["list_id"] = self.list_id
        if self.threshold is not None:
            query["threshold"] = str(self.threshold)
        if self.bottleneck_type is not None:
            query["bottleneck_type"] = self.bottleneck_type
        return query


class BottleneckDetectionResponse(BaseResponseDTO):
    """
    DTO for bottleneck detection API responses.

    API:
        GET /team/{team_id}/analytics/bottleneck

    Attributes:
        id: Detection ID
        team_id: Team/workspace ID
        list_id: Optional list ID for filtered detection
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        bottleneck_type: Type of bottleneck
        severity: Severity level (low, medium, high, critical)
        affected_tasks: Number of tasks affected by the bottleneck
        threshold: Threshold value that triggered the detection
        current_value: Current value that exceeded the threshold
        recommendations: Recommendations to resolve the bottleneck
        date_detected: Detection date in epoch milliseconds
        date_resolved: Resolution date in epoch milliseconds

    Examples:
        BottleneckDetectionResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Detection ID")
    team_id: str = Field(description="Team/workspace ID")
    list_id: str | None = Field(default=None, description="List ID for filtered detection")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    bottleneck_type: str = Field(description="Type of bottleneck")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    affected_tasks: int = Field(default=0, description="Number of tasks affected by the bottleneck")
    threshold: float | None = Field(default=None, description="Threshold value that triggered the detection")
    current_value: float | None = Field(default=None, description="Current value that exceeded the threshold")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations to resolve the bottleneck")
    date_detected: int | None = Field(default=None, description="Detection date in epoch milliseconds")
    date_resolved: int | None = Field(default=None, description="Resolution date in epoch milliseconds")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "BottleneckDetectionResponse":
        """
        Deserialize API response data into a BottleneckDetectionResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            BottleneckDetectionResponse: Deserialized DTO instance

        Examples:
            BottleneckDetectionResponse.deserialize({"id": "bd_1", "team_id": "t1", ...})
        """
        return cls(**data)
