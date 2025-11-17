"""Space DTO ↔ Domain mappers.

Translate between Space transport DTOs and the ClickUpSpace domain entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.space import ClickUpSpace
from clickup_mcp.models.dto.space import SpaceCreate, SpaceResp, SpaceUpdate
if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.outputs.space import SpaceListItem, SpaceResult
    from clickup_mcp.mcp_server.models.inputs.space import SpaceCreateInput, SpaceUpdateInput


class SpaceMapper:
    """Static helpers to convert between Space DTOs and domain entity."""

    @staticmethod
    def from_create_input(input: "SpaceCreateInput") -> ClickUpSpace:
        """Map MCP SpaceCreateInput to Space domain entity."""
        return ClickUpSpace(id="temp", name=input.name, multiple_assignees=input.multiple_assignees or False)

    @staticmethod
    def from_update_input(input: "SpaceUpdateInput") -> ClickUpSpace:
        """Map MCP SpaceUpdateInput to Space domain entity."""
        return ClickUpSpace(
            id=input.space_id,
            name=input.name or "",
            private=bool(input.private) if input.private is not None else False,
            multiple_assignees=bool(input.multiple_assignees) if input.multiple_assignees is not None else False,
        )

    @staticmethod
    def to_domain(resp: SpaceResp) -> ClickUpSpace:
        return ClickUpSpace(
            id=resp.id,
            name=resp.name,
            private=resp.private,
            statuses=[s.model_dump(exclude_none=True) for s in (resp.statuses or [])],
            multiple_assignees=resp.multiple_assignees,
            features=resp.features.to_payload() if resp.features else None,
            team_id=resp.team_id,
        )

    @staticmethod
    def to_create_dto(space: ClickUpSpace) -> SpaceCreate:
        return SpaceCreate(
            name=space.name,
            multiple_assignees=space.multiple_assignees,
            color=None,
            features=None,  # leave feature provisioning to service layer if needed
        )

    @staticmethod
    def to_update_dto(space: ClickUpSpace) -> SpaceUpdate:
        return SpaceUpdate(
            name=space.name,
            private=space.private,
            multiple_assignees=space.multiple_assignees,
            color=None,
            features=None,
        )

    @staticmethod
    def to_space_result_output(space: ClickUpSpace) -> "SpaceResult":
        from clickup_mcp.mcp_server.models.outputs.space import SpaceResult

        return SpaceResult(id=space.id, name=space.name, private=space.private, team_id=space.team_id)

    @staticmethod
    def to_space_list_item_output(space: ClickUpSpace) -> "SpaceListItem":
        from clickup_mcp.mcp_server.models.outputs.space import SpaceListItem

        return SpaceListItem(id=space.id, name=space.name)
