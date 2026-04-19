"""DTO tests for KeyResult."""

from clickup_mcp.models.dto.key_result import KeyResultCreate, KeyResultListResponse, KeyResultResponse, KeyResultUpdate


def test_key_result_create_serialization() -> None:
    dto = KeyResultCreate(
        name="Increase MRR",
        type="currency",
        target=1000000,
        unit="$",
        description="Monthly recurring revenue",
    )
    serialized = dto.serialize()
    assert serialized["name"] == "Increase MRR"
    assert serialized["type"] == "currency"
    assert serialized["target"] == 1000000
    assert serialized["unit"] == "$"
    assert serialized["description"] == "Monthly recurring revenue"


def test_key_result_update_serialization() -> None:
    dto = KeyResultUpdate(
        target=2000000,
        current=750000,
    )
    serialized = dto.serialize()
    assert serialized["target"] == 2000000
    assert serialized["current"] == 750000


def test_key_result_response_deserialization() -> None:
    data = {
        "id": "kr_123",
        "goal_id": "goal_1",
        "name": "Increase MRR",
        "type": "currency",
        "target": 1000000,
        "current": 500000,
        "unit": "$",
        "description": "Monthly recurring revenue",
    }
    response = KeyResultResponse.deserialize(data)
    assert response.id == "kr_123"
    assert response.goal_id == "goal_1"
    assert response.name == "Increase MRR"
    assert response.target == 1000000
    assert response.current == 500000


def test_key_result_list_response_deserialization() -> None:
    data = {
        "items": [
            {
                "id": "kr_123",
                "goal_id": "goal_1",
                "name": "Increase MRR",
                "type": "currency",
                "target": 1000000,
                "current": 500000,
            }
        ]
    }
    response = KeyResultListResponse.deserialize(data)
    assert len(response.items) == 1
    assert response.items[0].id == "kr_123"
