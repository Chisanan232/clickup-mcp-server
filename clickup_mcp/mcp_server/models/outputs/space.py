"""
Result models for Space tools.

These Pydantic models define concise, high-signal outputs returned by MCP tools
for Spaces. They are intentionally smaller than full ClickUp payloads and
optimized for LLM consumption, while preserving essential identifiers.

Usage Examples:
    # Python - Construct result for a single space
    from clickup_mcp.mcp_server.models.outputs.space import SpaceResult, SpaceListResult, SpaceListItem

    space = SpaceResult(id="space_1", name="Engineering", private=False, team_id="team_1")

    # Python - List result
    result = SpaceListResult(items=[SpaceListItem(id="space_1", name="Engineering")])

    # JSON - Example
    # {
    #   "items": [
    #     {"id": "space_1", "name": "Engineering"}
    #   ]
    # }
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SpaceResult(BaseModel):
    """
    Concise space detail for LLM planning.

    Attributes:
        id: Space ID
        name: Space name
        private: Whether the space is private
        team_id: Workspace (team) ID the space belongs to

    Notes:
        This model excludes heavy nested data to improve token efficiency.
    """

    id: str = Field(..., description="Space ID", examples=["space_1", "spc_abc"])
    name: str = Field(..., description="Space name", examples=["Engineering", "Delivery"])
    private: bool = Field(False, description="Whether the space is private", examples=[False])
    team_id: Optional[str] = Field(None, description="Workspace (team) ID", examples=["team_1", "9018752317"])

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": "space_1", "name": "Engineering", "private": False, "team_id": "team_1"}]
        }
    }


class SpaceListItem(BaseModel):
    """Item shape for space list results."""
    id: str = Field(..., description="Space ID", examples=["space_1", "spc_abc"])
    name: str = Field(..., description="Space name", examples=["Engineering", "Delivery"])


class SpaceListResult(BaseModel):
    """List wrapper for spaces returned from MCP tools."""
    items: List[SpaceListItem] = Field(
        default_factory=list,
        description="Spaces in the workspace",
        examples=[[{"id": "space_1", "name": "Engineering"}]],
    )

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "space_1", "name": "Engineering"}]}]}}
