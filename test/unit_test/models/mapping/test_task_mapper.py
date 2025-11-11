"""Unit tests for TaskMapper DTO ↔ Domain conversions."""

from clickup_mcp.models.mapping.task_mapper import TaskMapper
from clickup_mcp.models.domain.task import ClickUpTask
from clickup_mcp.models.dto.task import TaskResp


def test_to_domain_from_resp_minimal() -> None:
    resp = TaskResp(
        id="t1",
        name="Task One",
        status=TaskResp.TaskStatusInfo(status="open"),
        priority=TaskResp.TaskPriorityInfo(id="3"),
        assignees=[TaskResp.UserRef(id=1), TaskResp.UserRef(id="2")],
        folder=TaskResp.EntityRef(id="f1"),
        list=TaskResp.EntityRef(id="l1"),
        space=TaskResp.EntityRef(id="s1"),
        due_date=123,
        time_estimate=456,
        custom_fields=[TaskResp.CustomFieldValueResp(id="cf1", value="v1")],
    )

    dom = TaskMapper.to_domain(resp)

    assert dom.id == "t1"
    assert dom.name == "Task One"
    assert dom.status == "open"
    assert dom.priority == 3
    assert dom.list_id == "l1"
    assert dom.folder_id == "f1"
    assert dom.space_id == "s1"
    assert dom.assignee_ids == [1, "2"]
    assert dom.due_date == 123
    assert dom.time_estimate == 456
    assert dom.custom_fields == [{"id": "cf1", "value": "v1"}]


def test_to_create_and_update_dto_from_domain() -> None:
    dom = ClickUpTask(
        id="t1",
        name="Task",
        status="in progress",
        priority=2,
        list_id="l1",
        assignee_ids=[1, 2],
        due_date=1000,
        time_estimate=2000,
        parent_id=None,
        custom_fields=[{"id": "cf1", "value": "x"}],
    )

    create_dto = TaskMapper.to_create_dto(dom)
    payload = create_dto.to_payload()

    assert payload["name"] == "Task"
    assert payload["status"] == "in progress"
    assert payload["priority"] == 2
    assert payload["assignees"] == [1, 2]
    assert payload["due_date"] == 1000
    assert payload["time_estimate"] == 2000
    assert payload["custom_fields"] == [{"id": "cf1", "value": "x"}]

    update_dto = TaskMapper.to_update_dto(dom)
    up = update_dto.to_payload()
    assert up["name"] == "Task"
    assert up["status"] == "in progress"
    assert up["priority"] == 2
    assert up["assignees"] == [1, 2]
    assert up["due_date"] == 1000
    assert up["time_estimate"] == 2000
