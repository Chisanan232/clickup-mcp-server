"""Domain behavior tests for ClickUpFolder."""

import pytest

from clickup_mcp.models.domain.folder import ClickUpFolder


def test_folder_rename_and_move() -> None:
    folder = ClickUpFolder(id="f1", name="Folder")

    folder.rename("Renamed")
    assert folder.name == "Renamed"

    folder.move_to_space("s1")
    assert folder.space_id == "s1"


def test_folder_rename_invalid_raises() -> None:
    folder = ClickUpFolder(id="f1", name="Folder")
    with pytest.raises(ValueError):
        folder.rename("")


def test_folder_move_requires_space() -> None:
    folder = ClickUpFolder(id="f1", name="Folder")
    with pytest.raises(ValueError):
        folder.move_to_space("")
