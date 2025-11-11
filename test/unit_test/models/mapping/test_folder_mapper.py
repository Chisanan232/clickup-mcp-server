"""Unit tests for FolderMapper DTO ↔ Domain conversions."""

from clickup_mcp.models.mapping.folder_mapper import FolderMapper
from clickup_mcp.models.domain.folder import ClickUpFolder
from clickup_mcp.models.dto.folder import FolderResp


def test_to_domain_from_resp_minimal() -> None:
    resp = FolderResp(
        id="f1",
        name="Folder One",
        override_statuses=True,
        hidden=False,
        space=FolderResp.SpaceRef(id="s1"),
    )

    dom = FolderMapper.to_domain(resp)

    assert dom.id == "f1"
    assert dom.name == "Folder One"
    assert dom.space_id == "s1"
    assert dom.override_statuses is True
    assert dom.hidden is False


def test_to_create_and_update_dto_from_domain() -> None:
    dom = ClickUpFolder(id="f1", name="Folder X", space_id="s1", override_statuses=False, hidden=False)

    create_dto = FolderMapper.to_create_dto(dom)
    payload = create_dto.to_payload()

    assert payload["name"] == "Folder X"

    update_dto = FolderMapper.to_update_dto(dom)
    up = update_dto.to_payload()
    assert up["name"] == "Folder X"
