"""Unit tests for TeamMapper Domain  Output conversions."""

from clickup_mcp.models.domain.team import ClickUpTeam
from clickup_mcp.models.mapping.team_mapper import TeamMapper


def test_domain_to_workspace_list_item_and_result() -> None:
    t1 = ClickUpTeam(team_id="t1", name="Team One")
    t2 = ClickUpTeam(id="t2", name="Team Two")

    item1 = TeamMapper.to_workspace_list_item_output(t1)
    assert item1.team_id == "t1"
    assert item1.name == "Team One"

    item2 = TeamMapper.to_workspace_list_item_output(t2)
    assert item2.team_id == "t2"
    assert item2.name == "Team Two"

    res = TeamMapper.to_workspace_list_result_output([t1, t2])
    assert len(res.items) == 2
    assert {i.team_id for i in res.items} == {"t1", "t2"}
