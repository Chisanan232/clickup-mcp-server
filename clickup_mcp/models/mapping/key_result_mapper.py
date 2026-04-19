"""
Key Result DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Key Result resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic KeyResult domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_key_result_result_output)

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

    kr_domain = KeyResultMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    kr_domain = KeyResultMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = KeyResultMapper.to_create_dto(kr_domain)

    # Python - Map domain to MCP output
    mcp_output = KeyResultMapper.to_key_result_result_output(kr_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.key_result import KeyResult
from clickup_mcp.models.dto.key_result import KeyResultCreate, KeyResultResponse, KeyResultUpdate

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.key_result import KeyResultCreateInput, KeyResultUpdateInput


class KeyResultMapper:
    """
    Static mapper for converting between Key Result DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Key Result data:

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
        # Python - Create a key result from MCP input
        from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

        mcp_input = KeyResultCreateInput(
            goal_id="goal_1",
            name="Increase MRR",
            type="currency",
            target=1000000,
            unit="$"
        )
        kr_domain = KeyResultMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        kr_domain = KeyResultMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = KeyResultMapper.to_create_dto(kr_domain)

        # Python - Return to MCP client
        mcp_output = KeyResultMapper.to_key_result_result_output(kr_domain)
    """

    @staticmethod
    def from_create_input(input: "KeyResultCreateInput") -> KeyResult:
        """
        Map MCP KeyResultCreateInput to KeyResult domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the key result in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual key result is created via API.

        Args:
            input: KeyResultCreateInput from MCP tool call containing:
                - goal_id: Goal ID (required)
                - name: Key result name (required)
                - type: Key result type (required)
                - target: Target value (required)
                - unit: Unit of measurement (optional)
                - description: Description of the key result (optional)

        Returns:
            KeyResult domain entity with:
                - key_result_id: Temporary placeholder "temp"
                - goal_id: From input.goal_id
                - name: From input.name
                - type: From input.type
                - target: From input.target
                - current: 0.0 (default)
                - unit: From input.unit
                - description: From input.description

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

            mcp_input = KeyResultCreateInput(
                goal_id="goal_1",
                name="Increase MRR",
                type="currency",
                target=1000000
            )
            kr = KeyResultMapper.from_create_input(mcp_input)
            # kr.key_result_id == "temp"
            # kr.goal_id == "goal_1"
            # kr.name == "Increase MRR"
        """
        return KeyResult(
            id="temp",
            goal_id=input.goal_id,
            name=input.name,
            type=input.type,
            target=input.target,
            current=0.0,
            unit=input.unit,
            description=input.description,
        )

    @staticmethod
    def from_update_input(input: "KeyResultUpdateInput") -> KeyResult:
        """
        Map MCP KeyResultUpdateInput to KeyResult domain entity.

        Converts user-facing MCP update input to a domain entity with the
        key result ID and updated properties.

        Args:
            input: KeyResultUpdateInput from MCP tool call containing:
                - key_result_id: Key result ID to update (required)
                - name: Updated key result name (optional)
                - target: Updated target value (optional)
                - current: Updated current value (optional)
                - unit: Updated unit of measurement (optional)
                - description: Updated description (optional)

        Returns:
            KeyResult domain entity with:
                - key_result_id: From input.key_result_id
                - goal_id: Placeholder "temp"
                - name: From input.name
                - target: From input.target
                - current: From input.current
                - unit: From input.unit
                - description: From input.description

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

            mcp_input = KeyResultUpdateInput(
                key_result_id="kr_123",
                target=2000000
            )
            kr = KeyResultMapper.from_update_input(mcp_input)
            # kr.key_result_id == "kr_123"
            # kr.target == 2000000
        """
        return KeyResult(
            id=input.key_result_id,
            goal_id="temp",
            name=input.name or "temp",
            type="number",
            target=input.target or 0.0,
            current=input.current or 0.0,
            unit=input.unit,
            description=input.description,
        )

    @staticmethod
    def to_domain(resp: KeyResultResponse) -> KeyResult:
        """
        Map ClickUp API response DTO to KeyResult domain entity.

        Converts the ClickUp API response (KeyResultResponse DTO) to a domain entity,
        extracting relevant fields.

        Args:
            resp: KeyResultResponse DTO from ClickUp API containing:
                - id: Key result ID
                - goal_id: Goal ID this key result belongs to
                - name: Key result name
                - type: Key result type
                - target: Target value
                - current: Current value
                - unit: Unit of measurement
                - description: Description of the key result
                - date_created: Creation date in epoch milliseconds
                - date_updated: Last update date in epoch milliseconds

        Returns:
            KeyResult domain entity with:
                - key_result_id: From resp.id
                - goal_id: From resp.goal_id
                - name: From resp.name
                - type: From resp.type
                - target: From resp.target
                - current: From resp.current
                - unit: From resp.unit
                - description: From resp.description
                - date_created: From resp.date_created
                - date_updated: From resp.date_updated

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper
            from clickup_mcp.models.dto.key_result import KeyResultResponse

            api_response = KeyResultResponse(
                id="kr_123",
                goal_id="goal_001",
                name="Increase MRR",
                target=1000000,
                current=500000
            )
            kr = KeyResultMapper.to_domain(api_response)
            # kr.key_result_id == "kr_123"
            # kr.goal_id == "goal_001"
        """
        return KeyResult(
            id=resp.id,
            goal_id=resp.goal_id,
            name=resp.name,
            type=resp.type,
            target=resp.target,
            current=resp.current,
            unit=resp.unit,
            description=resp.description,
            date_created=resp.date_created,
            date_updated=resp.date_updated,
        )

    @staticmethod
    def to_create_dto(key_result: KeyResult) -> KeyResultCreate:
        """
        Map KeyResult domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new key result.

        Args:
            key_result: KeyResult domain entity containing key result data

        Returns:
            KeyResultCreate DTO with:
                - name: From key_result.name
                - type: From key_result.type
                - target: From key_result.target
                - unit: From key_result.unit
                - description: From key_result.description

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

            kr = KeyResult(
                id="temp",
                goal_id="goal_001",
                name="Increase MRR",
                type="currency",
                target=1000000
            )
            create_dto = KeyResultMapper.to_create_dto(kr)
            # create_dto.name == "Increase MRR"
            # create_dto.target == 1000000
        """
        return KeyResultCreate(
            name=key_result.name,
            type=key_result.type,
            target=key_result.target,
            unit=key_result.unit,
            description=key_result.description,
        )

    @staticmethod
    def to_update_dto(key_result: KeyResult) -> KeyResultUpdate:
        """
        Map KeyResult domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing key result.

        Args:
            key_result: KeyResult domain entity with updated data

        Returns:
            KeyResultUpdate DTO with:
                - name: From key_result.name
                - target: From key_result.target
                - current: From key_result.current
                - unit: From key_result.unit
                - description: From key_result.description

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

            kr = KeyResult(
                id="kr_123",
                goal_id="goal_001",
                name="Increase MRR",
                type="currency",
                target=2000000,
                current=750000
            )
            update_dto = KeyResultMapper.to_update_dto(kr)
            # update_dto.target == 2000000
        """
        return KeyResultUpdate(
            name=key_result.name,
            target=key_result.target,
            current=key_result.current,
            unit=key_result.unit,
            description=key_result.description,
        )

    @staticmethod
    def to_key_result_result_output(key_result: KeyResult) -> dict:
        """
        Map KeyResult domain entity to MCP key result result output.

        Converts a domain entity to the MCP output format for returning
        key result details to the MCP client.

        Args:
            key_result: KeyResult domain entity to convert

        Returns:
            Dictionary with key result data:
                - id: From key_result.key_result_id
                - goal_id: From key_result.goal_id
                - name: From key_result.name
                - type: From key_result.type
                - target: From key_result.target
                - current: From key_result.current
                - unit: From key_result.unit
                - description: From key_result.description
                - date_created: From key_result.date_created
                - date_updated: From key_result.date_updated

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.key_result_mapper import KeyResultMapper

            kr = KeyResult(
                id="kr_123",
                goal_id="goal_001",
                name="Increase MRR",
                target=1000000,
                current=500000
            )
            mcp_output = KeyResultMapper.to_key_result_result_output(kr)
            # mcp_output["id"] == "kr_123"
            # mcp_output["name"] == "Increase MRR"
        """
        return {
            "id": key_result.key_result_id,
            "goal_id": key_result.goal_id,
            "name": key_result.name,
            "type": key_result.type,
            "target": key_result.target,
            "current": key_result.current,
            "unit": key_result.unit,
            "description": key_result.description,
            "date_created": key_result.date_created,
            "date_updated": key_result.date_updated,
        }
