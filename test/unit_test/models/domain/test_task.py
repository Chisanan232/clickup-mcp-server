"""Domain behavior tests for ClickUpTask."""

import pytest

from clickup_mcp.models.domain.task import ClickUpTask


def test_task_change_status_and_priority_and_assignment() -> None:
    task = ClickUpTask(id="t1", name="Task")

    task.change_status("in progress")
    assert task.status == "in progress"

    task.set_priority(3)
    assert task.priority == 3

    task.assign(1, 2, "u3")
    assert task.assignee_ids == [1, 2, "u3"]


def test_task_invalid_status_raises() -> None:
    task = ClickUpTask(id="t1", name="Task")
    with pytest.raises(ValueError):
        task.change_status("")


def test_task_estimate_and_schedule_validation() -> None:
    task = ClickUpTask(id="t1", name="Task")

    task.set_estimate(5000)
    assert task.time_estimate == 5000

    with pytest.raises(ValueError):
        task.set_estimate(-1)

    task.schedule(123456789)
    assert task.due_date == 123456789

    with pytest.raises(ValueError):
        task.schedule(-5)


def test_task_attach_to_list() -> None:
    task = ClickUpTask(id="t1", name="Task")
    task.attach_to_list("list-1")
    assert task.list_id == "list-1"

    with pytest.raises(ValueError):
        task.attach_to_list("")
