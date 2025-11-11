"""Domain behavior tests for ClickUpList."""

import pytest

from clickup_mcp.models.domain.list import ClickUpList


def test_list_rename_and_schedule_and_assign() -> None:
    lst = ClickUpList(id="l1", name="My List")

    lst.rename("New Name")
    assert lst.name == "New Name"

    lst.assign_to(42)
    assert lst.assignee_id == 42

    lst.schedule(123456789, include_time=True)
    assert lst.due_date == 123456789
    assert lst.due_date_time is True


def test_list_rename_invalid_raises() -> None:
    lst = ClickUpList(id="l1", name="My List")
    with pytest.raises(ValueError):
        lst.rename("")


def test_list_attach_to_folder_space() -> None:
    lst = ClickUpList(id="l1", name="My List")

    lst.attach_to_folder("f1")
    assert lst.folder_id == "f1"

    lst.attach_to_space("s1")
    assert lst.space_id == "s1"

    with pytest.raises(ValueError):
        lst.attach_to_folder("")

    with pytest.raises(ValueError):
        lst.attach_to_space("")
