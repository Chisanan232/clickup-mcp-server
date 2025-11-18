"""Unit tests for TaskMapper DTO ↔ Domain conversions."""

import pytest
from pydantic import ValidationError

from clickup_mcp.mcp_server.models.inputs.task import TaskCreateInput, TaskUpdateInput
from clickup_mcp.models.domain.task import ClickUpTask
from clickup_mcp.models.dto.task import TaskResp

# NOTE: Root cause for earlier single-file import failures
# - mcp_server/__init__.py eagerly imported tool modules (task.py, etc.).
# - mapper modules imported MCP input/output models at module import time.
# - Importing this mapper in isolation created a circular import.
# Fix applied
# - Defer MCP imports in mappers via TYPE_CHECKING and import outputs inside functions.
#   See: clickup_mcp/models/mapping/task_mapper.py (and other mappers) for details.
from clickup_mcp.models.mapping.task_mapper import TaskMapper


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


def test_to_domain_parses_priority_id_suffix() -> None:
    resp = TaskResp(
        id="t2",
        name="Task Two",
        status=TaskResp.TaskStatusInfo(status="open"),
        priority=TaskResp.TaskPriorityInfo(id="priority_1"),
        assignees=[],
        list=TaskResp.EntityRef(id="l1"),
    )
    dom = TaskMapper.to_domain(resp)
    assert dom.priority == 1


def test_to_domain_fallbacks_to_priority_label() -> None:
    # Provide label only to exercise fallback mapping
    prio_obj = TaskResp.TaskPriorityInfo(id=None, priority="High")
    resp = TaskResp(
        id="t3",
        name="Task Three",
        status=TaskResp.TaskStatusInfo(status="open"),
        priority=prio_obj,
        assignees=[],
        list=TaskResp.EntityRef(id="l1"),
    )
    dom = TaskMapper.to_domain(resp)
    assert dom.priority == 2


def test_from_create_input_builds_domain_and_normalizes_priority() -> None:
    inp = TaskCreateInput(
        list_id="L1",
        name="Ship",
        status="in progress",
        description="This is a ship task description",
        priority="HIGH",
        assignees=[1, "2"],
        due_date=111,
        time_estimate=222,
        parent=None,
    )

    dom = TaskMapper.from_create_input(inp)
    assert dom.name == "Ship"
    assert dom.status == "in progress"
    # assert dom.description == "This is a ship task description"
    assert dom.priority == 2  # HIGH -> 2
    assert dom.assignee_ids == [1, "2"]
    assert dom.due_date == 111
    assert dom.time_estimate == 222


def test_from_update_input_builds_domain_with_defaults_and_normalization() -> None:
    inp = TaskUpdateInput(
        task_id="t1",
        name=None,  # should default to ""
        status=None,
        description=None,
        priority="LOW",  # -> 4
        assignees=None,  # should become []
        due_date=None,
        time_estimate=None,
    )

    dom = TaskMapper.from_update_input(inp)
    assert dom.id == "t1"
    assert dom.name == ""
    assert dom.status is None
    # assert dom.description is None
    assert dom.priority == 4
    assert dom.assignee_ids == []


def test_from_create_input_invalid_priority_int_raises() -> None:
    inp = TaskCreateInput(list_id="L1", name="Ship", priority=5)
    with pytest.raises(ValueError):
        TaskMapper.from_create_input(inp)


def test_from_create_input_invalid_priority_label_raises() -> None:
    with pytest.raises(ValidationError):
        TaskCreateInput(list_id="L1", name="Ship", priority="INVALID")


def test_from_update_input_invalid_priority_label_raises() -> None:
    with pytest.raises(ValidationError):
        TaskUpdateInput(task_id="t1", priority="WRONG")


def test_from_update_input_assignees_empty_list_kept() -> None:
    inp = TaskUpdateInput(task_id="t1", assignees=[])
    dom = TaskMapper.from_update_input(inp)
    assert dom.assignee_ids == []
