"""
Result models for Goal tools.

Concise shapes for LLM planning; no raw ClickUp payloads leak.

Usage Examples:
    # Python - Single goal result
    from clickup_mcp.mcp_server.models.outputs.goal import GoalResult

    g = GoalResult(
        id="goal_1",
        team_id="team_789",
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
        status="active"
    )

    # Python - List result
    lr = GoalListResult(items=[GoalListItem(id="goal_1", team_id="team_789", name="Q1 Revenue Goal", due_date=1702080000000, status="active")])
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class GoalResult(BaseModel):
    """Concise goal detail; normalized units."""

    id: str = Field(..., description="Goal ID", examples=["goal_1", "gl_123"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    name: str = Field(..., description="Goal name/title", examples=["Q1 Revenue Goal"])
    description: Optional[str] = Field(None, description="Description of the goal", examples=["Achieve $1M in revenue"])
    due_date: Optional[int] = Field(None, ge=0, description="Due date in epoch milliseconds", examples=[1702080000000])
    status: str = Field(..., description="Goal status", examples=["active", "completed", "paused"])
    key_results: List[str] = Field(default_factory=list, description="List of key result names", examples=[["KR1", "KR2"]])
    owners: List[str] = Field(default_factory=list, description="List of user IDs who own this goal", examples=[["user_1", "user_2"]])
    multiple_owners: bool = Field(default=False, description="Whether multiple users can own this goal", examples=[True, False])
    date_created: Optional[int] = Field(None, description="Creation date in epoch milliseconds", examples=[1702000000000])
    date_updated: Optional[int] = Field(None, description="Last update date in epoch milliseconds", examples=[1702100000000])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "goal_1",
                    "team_id": "team_789",
                    "name": "Q1 Revenue Goal",
                    "description": "Achieve $1M in revenue",
                    "due_date": 1702080000000,
                    "status": "active",
                }
            ]
        }
    }


class GoalListItem(BaseModel):
    """
    Item shape for goal summaries returned by MCP tools.

    Attributes:
        id: Goal ID
        team_id: Team/workspace ID
        name: Goal name/title
        description: Description of the goal
        due_date: Due date in epoch milliseconds
        status: Goal status
    """

    id: str = Field(..., description="Goal ID", examples=["goal_1", "gl_123"])
    team_id: str = Field(..., description="Team/workspace ID", examples=["team_789"])
    name: str = Field(..., description="Goal name/title", examples=["Q1 Revenue Goal"])
    description: Optional[str] = Field(None, description="Description of the goal", examples=["Achieve $1M in revenue"])
    due_date: Optional[int] = Field(None, ge=0, description="Due date in epoch milliseconds", examples=[1702080000000])
    status: str = Field(..., description="Goal status", examples=["active", "completed", "paused"])


class GoalListResult(BaseModel):
    """Paged listing, capped to API limit; includes cursor."""

    items: List[GoalListItem] = Field(
        default_factory=list,
        examples=[
            [
                {
                    "id": "goal_1",
                    "team_id": "team_789",
                    "name": "Q1 Revenue Goal",
                    "due_date": 1702080000000,
                    "status": "active",
                }
            ]
        ],
    )
    next_cursor: Optional[str] = Field(None, description="Pass to fetch next page (if present)", examples=["page=2"])
    truncated: bool = Field(False, description="True if items were trimmed to budget", examples=[False])
