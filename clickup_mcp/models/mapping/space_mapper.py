"""
Space DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Space resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic ClickUpSpace domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_space_result_output, to_space_list_item_output)

This separation ensures:
- Domain logic remains independent of transport details
- DTOs can change without affecting domain behavior
- Easy testing and mocking of domain operations
- Clear responsibility boundaries

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.space_mapper import SpaceMapper

    space_domain = SpaceMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    space_domain = SpaceMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = SpaceMapper.to_create_dto(space_domain)

    # Python - Map domain to MCP output
    mcp_output = SpaceMapper.to_space_result_output(space_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.space import ClickUpSpace
from clickup_mcp.models.dto.space import SpaceCreate, SpaceResp, SpaceUpdate

if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.inputs.space import (
        SpaceCreateInput,
        SpaceUpdateInput,
    )
    from clickup_mcp.mcp_server.models.outputs.space import SpaceListItem, SpaceResult


class SpaceMapper:
    """
    Static mapper for converting between Space DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Space data:

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
        # Python - Create a space from MCP input
        from clickup_mcp.models.mapping.space_mapper import SpaceMapper
        from clickup_mcp.mcp_server.models.inputs.space import SpaceCreateInput

        mcp_input = SpaceCreateInput(name="My Space", multiple_assignees=True)
        space_domain = SpaceMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        space_domain = SpaceMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = SpaceMapper.to_create_dto(space_domain)
        response = await client.space.create(team_id="123", space_create=create_dto)

        # Python - Return to MCP client
        mcp_output = SpaceMapper.to_space_result_output(space_domain)
    """

    @staticmethod
    def from_create_input(input: "SpaceCreateInput") -> ClickUpSpace:
        """
        Map MCP SpaceCreateInput to Space domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the space in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual space is created via API.

        Args:
            input: SpaceCreateInput from MCP tool call containing:
                - name: Space name (required)
                - multiple_assignees: Whether to allow multiple assignees (optional)

        Returns:
            ClickUpSpace domain entity with:
                - id: Temporary placeholder "temp" (will be replaced after API creation)
                - name: From input
                - multiple_assignees: From input or False if not provided
                - Other fields: Default values

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper

            mcp_input = SpaceCreateInput(
                name="Engineering",
                multiple_assignees=True
            )
            space = SpaceMapper.from_create_input(mcp_input)
            # space.id == "temp"
            # space.name == "Engineering"
            # space.multiple_assignees == True
        """
        return ClickUpSpace(id="temp", name=input.name, multiple_assignees=input.multiple_assignees or False)

    @staticmethod
    def from_update_input(input: "SpaceUpdateInput") -> ClickUpSpace:
        """
        Map MCP SpaceUpdateInput to Space domain entity.

        Converts user-facing MCP update input to a domain entity with the
        space ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Args:
            input: SpaceUpdateInput from MCP tool call containing:
                - space_id: Space ID to update (required)
                - name: Updated space name (optional)
                - private: Whether space is private (optional)
                - multiple_assignees: Whether to allow multiple assignees (optional)

        Returns:
            ClickUpSpace domain entity with:
                - id: From input.space_id
                - name: From input or empty string
                - private: From input or False
                - multiple_assignees: From input or False
                - Other fields: Default values

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper

            mcp_input = SpaceUpdateInput(
                space_id="456",
                name="Updated Engineering",
                private=True
            )
            space = SpaceMapper.from_update_input(mcp_input)
            # space.id == "456"
            # space.name == "Updated Engineering"
            # space.private == True
        """
        return ClickUpSpace(
            id=input.space_id,
            name=input.name or "",
            private=bool(input.private) if input.private is not None else False,
            multiple_assignees=bool(input.multiple_assignees) if input.multiple_assignees is not None else False,
        )

    @staticmethod
    def to_domain(resp: SpaceResp) -> ClickUpSpace:
        """
        Map ClickUp API response DTO to Space domain entity.

        Converts the ClickUp API response (SpaceResp DTO) to a domain entity,
        extracting relevant fields and transforming nested structures. This
        is the primary entry point for API responses.

        Args:
            resp: SpaceResp DTO from ClickUp API containing:
                - id: Space ID
                - name: Space name
                - private: Privacy setting
                - statuses: List of status definitions
                - multiple_assignees: Multiple assignee setting
                - features: Feature configuration
                - team_id: Parent team ID

        Returns:
            ClickUpSpace domain entity with:
                - id: From resp.id
                - name: From resp.name
                - private: From resp.private
                - statuses: Serialized status objects
                - multiple_assignees: From resp.multiple_assignees
                - features: Serialized feature payload
                - team_id: From resp.team_id

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper
            from clickup_mcp.models.dto.space import SpaceResp

            api_response = SpaceResp(
                id="456",
                name="Engineering",
                private=False,
                multiple_assignees=True,
                team_id="123"
            )
            space = SpaceMapper.to_domain(api_response)
            # space.id == "456"
            # space.name == "Engineering"
        """
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
        """
        Map Space domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new space. Only includes fields that are relevant for
        creation; feature provisioning is deferred to the service layer.

        Args:
            space: ClickUpSpace domain entity containing space data

        Returns:
            SpaceCreate DTO with:
                - name: From space.name
                - multiple_assignees: From space.multiple_assignees
                - color: None (not set during creation)
                - features: None (deferred to service layer)

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper

            space = ClickUpSpace(
                id="temp",
                name="Engineering",
                multiple_assignees=True
            )
            create_dto = SpaceMapper.to_create_dto(space)
            # create_dto.name == "Engineering"
            # create_dto.multiple_assignees == True

            # Python - Use with API client
            response = await client.space.create(
                team_id="123",
                space_create=create_dto
            )
        """
        return SpaceCreate(
            name=space.name,
            multiple_assignees=space.multiple_assignees,
            color=None,
            features=None,  # leave feature provisioning to service layer if needed
        )

    @staticmethod
    def to_update_dto(space: ClickUpSpace) -> SpaceUpdate:
        """
        Map Space domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing space. Only includes updatable fields.

        Args:
            space: ClickUpSpace domain entity with updated data

        Returns:
            SpaceUpdate DTO with:
                - name: From space.name
                - private: From space.private
                - multiple_assignees: From space.multiple_assignees
                - color: None (not updated)
                - features: None (deferred to service layer)

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper

            space = ClickUpSpace(
                id="456",
                name="Updated Engineering",
                private=True,
                multiple_assignees=True
            )
            update_dto = SpaceMapper.to_update_dto(space)
            # update_dto.name == "Updated Engineering"
            # update_dto.private == True

            # Python - Use with API client
            response = await client.space.update(
                space_id="456",
                space_update=update_dto
            )
        """
        return SpaceUpdate(
            name=space.name,
            private=space.private,
            multiple_assignees=space.multiple_assignees,
            color=None,
            features=None,
        )

    @staticmethod
    def to_space_result_output(space: ClickUpSpace) -> "SpaceResult":
        """
        Map Space domain entity to MCP SpaceResult output.

        Converts a domain entity to the MCP output format for returning
        space details to the MCP client. This is used for single space
        responses (get, create, update operations).

        Args:
            space: ClickUpSpace domain entity to convert

        Returns:
            SpaceResult MCP output model with:
                - id: From space.id
                - name: From space.name
                - private: From space.private
                - team_id: From space.team_id

        Raises:
            ImportError: If SpaceResult cannot be imported (should not occur in normal operation)

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper

            space = ClickUpSpace(
                id="456",
                name="Engineering",
                private=False,
                team_id="123"
            )
            mcp_output = SpaceMapper.to_space_result_output(space)
            # mcp_output.id == "456"
            # mcp_output.name == "Engineering"
            # mcp_output.private == False
            # mcp_output.team_id == "123"

            # Python - Return from MCP tool
            return mcp_output
        """
        from clickup_mcp.mcp_server.models.outputs.space import SpaceResult

        return SpaceResult(id=space.id, name=space.name, private=space.private, team_id=space.team_id)

    @staticmethod
    def to_space_list_item_output(space: ClickUpSpace) -> "SpaceListItem":
        """
        Map Space domain entity to MCP SpaceListItem output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple spaces
        in a list (get_all operation).

        Args:
            space: ClickUpSpace domain entity to convert

        Returns:
            SpaceListItem MCP output model with:
                - id: From space.id
                - name: From space.name

        Raises:
            ImportError: If SpaceListItem cannot be imported (should not occur in normal operation)

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.space_mapper import SpaceMapper

            space = ClickUpSpace(
                id="456",
                name="Engineering"
            )
            list_item = SpaceMapper.to_space_list_item_output(space)
            # list_item.id == "456"
            # list_item.name == "Engineering"

            # Python - Return from MCP tool (in a list)
            spaces = [SpaceMapper.to_space_list_item_output(s) for s in domain_spaces]
            return spaces
        """
        from clickup_mcp.mcp_server.models.outputs.space import SpaceListItem

        return SpaceListItem(id=space.id, name=space.name)
