"""Mapper tests for Goal."""

from clickup_mcp.models.domain.goal import Goal
from clickup_mcp.models.dto.goal import GoalCreate, GoalResponse, GoalUpdate
from clickup_mcp.models.mapping.goal_mapper import GoalMapper


def test_goal_mapper_to_domain() -> None:
    response = GoalResponse(
        id="goal_123",
        team_id="team_1",
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
        status="active",
        key_results=["KR1"],
        owners=["user_1"],
    )
    domain = GoalMapper.to_domain(response)
    assert domain.goal_id == "goal_123"
    assert domain.team_id == "team_1"
    assert domain.name == "Q1 Revenue Goal"


def test_goal_mapper_to_create_dto() -> None:
    domain = Goal(
        id="temp",
        team_id="team_1",
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
        key_results=["KR1"],
    )
    dto = GoalMapper.to_create_dto(domain)
    assert dto.name == "Q1 Revenue Goal"
    assert dto.description == "Achieve $1M in revenue"
    assert dto.due_date == 1702080000000
    assert dto.key_results == ["KR1"]


def test_goal_mapper_to_update_dto() -> None:
    domain = Goal(
        id="goal_123",
        team_id="temp",
        name="Updated Goal Name",
        status="completed",
    )
    dto = GoalMapper.to_update_dto(domain)
    assert dto.name == "Updated Goal Name"
    assert dto.status == "completed"


def test_goal_mapper_to_goal_result_output() -> None:
    domain = Goal(
        id="goal_123",
        team_id="team_1",
        name="Q1 Revenue Goal",
        description="Achieve $1M in revenue",
        due_date=1702080000000,
        status="active",
    )
    output = GoalMapper.to_goal_result_output(domain)
    assert output["id"] == "goal_123"
    assert output["team_id"] == "team_1"
    assert output["name"] == "Q1 Revenue Goal"


def test_goal_mapper_to_goal_list_item_output() -> None:
    domain = Goal(
        id="goal_123",
        team_id="team_1",
        name="Q1 Revenue Goal",
        due_date=1702080000000,
        status="active",
    )
    output = GoalMapper.to_goal_list_item_output(domain)
    assert output["id"] == "goal_123"
    assert output["team_id"] == "team_1"
    assert output["name"] == "Q1 Revenue Goal"
    assert output["status"] == "active"
