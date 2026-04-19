"""Result models for Key Result tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.

Usage Examples:
    # Python - Single key result result
    from clickup_mcp.mcp_server.models.outputs.key_result import KeyResultResult

    kr = KeyResultResult(
        id="kr_1",
        goal_id="goal_789",
        name="Increase MRR",
        type="currency",
        target=1000000,
        current=500000,
        unit="$"
    )

    # Python - List result
    lr = KeyResultListResult(items=[KeyResultListItem(id="kr_1", goal_id="goal_789", name="Increase MRR", target=1000000, current=500000)])
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class KeyResultResult(BaseModel):
    """Concise key result detail; normalized units."""

    id: str = Field(..., description="Key result ID", examples=["kr_1", "kr_abc"])
    goal_id: str = Field(..., description="Goal ID", examples=["goal_789"])
    name: str = Field(..., description="Key result name", examples=["Increase MRR"])
    type: str = Field(..., description="Key result type", examples=["number", "currency", "boolean"])
    target: float = Field(..., description="Target value", examples=[1000000, 50.0])
    current: float = Field(default=0.0, description="Current value", examples=[500000, 25.0])
    unit: Optional[str] = Field(None, description="Unit of measurement", examples=["$", "%", "users"])
    description: Optional[str] = Field(None, description="Description", examples=["Monthly recurring revenue"])
    date_created: Optional[int] = Field(None, description="Creation date in epoch milliseconds", examples=[1702000000000])
    date_updated: Optional[int] = Field(None, description="Last update date in epoch milliseconds", examples=[1702100000000])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "kr_1",
                    "goal_id": "goal_789",
                    "name": "Increase MRR",
                    "type": "currency",
                    "target": 1000000,
                    "current": 500000,
                    "unit": "$",
                }
            ]
        }
    }


class KeyResultListItem(BaseModel):
    """
    Item shape for key result summaries returned by MCP tools.

    Attributes:
        id: Key result ID
        goal_id: Goal ID
        name: Key result name
        type: Key result type
        target: Target value
        current: Current value
        unit: Unit of measurement
    """

    id: str = Field(..., description="Key result ID", examples=["kr_1", "kr_abc"])
    goal_id: str = Field(..., description="Goal ID", examples=["goal_789"])
    name: str = Field(..., description="Key result name", examples=["Increase MRR"])
    type: str = Field(..., description="Key result type", examples=["number", "currency", "boolean"])
    target: float = Field(..., description="Target value", examples=[1000000, 50.0])
    current: float = Field(default=0.0, description="Current value", examples=[500000, 25.0])
    unit: Optional[str] = Field(None, description="Unit of measurement", examples=["$", "%", "users"])


class KeyResultListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[KeyResultListItem] = Field(
        default_factory=list,
        examples=[
            [
                {
                    "id": "kr_1",
                    "goal_id": "goal_789",
                    "name": "Increase MRR",
                    "type": "currency",
                    "target": 1000000,
                    "current": 500000,
                }
            ]
        ],
    )
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)", examples=["page=2"])
    truncated: bool = Field(False, description="True if items were trimmed to budget", examples=[False])
