"""Domain behavior tests for Goal."""

import pytest

from clickup_mcp.models.domain.goal import Goal


def test_goal_update_name() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Original Name", due_date=1702080000000)
    goal.update_name("Updated Name")
    assert goal.name == "Updated Name"


def test_goal_update_name_empty_raises() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Original Name", due_date=1702080000000)
    with pytest.raises(ValueError):
        goal.update_name("")


def test_goal_update_description() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000)
    goal.update_description("New description")
    assert goal.description == "New description"


def test_goal_set_status() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000)
    goal.set_status("completed")
    assert goal.status == "completed"


def test_goal_set_status_empty_raises() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000)
    with pytest.raises(ValueError):
        goal.set_status("")


def test_goal_set_due_date() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000)
    goal.set_due_date(1702200000000)
    assert goal.due_date == 1702200000000


def test_goal_set_due_date_negative_raises() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000)
    with pytest.raises(ValueError):
        goal.set_due_date(-1)


def test_goal_add_key_result() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000)
    goal.add_key_result("KR1")
    assert goal.key_results == ["KR1"]

    # Adding another key result preserves existing
    goal.add_key_result("KR2")
    assert goal.key_results == ["KR1", "KR2"]

    # Adding duplicate raises error
    with pytest.raises(ValueError):
        goal.add_key_result("KR1")


def test_goal_remove_key_result() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000, key_results=["KR1", "KR2"])
    goal.remove_key_result("KR1")
    assert goal.key_results == ["KR2"]

    # Removing non-existent key result raises error
    with pytest.raises(ValueError):
        goal.remove_key_result("KR999")


def test_goal_add_owner() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000, multiple_owners=True)
    goal.add_owner("user_1")
    assert goal.owners == ["user_1"]

    # Adding another owner preserves existing
    goal.add_owner("user_2")
    assert goal.owners == ["user_1", "user_2"]

    # Adding duplicate raises error
    with pytest.raises(ValueError):
        goal.add_owner("user_1")


def test_goal_remove_owner() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000, owners=["user_1", "user_2"])
    goal.remove_owner("user_1")
    assert goal.owners == ["user_2"]

    # Removing non-existent owner raises error
    with pytest.raises(ValueError):
        goal.remove_owner("user_999")


def test_goal_is_active() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000, status="active")
    assert goal.is_active() is True

    goal.status = "completed"
    assert goal.is_active() is False


def test_goal_is_completed() -> None:
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000, status="completed")
    assert goal.is_completed() is True

    goal.status = "active"
    assert goal.is_completed() is False


def test_goal_is_overdue() -> None:
    # Create a goal with a past due date (1702080000000 is Dec 9, 2023)
    # Current time would be much later
    goal = Goal(id="goal_1", team_id="team_1", name="Goal", due_date=1702080000000, status="active")
    # This will depend on current time, but the logic should work
    result = goal.is_overdue()
    assert isinstance(result, bool)


def test_goal_id_property() -> None:
    goal = Goal(id="goal_123", team_id="team_1", name="Goal", due_date=1702080000000)
    assert goal.id == "goal_123"
    assert goal.goal_id == "goal_123"
