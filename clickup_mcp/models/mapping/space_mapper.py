"""Space DTO ↔ Domain mappers.

Translate between Space transport DTOs and the ClickUpSpace domain entity.
"""

from __future__ import annotations

from clickup_mcp.models.domain.space import ClickUpSpace
from clickup_mcp.models.dto.space import SpaceCreate, SpaceResp, SpaceUpdate
from clickup_mcp.mcp_server.models.outputs.space import SpaceListItem, SpaceResult


class SpaceMapper:
    """Static helpers to convert between Space DTOs and domain entity."""

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
    def to_space_result_output(space: ClickUpSpace) -> SpaceResult:
        return SpaceResult(id=space.id, name=space.name, private=space.private, team_id=space.team_id)

    @staticmethod
    def to_space_list_item_output(space: ClickUpSpace) -> SpaceListItem:
        return SpaceListItem(id=space.id, name=space.name)
