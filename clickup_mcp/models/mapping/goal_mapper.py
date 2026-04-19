"""
Goal DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Goal resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic Goal domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_goal_result_output, to_goal_list_item_output)

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.goal_mapper import GoalMapper

    goal_domain = GoalMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    goal_domain = GoalMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = GoalMapper.to_create_dto(goal_domain)

    # Python - Map domain to MCP output
    mcp_output = GoalMapper.to_goal_result_output(goal_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.goal import Goal
from clickup_mcp.models.dto.goal import GoalCreate, GoalResponse, GoalUpdate

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.goal import (
        GoalCreateInput,
        GoalUpdateInput,
    )


class GoalMapper:
    """
    Static mapper for converting between Goal DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Goal data:

    1. **MCP Input → Domain**: Converts user-facing MCP input models to domain entities
    2. **API Response → Domain**: Converts ClickUp API responses to domain entities
    3. **Domain → API Request**: Converts domain entities to ClickUp API request DTOs
    4. **Domain → MCP Output**: Converts domain entities to user-facing MCP output models

    Key Design Principles:
    - **Separation of Concerns**: Domain logic is isolated from transport details
    - **Unidirectional Flow**: Data flows in one direction through the mapper
    - **Testability**: Each mapping can be tested independently
    - **Maintainability**: Changes to DTOs don't affect domain logic

    Attributes:
        None - This is a static utility class with no instance state

    Usage Examples:
        # Python - Create a goal from MCP input
        from clickup_mcp.models.mapping.goal_mapper import GoalMapper

        mcp_input = GoalCreateInput(
            team_id="team_1",
            name="Q1 Revenue Goal",
            description="Achieve $1M in revenue",
            due_date=1702080000000
        )
        goal_domain = GoalMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        goal_domain = GoalMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = GoalMapper.to_create_dto(goal_domain)

        # Python - Return to MCP client
        mcp_output = GoalMapper.to_goal_result_output(goal_domain)
    """

    @staticmethod
    def from_create_input(input: "GoalCreateInput") -> Goal:
        """
        Map MCP GoalCreateInput to Goal domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the goal in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual goal is created via API.

        Args:
            input: GoalCreateInput from MCP tool call containing:
                - team_id: Team/workspace ID (required)
                - name: Goal name/title (required)
                - description: Description of the goal (optional)
                - due_date: Due date in epoch ms (required)
                - key_results: List of key result names (optional)
                - multiple_owners: Whether multiple users can own this goal (optional)
                - owners: List of user IDs who own this goal (optional)

        Returns:
            Goal domain entity with:
                - goal_id: Temporary placeholder "temp" (will be replaced after API creation)
                - team_id: From input.team_id
                - name: From input.name
                - description: From input.description
                - due_date: From input.due_date
                - status: "active" (default)
                - key_results: From input.key_results
                - owners: From input.owners
                - multiple_owners: From input.multiple_owners

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper

            mcp_input = GoalCreateInput(
                team_id="team_1",
                name="Q1 Revenue Goal",
                due_date=1702080000000
            )
            goal = GoalMapper.from_create_input(mcp_input)
            # goal.goal_id == "temp"
            # goal.team_id == "team_1"
            # goal.name == "Q1 Revenue Goal"
        """
        return Goal(
            id="temp",
            team_id=input.team_id,
            name=input.name,
            description=input.description,
            due_date=input.due_date,
            status="active",
            key_results=input.key_results or [],
            owners=input.owners or [],
            multiple_owners=input.multiple_owners,
        )

    @staticmethod
    def from_update_input(input: "GoalUpdateInput") -> Goal:
        """
        Map MCP GoalUpdateInput to Goal domain entity.

        Converts user-facing MCP update input to a domain entity with the
        goal ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Args:
            input: GoalUpdateInput from MCP tool call containing:
                - goal_id: Goal ID to update (required)
                - name: Updated goal name (optional)
                - description: Updated description (optional)
                - due_date: Updated due date in epoch ms (optional)
                - key_results: Updated list of key result names (optional)
                - owners: Updated list of user IDs (optional)
                - status: Updated goal status (optional)

        Returns:
            Goal domain entity with:
                - goal_id: From input.goal_id
                - team_id: Placeholder "temp" (not needed for update)
                - name: From input.name
                - description: From input.description
                - due_date: From input.due_date
                - status: From input.status
                - key_results: From input.key_results
                - owners: From input.owners
                - multiple_owners: False (default)

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper

            mcp_input = GoalUpdateInput(
                goal_id="goal_123",
                name="Updated Goal Name"
            )
            goal = GoalMapper.from_update_input(mcp_input)
            # goal.goal_id == "goal_123"
            # goal.name == "Updated Goal Name"
        """
        return Goal(
            id=input.goal_id,
            team_id="temp",
            name=input.name or "temp",
            description=input.description,
            due_date=input.due_date,
            status=input.status or "active",
            key_results=input.key_results or [],
            owners=input.owners or [],
            multiple_owners=False,
        )

    @staticmethod
    def to_domain(resp: GoalResponse) -> Goal:
        """
        Map ClickUp API response DTO to Goal domain entity.

        Converts the ClickUp API response (GoalResponse DTO) to a domain entity,
        extracting relevant fields. This is the primary entry point for API responses.

        Args:
            resp: GoalResponse DTO from ClickUp API containing:
                - id: Goal ID
                - team_id: Team/workspace ID this goal belongs to
                - name: Goal name/title
                - description: Description of the goal
                - due_date: Due date in epoch milliseconds
                - status: Goal status
                - key_results: List of key result names
                - owners: List of user IDs who own this goal
                - multiple_owners: Whether multiple users can own this goal
                - date_created: Creation date in epoch milliseconds
                - date_updated: Last update date in epoch milliseconds

        Returns:
            Goal domain entity with:
                - goal_id: From resp.id
                - team_id: From resp.team_id
                - name: From resp.name
                - description: From resp.description
                - due_date: From resp.due_date
                - status: From resp.status
                - key_results: From resp.key_results
                - owners: From resp.owners
                - multiple_owners: From resp.multiple_owners
                - date_created: From resp.date_created
                - date_updated: From resp.date_updated

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper
            from clickup_mcp.models.dto.goal import GoalResponse

            api_response = GoalResponse(
                id="goal_123",
                team_id="team_001",
                name="Q1 Revenue Goal",
                due_date=1702080000000
            )
            goal = GoalMapper.to_domain(api_response)
            # goal.goal_id == "goal_123"
            # goal.team_id == "team_001"
            # goal.name == "Q1 Revenue Goal"
        """
        return Goal(
            id=resp.id,
            team_id=resp.team_id,
            name=resp.name,
            description=resp.description,
            due_date=resp.due_date,
            status=resp.status,
            key_results=resp.key_results,
            owners=resp.owners,
            multiple_owners=resp.multiple_owners,
            date_created=resp.date_created,
            date_updated=resp.date_updated,
        )

    @staticmethod
    def to_create_dto(goal: Goal) -> GoalCreate:
        """
        Map Goal domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new goal.

        Args:
            goal: Goal domain entity containing goal data

        Returns:
            GoalCreate DTO with:
                - name: From goal.name
                - description: From goal.description
                - due_date: From goal.due_date
                - key_results: From goal.key_results
                - multiple_owners: From goal.multiple_owners
                - owners: From goal.owners

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper

            goal = Goal(
                id="temp",
                team_id="team_001",
                name="Q1 Revenue Goal",
                due_date=1702080000000
            )
            create_dto = GoalMapper.to_create_dto(goal)
            # create_dto.name == "Q1 Revenue Goal"
            # create_dto.due_date == 1702080000000

            # Python - Use with API client
            response = await client.goal.create(
                team_id="team_001",
                goal_create=create_dto
            )
        """
        return GoalCreate(
            name=goal.name,
            description=goal.description,
            due_date=goal.due_date,
            key_results=goal.key_results,
            multiple_owners=goal.multiple_owners,
            owners=goal.owners,
        )

    @staticmethod
    def to_update_dto(goal: Goal) -> GoalUpdate:
        """
        Map Goal domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing goal.

        Args:
            goal: Goal domain entity with updated data

        Returns:
            GoalUpdate DTO with:
                - name: From goal.name
                - description: From goal.description
                - due_date: From goal.due_date
                - key_results: From goal.key_results
                - owners: From goal.owners
                - status: From goal.status

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper

            goal = Goal(
                id="goal_123",
                team_id="team_001",
                name="Updated Goal Name",
                due_date=1702080000000
            )
            update_dto = GoalMapper.to_update_dto(goal)
            # update_dto.name == "Updated Goal Name"

            # Python - Use with API client
            response = await client.goal.update(
                goal_id="goal_123",
                goal_update=update_dto
            )
        """
        return GoalUpdate(
            name=goal.name,
            description=goal.description,
            due_date=goal.due_date,
            key_results=goal.key_results,
            owners=goal.owners,
            status=goal.status,
        )

    @staticmethod
    def to_goal_result_output(goal: Goal) -> dict:
        """
        Map Goal domain entity to MCP goal result output.

        Converts a domain entity to the MCP output format for returning
        goal details to the MCP client. This is used for single goal
        responses (get, create, update operations).

        Args:
            goal: Goal domain entity to convert

        Returns:
            Dictionary with goal data:
                - id: From goal.goal_id
                - team_id: From goal.team_id
                - name: From goal.name
                - description: From goal.description
                - due_date: From goal.due_date
                - status: From goal.status
                - key_results: From goal.key_results
                - owners: From goal.owners
                - multiple_owners: From goal.multiple_owners
                - date_created: From goal.date_created
                - date_updated: From goal.date_updated

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper

            goal = Goal(
                id="goal_123",
                team_id="team_001",
                name="Q1 Revenue Goal",
                due_date=1702080000000
            )
            mcp_output = GoalMapper.to_goal_result_output(goal)
            # mcp_output["id"] == "goal_123"
            # mcp_output["name"] == "Q1 Revenue Goal"

            # Python - Return from MCP tool
            return mcp_output
        """
        return {
            "id": goal.goal_id,
            "team_id": goal.team_id,
            "name": goal.name,
            "description": goal.description,
            "due_date": goal.due_date,
            "status": goal.status,
            "key_results": goal.key_results,
            "owners": goal.owners,
            "multiple_owners": goal.multiple_owners,
            "date_created": goal.date_created,
            "date_updated": goal.date_updated,
        }

    @staticmethod
    def to_goal_list_item_output(goal: Goal) -> dict:
        """
        Map Goal domain entity to MCP goal list item output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple goals
        in a list.

        Args:
            goal: Goal domain entity to convert

        Returns:
            Dictionary with goal list item data:
                - id: From goal.goal_id
                - team_id: From goal.team_id
                - name: From goal.name
                - description: From goal.description
                - due_date: From goal.due_date
                - status: From goal.status

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.goal_mapper import GoalMapper

            goal = Goal(
                id="goal_123",
                team_id="team_001",
                name="Q1 Revenue Goal",
                due_date=1702080000000
            )
            list_item = GoalMapper.to_goal_list_item_output(goal)
            # list_item["id"] == "goal_123"
            # list_item["name"] == "Q1 Revenue Goal"

            # Python - Return from MCP tool (in a list)
            goals = [GoalMapper.to_goal_list_item_output(g) for g in domain_goals]
            return goals
        """
        return {
            "id": goal.goal_id,
            "team_id": goal.team_id,
            "name": goal.name,
            "description": goal.description,
            "due_date": goal.due_date,
            "status": goal.status,
        }
