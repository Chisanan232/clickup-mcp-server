"""Unit tests for ListMapper DTO ↔ Domain conversions."""

from clickup_mcp.models.domain.list import ClickUpList
from clickup_mcp.models.dto.list import ListResp
# NOTE: Why single-file runs used to fail here
# - mcp_server/__init__.py eagerly imported tool modules, and mappers imported MCP models
#   at module import time → circular import when importing this test alone.
# Fix: mappers now defer MCP imports using TYPE_CHECKING + local imports inside functions.
from clickup_mcp.models.mapping.list_mapper import ListMapper
from clickup_mcp.mcp_server.models.inputs.list_ import ListCreateInput, ListUpdateInput


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


def test_domain_to_output_result_and_list_item() -> None:
    dom = ClickUpList(
        id="l1",
        name="List",
        content="desc",
        status="open",
        priority=3,
        assignee_id=77,
        due_date=1000,
        due_date_time=False,
        folder_id="f1",
        space_id="s1",
    )

    res = ListMapper.to_list_result_output(dom)
    assert res.id == "l1"
    assert res.name == "List"
    assert res.status == "open"
    assert res.folder_id == "f1"
    assert res.space_id == "s1"

    item = ListMapper.to_list_list_item_output(dom)
    assert item.id == "l1"
    assert item.name == "List"


def test_from_create_input_builds_domain_and_copies_fields() -> None:
    inp = ListCreateInput(
        folder_id="f1",
        name="List A",
        content="desc",
        status="open",
        priority=2,
        assignee=77,
        due_date=100,
        due_date_time=True,
    )
    dom = ListMapper.from_create_input(inp)
    assert dom.name == "List A"
    assert dom.content == "desc"
    assert dom.folder_id == "f1"
    assert dom.status == "open"
    assert dom.priority == 2
    assert dom.assignee_id == 77
    assert dom.due_date == 100
    assert dom.due_date_time is True


def test_from_update_input_builds_domain_and_defaults_name() -> None:
    inp = ListUpdateInput(
        list_id="l1",
        name=None,
        content="desc2",
        status="open",
        priority=3,
        assignee=88,
        due_date=200,
        due_date_time=False,
    )
    dom = ListMapper.from_update_input(inp)
    assert dom.id == "l1"
    assert dom.name == ""
    assert dom.content == "desc2"
    assert dom.priority == 3
