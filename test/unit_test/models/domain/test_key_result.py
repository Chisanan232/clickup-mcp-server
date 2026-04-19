"""Domain behavior tests for KeyResult."""

import pytest

from clickup_mcp.models.domain.key_result import KeyResult


def test_key_result_update_name() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="Original Name", target=1000000)
    kr.update_name("Updated Name")
    assert kr.name == "Updated Name"


def test_key_result_update_name_empty_raises() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="Original Name", target=1000000)
    with pytest.raises(ValueError):
        kr.update_name("")


def test_key_result_set_target() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000)
    kr.set_target(2000000)
    assert kr.target == 2000000


def test_key_result_set_target_negative_raises() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000)
    with pytest.raises(ValueError):
        kr.set_target(-1)


def test_key_result_update_current() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000)
    kr.update_current(500000)
    assert kr.current == 500000


def test_key_result_update_current_negative_raises() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000)
    with pytest.raises(ValueError):
        kr.update_current(-1)


def test_key_result_update_description() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000)
    kr.update_description("New description")
    assert kr.description == "New description"


def test_key_result_set_unit() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000)
    kr.set_unit("$")
    assert kr.unit == "$"


def test_key_result_get_progress_percentage() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000, current=500000)
    progress = kr.get_progress_percentage()
    assert progress == 50.0


def test_key_result_get_progress_percentage_zero_target() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=0, current=500000)
    progress = kr.get_progress_percentage()
    assert progress == 0.0


def test_key_result_get_progress_percentage_over_target() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000, current=1500000)
    progress = kr.get_progress_percentage()
    assert progress == 100.0


def test_key_result_is_completed() -> None:
    kr = KeyResult(id="kr_1", goal_id="goal_1", name="KR", target=1000000, current=1000000)
    assert kr.is_completed() is True

    kr.current = 500000
    assert kr.is_completed() is False


def test_key_result_id_property() -> None:
    kr = KeyResult(id="kr_123", goal_id="goal_1", name="KR", target=1000000)
    assert kr.id == "kr_123"
    assert kr.key_result_id == "kr_123"
