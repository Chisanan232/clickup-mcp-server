"""Folder DTO ↔ Domain mappers.

Translate between Folder transport DTOs and the ClickUpFolder domain entity.
"""

from __future__ import annotations

from clickup_mcp.models.domain.folder import ClickUpFolder
from clickup_mcp.models.dto.folder import FolderCreate, FolderResp, FolderUpdate
from clickup_mcp.mcp_server.models.outputs.folder import FolderListItem, FolderResult


class FolderMapper:
    """Static helpers to convert between Folder DTOs and domain entity."""

    @staticmethod
    def to_domain(resp: FolderResp) -> ClickUpFolder:
        space_id = resp.space.id if resp.space and resp.space.id else None
        return ClickUpFolder(
            id=resp.id,
            name=resp.name,
            space_id=space_id,
            override_statuses=resp.override_statuses,
            hidden=resp.hidden,
        )

    @staticmethod
    def to_create_dto(folder: ClickUpFolder) -> FolderCreate:
        return FolderCreate(name=folder.name)

    @staticmethod
    def to_update_dto(folder: ClickUpFolder) -> FolderUpdate:
        return FolderUpdate(name=folder.name)

    @staticmethod
    def to_folder_result_output(folder: ClickUpFolder) -> FolderResult:
        return FolderResult(id=folder.id, name=folder.name, space_id=folder.space_id)

    @staticmethod
    def to_folder_list_item_output(folder: ClickUpFolder) -> FolderListItem:
        return FolderListItem(id=folder.id, name=folder.name)
