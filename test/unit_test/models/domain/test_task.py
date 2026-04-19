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


def test_task_add_assignee() -> None:
    task = ClickUpTask(id="t1", name="Task")
    task.add_assignee("user_1")
    assert task.assignee_ids == ["user_1"]

    # Adding another assignee preserves existing
    task.add_assignee("user_2")
    assert task.assignee_ids == ["user_1", "user_2"]

    # Adding duplicate has no effect
    task.add_assignee("user_1")
    assert task.assignee_ids == ["user_1", "user_2"]


def test_task_remove_assignee() -> None:
    task = ClickUpTask(id="t1", name="Task", assignee_ids=["user_1", "user_2"])
    task.remove_assignee("user_1")
    assert task.assignee_ids == ["user_2"]

    # Removing non-existent user has no effect
    task.remove_assignee("user_999")
    assert task.assignee_ids == ["user_2"]


def test_task_matches_search_text() -> None:
    task = ClickUpTask(id="t1", name="Fix urgent bug", status="open")
    assert task.matches_search(query="urgent") is True
    assert task.matches_search(query="bug") is True
    assert task.matches_search(query="fix") is True
    assert task.matches_search(query="feature") is False


def test_task_matches_search_status() -> None:
    task = ClickUpTask(id="t1", name="Task", status="open")
    assert task.matches_search(status="open") is True
    assert task.matches_search(status="closed") is False


def test_task_matches_search_priority() -> None:
    task = ClickUpTask(id="t1", name="Task", priority=1)
    assert task.matches_search(priority=1) is True
    assert task.matches_search(priority=2) is False


def test_task_matches_search_assignee() -> None:
    task = ClickUpTask(id="t1", name="Task", assignee_ids=["user_1", "user_2"])
    assert task.matches_search(assignee_id="user_1") is True
    assert task.matches_search(assignee_id="user_999") is False


def test_task_matches_search_combined() -> None:
    task = ClickUpTask(id="t1", name="Fix urgent bug", status="open", priority=1, assignee_ids=["user_1"])
    assert task.matches_search(query="bug", status="open", priority=1, assignee_id="user_1") is True
    assert task.matches_search(query="bug", status="closed") is False


def test_task_matches_search_due_date() -> None:
    task = ClickUpTask(id="t1", name="Task", due_date=1702128000000)
    # 2023-12-09 00:00:00 UTC
    assert task.matches_search(due_date_from=1702080000000, due_date_to=1702174400000) is True
    # Outside range
    assert task.matches_search(due_date_from=1702200000000, due_date_to=1702300000000) is False
