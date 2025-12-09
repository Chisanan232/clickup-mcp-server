"""Team domain → MCP output mappers.

Translate between Team domain entities and Workspace MCP output models.

Usage Examples:
    # Python - Single team to list item
    from clickup_mcp.models.mapping.team_mapper import TeamMapper
    from clickup_mcp.models.domain.team import ClickUpTeam

    team = ClickUpTeam(id="team_123", name="Engineering")
    item = TeamMapper.to_workspace_list_item_output(team)

    # Python - Multiple teams to list result
    result = TeamMapper.to_workspace_list_result_output([
        ClickUpTeam(id="team_1", name="Eng"),
        ClickUpTeam(id="team_2", name="Product"),
    ])
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List

from clickup_mcp.models.domain.team import ClickUpTeam

if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.outputs.workspace import (
        WorkspaceListItem,
        WorkspaceListResult,
    )


class TeamMapper:
    """
    Static mapper for converting Team domain entities to MCP output models.

    This class provides mappings from Team domain entities to Workspace MCP output models.
    Unlike other mappers, this focuses on output mapping only, as Teams are typically
    read-only resources from the MCP perspective.

    Key Design Principles:
    - **Output-Only Mapping**: Converts domain entities to MCP output formats
    - **Null Safety**: Handles missing team_id and name fields gracefully
    - **Backward Compatibility**: Handles both team_id and id fields
    - **Testability**: Each mapping can be tested independently

    Attributes:
        None - This is a static utility class with no instance state

    Usage Examples:
        # Python - Convert single team to list item
        from clickup_mcp.models.mapping.team_mapper import TeamMapper

        team = ClickUpTeam(id="team_123", name="Engineering")
        list_item = TeamMapper.to_workspace_list_item_output(team)

        # Python - Convert multiple teams to list result
        teams = [
            ClickUpTeam(id="team_123", name="Engineering"),
            ClickUpTeam(id="team_456", name="Product")
        ]
        list_result = TeamMapper.to_workspace_list_result_output(teams)
    """

    @staticmethod
    def to_workspace_list_item_output(team: ClickUpTeam) -> "WorkspaceListItem":
        """
        Map Team domain entity to MCP WorkspaceListItem output.

        Converts a domain entity to the MCP output format for list items.
        This is a lightweight representation used when returning teams in a list.

        Handles backward compatibility by checking both team_id and id fields.
        Provides sensible defaults for missing values.

        Args:
            team: ClickUpTeam domain entity to convert

        Returns:
            WorkspaceListItem MCP output model with team_id and name

        Usage Examples:
            # Python - Convert single team to list item
            from clickup_mcp.models.mapping.team_mapper import TeamMapper

            team = ClickUpTeam(
                id="team_123",
                name="Engineering"
            )
            list_item = TeamMapper.to_workspace_list_item_output(team)
            # list_item.team_id == "team_123"
            # list_item.name == "Engineering"

            # Python - Handle missing name
            team = ClickUpTeam(id="team_123", name=None)
            list_item = TeamMapper.to_workspace_list_item_output(team)
            # list_item.name == "" (empty string default)
        """
        from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListItem

        team_id_val = team.team_id or team.id or ""
        name_val = team.name or ""
        return WorkspaceListItem(team_id=str(team_id_val), name=name_val)

    @staticmethod
    def to_workspace_list_result_output(teams: Iterable[ClickUpTeam]) -> "WorkspaceListResult":
        """
        Map multiple Team domain entities to MCP WorkspaceListResult output.

        Converts an iterable of domain entities to the MCP output format for list results.
        This is used when returning multiple teams (e.g., from a get_all operation).

        Args:
            teams: Iterable of ClickUpTeam domain entities to convert

        Returns:
            WorkspaceListResult MCP output model containing list of WorkspaceListItem

        Usage Examples:
            # Python - Convert multiple teams to list result
            from clickup_mcp.models.mapping.team_mapper import TeamMapper

            teams = [
                ClickUpTeam(id="team_123", name="Engineering"),
                ClickUpTeam(id="team_456", name="Product"),
                ClickUpTeam(id="team_789", name="Design")
            ]
            list_result = TeamMapper.to_workspace_list_result_output(teams)
            # list_result.items has 3 WorkspaceListItem objects

            # Python - Convert from API response
            api_teams = await client.team.get_all()
            domain_teams = [TeamMapper.to_domain(t) for t in api_teams]
            mcp_output = TeamMapper.to_workspace_list_result_output(domain_teams)
        """
        from clickup_mcp.mcp_server.models.outputs.workspace import (
            WorkspaceListItem,
            WorkspaceListResult,
        )

        items: List[WorkspaceListItem] = [TeamMapper.to_workspace_list_item_output(t) for t in teams]
        return WorkspaceListResult(items=items)
