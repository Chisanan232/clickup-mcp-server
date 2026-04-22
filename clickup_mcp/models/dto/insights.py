"""
Insights generation DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Insights
operations, including query parameters and response parsing. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create insights generation query
    from clickup_mcp.models.dto.insights import InsightsGenerationQuery

    query = InsightsGenerationQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    # => {"start_date": "1640995200000", "end_date": "1643673600000"}
"""

from typing import Any, Dict, List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class InsightsGenerationQuery(BaseRequestDTO):
    """
    DTO for insights generation query parameters.

    API:
        GET /team/{team_id}/analytics/insights

    Attributes:
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        insight_type: Type of insight to generate

    Examples:
        InsightsGenerationQuery(start_date=1640995200000, end_date=1643673600000).to_query()
    """

    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    insight_type: str = Field(description="Type of insight to generate")

    def to_query(self) -> Dict[str, str]:
        """
        Convert the DTO into ClickUp query parameters.

        Returns:
            Dict[str, str]: Query parameters as string values.
        """
        query: Dict[str, str] = {}
        query["start_date"] = str(self.start_date)
        query["end_date"] = str(self.end_date)
        query["insight_type"] = self.insight_type
        return query


class InsightsGenerationResponse(BaseResponseDTO):
    """
    DTO for insights generation API responses.

    API:
        GET /team/{team_id}/analytics/insights

    Attributes:
        id: Insights ID
        team_id: Team/workspace ID
        start_date: Start date in epoch milliseconds
        end_date: End date in epoch milliseconds
        insight_type: Type of insight
        priority: Priority level (low, medium, high)
        recommendations: Actionable recommendations
        metrics: Key metrics used to generate insights
        confidence_score: Confidence score of the insights (0-100)
        date_generated: Generation date in epoch milliseconds

    Examples:
        InsightsGenerationResponse.deserialize(api_response_data)
    """

    id: str = Field(description="Insights ID")
    team_id: str = Field(description="Team/workspace ID")
    start_date: int = Field(description="Start date in epoch milliseconds")
    end_date: int = Field(description="End date in epoch milliseconds")
    insight_type: str = Field(description="Type of insight")
    priority: str = Field(description="Priority level (low, medium, high)")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Key metrics used to generate insights")
    confidence_score: int = Field(default=0, description="Confidence score of the insights (0-100)")
    date_generated: int | None = Field(default=None, description="Generation date in epoch milliseconds")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "InsightsGenerationResponse":
        """
        Deserialize API response data into an InsightsGenerationResponse DTO.

        Args:
            data: Raw API response data

        Returns:
            InsightsGenerationResponse: Deserialized DTO instance

        Examples:
            InsightsGenerationResponse.deserialize({"id": "ins_1", "team_id": "t1", ...})
        """
        return cls(**data)
