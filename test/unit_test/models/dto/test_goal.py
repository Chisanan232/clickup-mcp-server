"""DTO tests for Goal."""

from clickup_mcp.models.dto.goal import GoalCreate, GoalListQuery, GoalResponse, GoalUpdate


def test_goal_create_serialization() -> None:
    dto = GoalCreate(
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
        key_results=["KR1", "KR2"],
        owners=["user_1"],
    )
    serialized = dto.serialize()
    assert serialized["name"] == "Q1 Revenue Goal"
    assert serialized["description"] == "Achieve $1M in revenue"
    assert serialized["due_date"] == 1702080000000
    assert serialized["key_results"] == ["KR1", "KR2"]
    assert serialized["owners"] == ["user_1"]


def test_goal_update_serialization() -> None:
    dto = GoalUpdate(
        name="Updated Goal Name",
        target=2000000,
        status="completed",
    )
    serialized = dto.serialize()
    assert serialized["name"] == "Updated Goal Name"
    assert serialized["target"] == 2000000
    assert serialized["status"] == "completed"


def test_goal_list_query_to_query() -> None:
    query = GoalListQuery(status="active", limit=50, page=0)
    query_dict = query.to_query()
    assert query_dict["status"] == "active"
    assert query_dict["limit"] == 50
    assert query_dict["page"] == 0


def test_goal_list_query_limit_capped() -> None:
    query = GoalListQuery(limit=150)
    query_dict = query.to_query()
    assert query_dict["limit"] == 100


def test_goal_response_deserialization() -> None:
    data = {
        "id": "goal_123",
        "team_id": "team_1",
        "name": "Q1 Revenue Goal",
        "description": "Achieve $1M in revenue",
        "due_date": 1702080000000,
        "status": "active",
        "key_results": ["KR1"],
        "owners": ["user_1"],
        "multiple_owners": False,
    }
    response = GoalResponse.deserialize(data)
    assert response.id == "goal_123"
    assert response.team_id == "team_1"
    assert response.name == "Q1 Revenue Goal"
