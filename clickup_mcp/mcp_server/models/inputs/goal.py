"""MCP input models for goal CRUD operations.

High-signal schemas for FastMCP with constraints and examples.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GoalCreateInput(BaseModel):
    """
    Create a goal for a team. HTTP: POST /team/{team_id}/goal

    When to use: Create a new goal to track objectives and key results.

    Constraints:
        - `due_date` must be in the future (epoch milliseconds)
        - Time fields are epoch milliseconds

    Attributes:
        team_id: Team/workspace ID
        name: Goal name/title
        description: Optional description of the goal
        due_date: Due date in epoch ms
        key_results: Optional list of key result names
        multiple_owners: Whether multiple users can own this goal
        owners: List of user IDs who own this goal

    Examples:
        GoalCreateInput(team_id="team_1", name="Q1 Revenue Goal", description="Achieve $1M in revenue", due_date=1702080000000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "team_id": "team_1",
                    "name": "Q1 Revenue Goal",
                    "description": "Achieve $1M in revenue",
                    "due_date": 1702080000000,
                }
            ]
        }
    )

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    name: str = Field(
        ..., min_length=1, description="Goal name/title.", examples=["Q1 Revenue Goal", "Increase user retention"]
    )
    description: Optional[str] = Field(
        None, description="Description of the goal.", examples=["Achieve $1M in revenue", "Improve user onboarding"]
    )
    due_date: int = Field(..., description="Due date in epoch ms.", examples=[1702080000000, 1702166400000])
    key_results: Optional[list[str]] = Field(
        None, description="List of key result names.", examples=[["KR1", "KR2"], ["Increase MRR by 20%"]]
    )
    multiple_owners: bool = Field(
        default=False, description="Whether multiple users can own this goal.", examples=[True, False]
    )
    owners: Optional[list[str]] = Field(
        None, description="List of user IDs who own this goal.", examples=[["user_1", "user_2"]]
    )


class GoalGetInput(BaseModel):
    """
    Get a goal by ID. HTTP: GET /goal/{goal_id}

    When to use: Retrieve details of a specific goal.

    Attributes:
        goal_id: Goal ID

    Examples:
        GoalGetInput(goal_id="goal_123")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"goal_id": "goal_123"}]})

    goal_id: str = Field(..., min_length=1, description="Goal ID.", examples=["goal_123", "gl_abc"])


class GoalUpdateInput(BaseModel):
    """
    Update a goal. HTTP: PUT /goal/{goal_id}

    When to use: Modify goal details like name, description, due date, or owners.

    Constraints:
        - `due_date` must be in the future if provided
        - Time fields are epoch milliseconds

    Attributes:
        goal_id: Goal ID
        name: New goal name
        description: New description
        due_date: New due date in epoch ms
        key_results: New list of key result names
        owners: New list of user IDs who own this goal
        status: New goal status

    Examples:
        GoalUpdateInput(goal_id="goal_123", name="Updated Goal Name", due_date=1702166400000)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"goal_id": "goal_123", "name": "Updated Goal Name", "due_date": 1702166400000}]
        }
    )

    goal_id: str = Field(..., min_length=1, description="Goal ID.", examples=["goal_123", "gl_abc"])
    name: Optional[str] = Field(None, description="New goal name.", examples=["Updated Goal Name"])
    description: Optional[str] = Field(None, description="New description.", examples=["Updated description"])
    due_date: Optional[int] = Field(None, description="New due date in epoch ms.", examples=[1702166400000])
    key_results: Optional[list[str]] = Field(
        None, description="New list of key result names.", examples=[["KR1", "KR2"]]
    )
    owners: Optional[list[str]] = Field(None, description="New list of user IDs.", examples=[["user_1", "user_2"]])
    status: Optional[str] = Field(None, description="New goal status.", examples=["active", "completed", "paused"])


class GoalDeleteInput(BaseModel):
    """
    Delete a goal. HTTP: DELETE /goal/{goal_id}

    When to use: Remove a goal permanently.

    Attributes:
        goal_id: Goal ID

    Examples:
        GoalDeleteInput(goal_id="goal_123")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"goal_id": "goal_123"}]})

    goal_id: str = Field(..., min_length=1, description="Goal ID.", examples=["goal_123", "gl_abc"])


class GoalListInput(BaseModel):
    """
    List goals for a team with filters. HTTP: GET /team/{team_id}/goal

    When to use: Retrieve goals with optional filtering by status, owner, date range.

    Constraints:
        - `limit` ≤ 100 per API

    Attributes:
        team_id: Team/workspace ID
        status: Filter by goal status
        owner: Filter by user ID
        start_date: Filter by start date (epoch ms)
        end_date: Filter by end date (epoch ms)
        page: Page number (0-indexed)
        limit: Page size (cap 100)

    Examples:
        GoalListInput(team_id="team_1", status="active", limit=50)
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"team_id": "team_1", "status": "active", "limit": 50}]})

    team_id: str = Field(..., min_length=1, description="Team/workspace ID.", examples=["team_1", "9018752317"])
    status: Optional[str] = Field(
        None, description="Filter by goal status.", examples=["active", "completed", "paused"]
    )
    owner: Optional[str] = Field(None, description="Filter by user ID.", examples=["user_123", "usr_abc"])
    start_date: Optional[int] = Field(None, description="Filter by start date (epoch ms).", examples=[1702080000000])
    end_date: Optional[int] = Field(None, description="Filter by end date (epoch ms).", examples=[1702166400000])
    page: int = Field(0, ge=0, description="Page number (0-indexed).", examples=[0, 1, 2])
    limit: int = Field(100, ge=1, le=100, description="Page size (cap 100).", examples=[25, 50, 100])
