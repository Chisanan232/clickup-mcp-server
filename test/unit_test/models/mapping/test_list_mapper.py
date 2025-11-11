"""Unit tests for ListMapper DTO ↔ Domain conversions."""

from clickup_mcp.models.mapping.list_mapper import ListMapper
from clickup_mcp.models.domain.list import ClickUpList
from clickup_mcp.models.dto.list import ListResp


def test_to_domain_from_resp_minimal() -> None:
    resp = ListResp(
        id="l1",
        name="List One",
        status="open",
        priority=2,
        assignee=ListResp.UserRef(id=42),
        folder=ListResp.FolderRef(id="f1"),
        space=ListResp.SpaceRef(id="s1"),
        due_date=123,
        due_date_time=True,
        content="desc",
    )

    dom = ListMapper.to_domain(resp)

    assert dom.id == "l1"
    assert dom.name == "List One"
    assert dom.status == "open"
    assert dom.priority == 2
    assert dom.assignee_id == 42
    assert dom.folder_id == "f1"
    assert dom.space_id == "s1"
    assert dom.due_date == 123
    assert dom.due_date_time is True
    assert dom.content == "desc"


def test_to_create_and_update_dto_from_domain() -> None:
    dom = ClickUpList(
        id="l1",
        name="List",
        content="desc",
        status="open",
        priority=3,
        assignee_id=77,
        due_date=1000,
        due_date_time=False,
    )

    create_dto = ListMapper.to_create_dto(dom)
    payload = create_dto.to_payload()

    assert payload["name"] == "List"
    assert payload["content"] == "desc"
    assert payload["status"] == "open"
    assert payload["priority"] == 3
    assert payload["assignee"] == 77
    assert payload["due_date"] == 1000
    assert payload["due_date_time"] is False

    update_dto = ListMapper.to_update_dto(dom)
    up = update_dto.to_payload()
    assert up["name"] == "List"
    assert up["content"] == "desc"
    assert up["status"] == "open"
    assert up["priority"] == 3
    assert up["assignee"] == 77
    assert up["due_date"] == 1000
    assert up["due_date_time"] is False
