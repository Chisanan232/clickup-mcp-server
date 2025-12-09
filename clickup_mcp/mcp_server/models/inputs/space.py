"""MCP input models for space operations.

High-signal schemas for FastMCP: include constraints and examples to aid LLMs.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SpaceCreateInput(BaseModel):
    """
    Create a space. HTTP: POST /team/{team_id}/space

    When to use: You have a workspace (`team_id`) and want to create a new space.
    Notes: Features provisioning is typically managed separately; this tool sets core fields.

    Attributes:
        team_id: Target workspace (team) ID
        name: Space name
        multiple_assignees: Whether tasks can have multiple assignees

    Examples:
        SpaceCreateInput(team_id="team_1", name="[TEST] Eng", multiple_assignees=True)
    """

    model_config = {
        "json_schema_extra": {"examples": [{"team_id": "team_1", "name": "[TEST] Eng", "multiple_assignees": True}]}
    }

    team_id: str = Field(
        ..., min_length=1, description="Target workspace (team) ID.", examples=["9018752317", "team_1"]
    )
    name: str = Field(..., min_length=1, description="Space name.", examples=["[TEST] Eng", "Platform", "Delivery"])
    multiple_assignees: Optional[bool] = Field(
        None,
        description="Allow multiple assignees for tasks in this space.",
        examples=[True, False],
    )


class SpaceGetInput(BaseModel):
    """
    Get a space. HTTP: GET /space/{space_id}

    When to use: Retrieve details for a single space by ID.

    Attributes:
        space_id: Space ID

    Examples:
        SpaceGetInput(space_id="space_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"space_id": "space_1"}]}}

    space_id: str = Field(..., min_length=1, description="Space ID.", examples=["space_1", "abc123"])


class SpaceUpdateInput(BaseModel):
    """
    Update a space. HTTP: PUT /space/{space_id}

    When to use: Change core attributes like name/privacy/multiple-assignees.

    Attributes:
        space_id: Space ID
        name: New space name
        private: Whether the space is private
        multiple_assignees: Whether tasks can have multiple assignees

    Examples:
        SpaceUpdateInput(space_id="space_1", name="Delivery", private=False)
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"space_id": "space_1", "name": "Delivery", "private": False},
                {"space_id": "space_1", "multiple_assignees": True},
            ]
        }
    }

    space_id: str = Field(..., min_length=1, description="Space ID.", examples=["space_1", "abc123"])
    name: Optional[str] = Field(None, min_length=1, description="Space name.", examples=["Delivery", "Engineering"])
    private: Optional[bool] = Field(None, description="Whether the space is private.", examples=[True, False])
    multiple_assignees: Optional[bool] = Field(
        None, description="Allow multiple assignees for tasks.", examples=[True, False]
    )


class SpaceDeleteInput(BaseModel):
    """
    Delete a space. HTTP: DELETE /space/{space_id}

    When to use: Permanently remove a space. Ensure no critical data is lost.

    Attributes:
        space_id: Space ID

    Examples:
        SpaceDeleteInput(space_id="space_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"space_id": "space_1"}]}}

    space_id: str = Field(..., min_length=1, description="Space ID.", examples=["space_1", "abc123"])


class SpaceListInput(BaseModel):
    """
    List spaces in a workspace. HTTP: GET /team/{team_id}/space

    When to use: Discover spaces within a specific workspace (team).

    Attributes:
        team_id: Workspace (team) ID

    Examples:
        SpaceListInput(team_id="team_1")
    """

    model_config = {"json_schema_extra": {"examples": [{"team_id": "team_1"}]}}

    team_id: str = Field(..., min_length=1, description="Workspace (team) ID.", examples=["9018752317", "team_1"])
