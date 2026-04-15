"""
Workspace DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Workspace resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic ClickUpWorkspace domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_workspace_result_output, to_workspace_list_item_output)

This separation ensures:
- Domain logic remains independent of transport details
- DTOs can change without affecting domain behavior
- Easy testing and mocking of domain operations
- Clear responsibility boundaries

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

    workspace_domain = WorkspaceMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    workspace_domain = WorkspaceMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = WorkspaceMapper.to_create_dto(workspace_domain)

    # Python - Map domain to MCP output
    mcp_output = WorkspaceMapper.to_workspace_result_output(workspace_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.workspace import ClickUpWorkspace
from clickup_mcp.models.dto.workspace import WorkspaceCreate, WorkspaceResp, WorkspaceUpdate

if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.inputs.workspace import (
        WorkspaceCreateInput,
        WorkspaceUpdateInput,
    )
    from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListItem, WorkspaceResult


class WorkspaceMapper:
    """
    Static mapper for converting between Workspace DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Workspace data:

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
        # Python - Create a workspace from MCP input
        from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper
        from clickup_mcp.mcp_server.models.inputs.workspace import WorkspaceCreateInput

        mcp_input = WorkspaceCreateInput(name="My Workspace", color="#3498db")
        workspace_domain = WorkspaceMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        workspace_domain = WorkspaceMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = WorkspaceMapper.to_create_dto(workspace_domain)
        response = await client.team.create(workspace_create=create_dto)

        # Python - Return to MCP client
        mcp_output = WorkspaceMapper.to_workspace_result_output(workspace_domain)
    """

    @staticmethod
    def from_create_input(input: "WorkspaceCreateInput") -> ClickUpWorkspace:
        """
        Map MCP WorkspaceCreateInput to Workspace domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the workspace in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual workspace is created via API.

        Args:
            input: WorkspaceCreateInput from MCP tool call containing:
                - name: Workspace name (required)
                - color: Workspace color (optional)
                - avatar: Workspace avatar URL (optional)

        Returns:
            ClickUpWorkspace domain entity with:
                - id: Temporary placeholder "temp" (will be replaced after API creation)
                - name: From input
                - color: From input
                - avatar: From input
                - Other fields: Default values

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

            mcp_input = WorkspaceCreateInput(
                name="Engineering Team",
                color="#3498db"
            )
            workspace = WorkspaceMapper.from_create_input(mcp_input)
            # workspace.id == "temp"
            # workspace.name == "Engineering Team"
            # workspace.color == "#3498db"
        """
        return ClickUpWorkspace(
            id="temp",
            name=input.name,
            color=input.color,
            avatar=input.avatar
        )

    @staticmethod
    def from_update_input(input: "WorkspaceUpdateInput") -> ClickUpWorkspace:
        """
        Map MCP WorkspaceUpdateInput to Workspace domain entity.

        Converts user-facing MCP update input to a domain entity with the
        workspace ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Args:
            input: WorkspaceUpdateInput from MCP tool call containing:
                - workspace_id: Workspace ID to update (required)
                - name: Updated workspace name (optional)
                - color: Updated workspace color (optional)
                - avatar: Updated workspace avatar URL (optional)

        Returns:
            ClickUpWorkspace domain entity with:
                - id: From input.workspace_id
                - name: From input or empty string
                - color: From input
                - avatar: From input
                - Other fields: Default values

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

            mcp_input = WorkspaceUpdateInput(
                workspace_id="9018752317",
                name="Updated Team Name"
            )
            workspace = WorkspaceMapper.from_update_input(mcp_input)
            # workspace.id == "9018752317"
            # workspace.name == "Updated Team Name"
        """
        return ClickUpWorkspace(
            id=input.workspace_id,
            name=input.name or "",
            color=input.color,
            avatar=input.avatar
        )

    @staticmethod
    def to_domain(resp: WorkspaceResp) -> ClickUpWorkspace:
        """
        Map ClickUp API response DTO to Workspace domain entity.

        Converts the ClickUp API response (WorkspaceResp DTO) to a domain entity,
        extracting relevant fields and transforming nested structures. This
        is the primary entry point for API responses.

        Args:
            resp: WorkspaceResp DTO from ClickUp API containing:
                - id: Workspace ID
                - name: Workspace name
                - color: Workspace color
                - avatar: Workspace avatar URL
                - members: List of workspace members
                - settings: Workspace settings

        Returns:
            ClickUpWorkspace domain entity with:
                - id: From resp.id
                - name: From resp.name
                - color: From resp.color
                - avatar: From resp.avatar
                - members: From resp.members
                - settings: From resp.settings

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper
            from clickup_mcp.models.dto.workspace import WorkspaceResp

            api_response = WorkspaceResp(
                id="9018752317",
                name="Engineering Team",
                color="#3498db"
            )
            workspace = WorkspaceMapper.to_domain(api_response)
            # workspace.id == "9018752317"
            # workspace.name == "Engineering Team"
        """
        return ClickUpWorkspace(
            id=resp.id,
            name=resp.name,
            color=resp.color,
            avatar=resp.avatar,
            members=resp.members or [],
            settings=resp.settings
        )

    @staticmethod
    def to_create_dto(workspace: ClickUpWorkspace) -> WorkspaceCreate:
        """
        Map Workspace domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new workspace.

        Args:
            workspace: ClickUpWorkspace domain entity containing workspace data

        Returns:
            WorkspaceCreate DTO with:
                - name: From workspace.name
                - color: From workspace.color
                - avatar: From workspace.avatar

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

            workspace = ClickUpWorkspace(
                id="temp",
                name="Engineering Team",
                color="#3498db"
            )
            create_dto = WorkspaceMapper.to_create_dto(workspace)
            # create_dto.name == "Engineering Team"
            # create_dto.color == "#3498db"

            # Python - Use with API client
            response = await client.team.create(workspace_create=create_dto)
        """
        return WorkspaceCreate(
            name=workspace.name,
            color=workspace.color,
            avatar=workspace.avatar
        )

    @staticmethod
    def to_update_dto(workspace: ClickUpWorkspace) -> WorkspaceUpdate:
        """
        Map Workspace domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing workspace.

        Args:
            workspace: ClickUpWorkspace domain entity with updated data

        Returns:
            WorkspaceUpdate DTO with:
                - name: From workspace.name
                - color: From workspace.color
                - avatar: From workspace.avatar

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

            workspace = ClickUpWorkspace(
                id="9018752317",
                name="Updated Team Name",
                color="#e74c3c"
            )
            update_dto = WorkspaceMapper.to_update_dto(workspace)
            # update_dto.name == "Updated Team Name"
            # update_dto.color == "#e74c3c"

            # Python - Use with API client
            response = await client.team.update(
                team_id="9018752317",
                workspace_update=update_dto
            )
        """
        return WorkspaceUpdate(
            name=workspace.name,
            color=workspace.color,
            avatar=workspace.avatar
        )

    @staticmethod
    def to_workspace_result_output(workspace: ClickUpWorkspace) -> "WorkspaceResult":
        """
        Map Workspace domain entity to MCP WorkspaceResult output.

        Converts a domain entity to the MCP output format for returning
        workspace details to the MCP client. This is used for single workspace
        responses (get, create, update operations).

        Args:
            workspace: ClickUpWorkspace domain entity to convert

        Returns:
            WorkspaceResult MCP output model with:
                - id: From workspace.id
                - name: From workspace.name
                - color: From workspace.color
                - avatar: From workspace.avatar

        Raises:
            ImportError: If WorkspaceResult cannot be imported (should not occur in normal operation)

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

            workspace = ClickUpWorkspace(
                id="9018752317",
                name="Engineering Team",
                color="#3498db"
            )
            mcp_output = WorkspaceMapper.to_workspace_result_output(workspace)
            # mcp_output.id == "9018752317"
            # mcp_output.name == "Engineering Team"
            # mcp_output.color == "#3498db"

            # Python - Return from MCP tool
            return mcp_output
        """
        from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceResult

        return WorkspaceResult(
            id=workspace.id,
            name=workspace.name,
            color=workspace.color,
            avatar=workspace.avatar
        )

    @staticmethod
    def to_workspace_list_item_output(workspace: ClickUpWorkspace) -> "WorkspaceListItem":
        """
        Map Workspace domain entity to MCP WorkspaceListItem output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple workspaces
        in a list (get_all operation).

        Args:
            workspace: ClickUpWorkspace domain entity to convert

        Returns:
            WorkspaceListItem MCP output model with:
                - id: From workspace.id
                - name: From workspace.name

        Raises:
            ImportError: If WorkspaceListItem cannot be imported (should not occur in normal operation)

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.workspace_mapper import WorkspaceMapper

            workspace = ClickUpWorkspace(
                id="9018752317",
                name="Engineering Team"
            )
            list_item = WorkspaceMapper.to_workspace_list_item_output(workspace)
            # list_item.id == "9018752317"
            # list_item.name == "Engineering Team"

            # Python - Return from MCP tool (in a list)
            workspaces = [WorkspaceMapper.to_workspace_list_item_output(w) for w in domain_workspaces]
            return workspaces
        """
        from clickup_mcp.mcp_server.models.outputs.workspace import WorkspaceListItem

        return WorkspaceListItem(id=workspace.id, name=workspace.name)
