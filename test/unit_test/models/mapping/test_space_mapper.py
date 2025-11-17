"""Unit tests for SpaceMapper DTO ↔ Domain conversions."""

from clickup_mcp.models.domain.space import ClickUpSpace
from clickup_mcp.models.dto.space import DueDatesFeature, SpaceFeatures, SpaceResp
from clickup_mcp.models.mapping.space_mapper import SpaceMapper


def test_to_domain_from_resp_minimal() -> None:
    resp = SpaceResp(
        id="s1",
        name="Space One",
        private=False,
        statuses=[],
        multiple_assignees=True,
        features=SpaceFeatures(due_dates=DueDatesFeature(enabled=True)),
        team_id="t1",
    )

    dom = SpaceMapper.to_domain(resp)

    assert dom.id == "s1"
    assert dom.name == "Space One"
    assert dom.private is False
    assert dom.multiple_assignees is True
    assert isinstance(dom.features, dict)
    assert "due_dates" in dom.features
    assert dom.team_id == "t1"


def test_to_create_and_update_dto_from_domain() -> None:
    dom = ClickUpSpace(
        id="s1",
        name="My Space",
        private=False,
        statuses=[],
        multiple_assignees=True,
        features=None,
        team_id="t1",
    )

    create_dto = SpaceMapper.to_create_dto(dom)
    payload = create_dto.to_payload()
    assert payload["name"] == "My Space"
    assert payload["multiple_assignees"] is True

    update_dto = SpaceMapper.to_update_dto(dom)
    up = update_dto.to_payload()
    assert up["name"] == "My Space"
    assert up["private"] is False
    assert up["multiple_assignees"] is True


def test_domain_to_output_result_and_list_item() -> None:
    dom = ClickUpSpace(
        id="s1",
        name="My Space",
        private=False,
        statuses=[],
        multiple_assignees=True,
        features=None,
        team_id="t1",
    )

    res = SpaceMapper.to_space_result_output(dom)
    assert res.id == "s1"
    assert res.name == "My Space"
    assert res.private is False
    assert res.team_id == "t1"

    item = SpaceMapper.to_space_list_item_output(dom)
    assert item.id == "s1"
    assert item.name == "My Space"
