"""
Folder DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Folder resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic ClickUpFolder domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_folder_result_output, to_folder_list_item_output)

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.folder_mapper import FolderMapper

    folder_domain = FolderMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    folder_domain = FolderMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = FolderMapper.to_create_dto(folder_domain)

    # Python - Map domain to MCP output
    mcp_output = FolderMapper.to_folder_result_output(folder_domain)
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
    """
    Static mapper for converting between Folder DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Folder data:

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
        # Python - Create a folder from MCP input
        from clickup_mcp.models.mapping.folder_mapper import FolderMapper

        mcp_input = FolderCreateInput(name="Q4 Planning", space_id="space_123")
        folder_domain = FolderMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        folder_domain = FolderMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = FolderMapper.to_create_dto(folder_domain)
        response = await client.folder.create(space_id="space_123", folder_create=create_dto)

        # Python - Return to MCP client
        mcp_output = FolderMapper.to_folder_result_output(folder_domain)
    """

    @staticmethod
    def from_create_input(input: "FolderCreateInput") -> ClickUpFolder:
        """
        Map MCP FolderCreateInput to Folder domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the folder in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual folder is created via API.

        Args:
            input: FolderCreateInput from MCP tool call containing:
                - name: Folder name (required)
                - space_id: Space ID to create folder in (required)

        Returns:
            ClickUpFolder domain entity with:
                - id: Temporary placeholder "temp"
                - name: From input
                - space_id: From input

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            mcp_input = FolderCreateInput(
                name="Q4 Planning",
                space_id="space_123"
            )
            folder = FolderMapper.from_create_input(mcp_input)
            # folder.id == "temp"
            # folder.name == "Q4 Planning"
        """
        return ClickUpFolder(id="temp", name=input.name, space_id=input.space_id)

    @staticmethod
    def from_update_input(input: "FolderUpdateInput") -> ClickUpFolder:
        """
        Map MCP FolderUpdateInput to Folder domain entity.

        Converts user-facing MCP update input to a domain entity with the
        folder ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Args:
            input: FolderUpdateInput from MCP tool call containing:
                - folder_id: Folder ID to update (required)
                - name: Updated folder name (optional)

        Returns:
            ClickUpFolder domain entity with:
                - id: From input.folder_id
                - name: From input or empty string

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            mcp_input = FolderUpdateInput(
                folder_id="folder_123",
                name="Updated Folder Name"
            )
            folder = FolderMapper.from_update_input(mcp_input)
            # folder.id == "folder_123"
            # folder.name == "Updated Folder Name"
        """
        return ClickUpFolder(id=input.folder_id, name=input.name or "")

    @staticmethod
    def to_domain(resp: FolderResp) -> ClickUpFolder:
        """
        Map ClickUp API response DTO to Folder domain entity.

        Converts the ClickUp API response (FolderResp DTO) to a domain entity,
        extracting relevant fields and transforming nested structures. This
        is the primary entry point for API responses.

        Args:
            resp: FolderResp DTO from ClickUp API containing:
                - id: Folder ID
                - name: Folder name
                - space: Space object with ID
                - override_statuses: Whether folder overrides statuses
                - hidden: Whether folder is hidden

        Returns:
            ClickUpFolder domain entity with all fields populated

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            api_response = FolderResp(
                id="folder_123",
                name="Q4 Planning",
                space=SpaceObj(id="space_456"),
                override_statuses=True
            )
            folder = FolderMapper.to_domain(api_response)
            # folder.id == "folder_123"
            # folder.space_id == "space_456"
        """
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
        """
        Map Folder domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new folder.

        Args:
            folder: ClickUpFolder domain entity containing folder data

        Returns:
            FolderCreate DTO with folder name

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            folder = ClickUpFolder(
                id="temp",
                name="Q4 Planning",
                space_id="space_123"
            )
            create_dto = FolderMapper.to_create_dto(folder)
            # create_dto.name == "Q4 Planning"
        """
        return FolderCreate(name=folder.name)

    @staticmethod
    def to_update_dto(folder: ClickUpFolder) -> FolderUpdate:
        """
        Map Folder domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing folder.

        Args:
            folder: ClickUpFolder domain entity with updated data

        Returns:
            FolderUpdate DTO with folder name

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            folder = ClickUpFolder(
                id="folder_123",
                name="Updated Folder Name",
                space_id="space_456"
            )
            update_dto = FolderMapper.to_update_dto(folder)
            # update_dto.name == "Updated Folder Name"
        """
        return FolderUpdate(name=folder.name)

    @staticmethod
    def to_folder_result_output(folder: ClickUpFolder) -> "FolderResult":
        """
        Map Folder domain entity to MCP FolderResult output.

        Converts a domain entity to the MCP output format for returning
        folder details to the MCP client. This is used for single folder
        responses (get, create, update operations).

        Args:
            folder: ClickUpFolder domain entity to convert

        Returns:
            FolderResult MCP output model with id, name, and space_id

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            folder = ClickUpFolder(
                id="folder_123",
                name="Q4 Planning",
                space_id="space_456"
            )
            mcp_output = FolderMapper.to_folder_result_output(folder)
            # mcp_output.id == "folder_123"
            # mcp_output.name == "Q4 Planning"
        """
        from clickup_mcp.mcp_server.models.outputs.folder import FolderResult

        return FolderResult(id=folder.id, name=folder.name, space_id=folder.space_id)

    @staticmethod
    def to_folder_list_item_output(folder: ClickUpFolder) -> "FolderListItem":
        """
        Map Folder domain entity to MCP FolderListItem output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple folders
        in a list (get_all operation).

        Args:
            folder: ClickUpFolder domain entity to convert

        Returns:
            FolderListItem MCP output model with id and name

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.folder_mapper import FolderMapper

            folder = ClickUpFolder(
                id="folder_123",
                name="Q4 Planning",
                space_id="space_456"
            )
            list_item = FolderMapper.to_folder_list_item_output(folder)
            # list_item.id == "folder_123"
            # list_item.name == "Q4 Planning"
        """
        from clickup_mcp.mcp_server.models.outputs.folder import FolderListItem

        return FolderListItem(id=folder.id, name=folder.name)
