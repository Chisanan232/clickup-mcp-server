"""Mapper tests for KeyResult."""

from clickup_mcp.models.domain.key_result import KeyResult
from clickup_mcp.models.dto.key_result import KeyResultCreate, KeyResultResponse, KeyResultUpdate
from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper


def test_key_result_mapper_to_domain() -> None:
    response = KeyResultResponse(
        id="kr_123",
        goal_id="goal_1",
        name="Increase MRR",
        type="currency",
        target=1000000,
        current=500000,
        unit="$",
        description="Monthly recurring revenue",
    )
    domain = KeyResultMapper.to_domain(response)
    assert domain.key_result_id == "kr_123"
    assert domain.goal_id == "goal_1"
    assert domain.name == "Increase MRR"


def test_key_result_mapper_to_create_dto() -> None:
    domain = KeyResult(
        id="temp",
        goal_id="goal_1",
        name="Increase MRR",
        type="currency",
        target=1000000,
        unit="$",
    )
    dto = KeyResultMapper.to_create_dto(domain)
    assert dto.name == "Increase MRR"
    assert dto.type == "currency"
    assert dto.target == 1000000
    assert dto.unit == "$"


def test_key_result_mapper_to_update_dto() -> None:
    domain = KeyResult(
        id="kr_123",
        goal_id="temp",
        name="Updated KR Name",
        target=2000000,
        current=750000,
    )
    dto = KeyResultMapper.to_update_dto(domain)
    assert dto.name == "Updated KR Name"
    assert dto.target == 2000000
    assert dto.current == 750000


def test_key_result_mapper_to_key_result_result_output() -> None:
    domain = KeyResult(
        id="kr_123",
        goal_id="goal_1",
        name="Increase MRR",
        type="currency",
        target=1000000,
        current=500000,
        unit="$",
    )
    output = KeyResultMapper.to_key_result_result_output(domain)
    assert output["id"] == "kr_123"
    assert output["goal_id"] == "goal_1"
    assert output["name"] == "Increase MRR"
    assert output["target"] == 1000000
    assert output["current"] == 500000
