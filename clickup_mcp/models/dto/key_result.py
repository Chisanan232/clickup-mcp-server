"""
Key Result DTOs for ClickUp API requests and responses.

These DTOs provide serialization and deserialization helpers for ClickUp Key Result
operations, including create, update, list, and response operations. All request DTOs inherit
from `BaseRequestDTO` and exclude None values from payloads; response DTOs
inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create key result payload
    from clickup_mcp.models.dto.key_result import KeyResultCreate

    payload = KeyResultCreate(
        name="Increase MRR",
        type="currency",
        target=1000000,
        unit="$"
    ).to_payload()
    # => {"name": "Increase MRR", "type": "currency", "target": 1000000, "unit": "$"}
"""

from typing import List

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "Key result name"
PROPERTY_TYPE_DESCRIPTION: str = "Key result type (e.g., 'number', 'currency', 'boolean')"
PROPERTY_TARGET_DESCRIPTION: str = "Target value for the key result"
PROPERTY_CURRENT_DESCRIPTION: str = "Current value for the key result"
PROPERTY_UNIT_DESCRIPTION: str = "Unit of measurement"


class KeyResultCreate(BaseRequestDTO):
    """
    DTO for creating a new key result.

    API:
        POST /goal/{goal_id}/key_result
        Docs: https://developer.clickup.com/reference/createkeyresult

    Notes:
        Requires name, type, and target to define the key result.

    Attributes:
        name: Key result name
        type: Key result type
        target: Target value
        unit: Unit of measurement
        description: Description of the key result

    Examples:
        # Python - payload build
        KeyResultCreate(
            name="Increase MRR",
            type="currency",
            target=1000000,
            unit="$"
        ).to_payload()
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    type: str = Field(description=PROPERTY_TYPE_DESCRIPTION)
    target: float = Field(description=PROPERTY_TARGET_DESCRIPTION)
    unit: str | None = Field(default=None, description=PROPERTY_UNIT_DESCRIPTION)
    description: str | None = Field(default=None, description="Description of the key result")


class KeyResultUpdate(BaseRequestDTO):
    """
    DTO for updating an existing key result.

    API:
        PUT /key_result/{key_result_id}
        Docs: https://developer.clickup.com/reference/updatekeyresult

    Notes:
        Only include fields that need to be updated.

    Attributes:
        name: New key result name
        target: New target value
        current: New current value
        unit: New unit of measurement
        description: New description

    Examples:
        # Python - update target
        KeyResultUpdate(target=2000000).to_payload()
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    target: float | None = Field(default=None, description=PROPERTY_TARGET_DESCRIPTION)
    current: float | None = Field(default=None, description=PROPERTY_CURRENT_DESCRIPTION)
    unit: str | None = Field(default=None, description=PROPERTY_UNIT_DESCRIPTION)
    description: str | None = Field(default=None, description="Description of the key result")


class KeyResultResponse(BaseResponseDTO):
    """
    DTO for key result API responses.

    Attributes:
        id: Key result ID
        goal_id: Goal ID this key result belongs to
        name: Key result name
        type: Key result type
        target: Target value
        current: Current value
        unit: Unit of measurement
        description: Description of the key result
        date_created: Creation date in epoch milliseconds
        date_updated: Last update date in epoch milliseconds

    Examples:
        # Python - deserialize API response
        KeyResultResponse.deserialize({
            "id": "kr_123",
            "goal_id": "goal_001",
            "name": "Increase MRR",
            "target": 1000000,
            "current": 500000,
        })
    """

    id: str = Field(description="Key result ID")
    goal_id: str = Field(description="Goal ID this key result belongs to")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    type: str = Field(default="number", description=PROPERTY_TYPE_DESCRIPTION)
    target: float = Field(description=PROPERTY_TARGET_DESCRIPTION)
    current: float = Field(default=0.0, description=PROPERTY_CURRENT_DESCRIPTION)
    unit: str | None = Field(default=None, description=PROPERTY_UNIT_DESCRIPTION)
    description: str | None = Field(default=None, description="Description of the key result")
    date_created: int | None = Field(default=None, description="Creation date in epoch milliseconds")
    date_updated: int | None = Field(default=None, description="Last update date in epoch milliseconds")


class KeyResultListResponse(BaseResponseDTO):
    """
    DTO for key result list responses.

    Attributes:
        items: List of key results

    Examples:
        # Python - deserialize list response
        KeyResultListResponse.deserialize({
            "items": [{"id": "kr_123", "name": "Increase MRR", ...}]
        })
    """

    items: List[KeyResultResponse] = Field(description="List of key results")
