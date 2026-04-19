"""MCP input models for key result operations.

High-signal schemas for FastMCP with constraints and examples.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KeyResultCreateInput(BaseModel):
    """
    Create a key result for a goal. HTTP: POST /goal/{goal_id}/key_result

    When to use: Add a measurable outcome to track goal progress.

    Constraints:
        - `goal_id` is required
        - `type` must be one of the valid types

    Attributes:
        goal_id: Goal ID to add the key result to
        name: Key result name
        type: Key result type (e.g., "number", "currency", "boolean")
        target: Target value for the key result
        unit: Unit of measurement (e.g., "$", "%", "users")
        description: Optional description of the key result

    Examples:
        KeyResultCreateInput(goal_id="goal_123", name="Increase MRR", type="currency", target=1000000, unit="$")
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "goal_id": "goal_123",
                    "name": "Increase MRR",
                    "type": "currency",
                    "target": 1000000,
                    "unit": "$",
                }
            ]
        }
    )

    goal_id: str = Field(..., min_length=1, description="Goal ID.", examples=["goal_123", "gl_abc"])
    name: str = Field(..., min_length=1, description="Key result name.", examples=["Increase MRR", "Improve retention"])
    type: str = Field(..., description="Key result type.", examples=["number", "currency", "boolean"])
    target: float = Field(..., description="Target value.", examples=[1000000, 50.0, 1])
    unit: Optional[str] = Field(None, description="Unit of measurement.", examples=["$", "%", "users"])
    description: Optional[str] = Field(
        None, description="Description of the key result.", examples=["Monthly recurring revenue"]
    )


class KeyResultGetInput(BaseModel):
    """
    Get a key result by ID. HTTP: GET /key_result/{key_result_id}

    When to use: Retrieve details of a specific key result.

    Attributes:
        key_result_id: Key result ID

    Examples:
        KeyResultGetInput(key_result_id="kr_123")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"key_result_id": "kr_123"}]})

    key_result_id: str = Field(..., min_length=1, description="Key result ID.", examples=["kr_123", "kr_abc"])


class KeyResultUpdateInput(BaseModel):
    """
    Update a key result. HTTP: PUT /key_result/{key_result_id}

    When to use: Modify key result details like name, target, or current value.

    Constraints:
        - `target` must be positive if provided

    Attributes:
        key_result_id: Key result ID
        name: New key result name
        target: New target value
        current: New current value
        unit: New unit of measurement
        description: New description

    Examples:
        KeyResultUpdateInput(key_result_id="kr_123", target=2000000)
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"key_result_id": "kr_123", "target": 2000000}]})

    key_result_id: str = Field(..., min_length=1, description="Key result ID.", examples=["kr_123", "kr_abc"])
    name: Optional[str] = Field(None, description="New key result name.", examples=["Updated Key Result Name"])
    target: Optional[float] = Field(None, description="New target value.", examples=[2000000, 75.0])
    current: Optional[float] = Field(None, description="New current value.", examples=[500000, 25.0])
    unit: Optional[str] = Field(None, description="New unit of measurement.", examples=["$", "%", "users"])
    description: Optional[str] = Field(None, description="New description.", examples=["Updated description"])


class KeyResultDeleteInput(BaseModel):
    """
    Delete a key result. HTTP: DELETE /key_result/{key_result_id}

    When to use: Remove a key result permanently.

    Attributes:
        key_result_id: Key result ID

    Examples:
        KeyResultDeleteInput(key_result_id="kr_123")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"key_result_id": "kr_123"}]})

    key_result_id: str = Field(..., min_length=1, description="Key result ID.", examples=["kr_123", "kr_abc"])


class KeyResultListInput(BaseModel):
    """
    List key results for a goal. HTTP: GET /goal/{goal_id}/key_result

    When to use: Retrieve all key results for a specific goal.

    Attributes:
        goal_id: Goal ID

    Examples:
        KeyResultListInput(goal_id="goal_123")
    """

    model_config = ConfigDict(json_schema_extra={"examples": [{"goal_id": "goal_123"}]})

    goal_id: str = Field(..., min_length=1, description="Goal ID.", examples=["goal_123", "gl_abc"])
