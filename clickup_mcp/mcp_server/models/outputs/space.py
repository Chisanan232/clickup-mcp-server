"""Result models for Space tools."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SpaceResult(BaseModel):
    """Concise space detail for LLM planning."""

    id: str = Field(..., description="Space ID")
    name: str = Field(..., description="Space name")
    private: bool = Field(False, description="Whether the space is private")
    team_id: Optional[str] = Field(None, description="Workspace (team) ID")

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": "space_1", "name": "Engineering", "private": False, "team_id": "team_1"}]
        }
    }


class SpaceListItem(BaseModel):
    id: str = Field(..., description="Space ID")
    name: str = Field(..., description="Space name")


class SpaceListResult(BaseModel):
    items: List[SpaceListItem] = Field(default_factory=list, description="Spaces in the workspace")

    model_config = {"json_schema_extra": {"examples": [{"items": [{"id": "space_1", "name": "Engineering"}]}]}}
