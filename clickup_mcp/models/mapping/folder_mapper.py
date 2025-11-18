"""Folder DTO ↔ Domain mappers.

Translate between Folder transport DTOs and the ClickUpFolder domain entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.folder import ClickUpFolder
from clickup_mcp.models.dto.folder import FolderCreate, FolderResp, FolderUpdate

if TYPE_CHECKING:  # only for type hints; avoids circular import at runtime
    from clickup_mcp.mcp_server.models.inputs.folder import (
        FolderCreateInput,
        FolderUpdateInput,
    )
    from clickup_mcp.mcp_server.models.outputs.folder import (
        FolderListItem,
        FolderResult,
    )


class FolderMapper:
    """Static helpers to convert between Folder DTOs and domain entity."""

    @staticmethod
    def from_create_input(input: "FolderCreateInput") -> ClickUpFolder:
        """Map MCP FolderCreateInput to Folder domain entity."""
        return ClickUpFolder(id="temp", name=input.name, space_id=input.space_id)

    @staticmethod
    def from_update_input(input: "FolderUpdateInput") -> ClickUpFolder:
        """Map MCP FolderUpdateInput to Folder domain entity."""
        return ClickUpFolder(id=input.folder_id, name=input.name or "")

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
    def to_folder_result_output(folder: ClickUpFolder) -> "FolderResult":
        from clickup_mcp.mcp_server.models.outputs.folder import FolderResult

        return FolderResult(id=folder.id, name=folder.name, space_id=folder.space_id)

    @staticmethod
    def to_folder_list_item_output(folder: ClickUpFolder) -> "FolderListItem":
        from clickup_mcp.mcp_server.models.outputs.folder import FolderListItem

        return FolderListItem(id=folder.id, name=folder.name)
