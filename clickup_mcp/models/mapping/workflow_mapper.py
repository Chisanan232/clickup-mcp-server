"""
Workflow DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Workflow resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic Workflow domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_workflow_result_output, to_workflow_list_item_output)

Special Handling:
- Trigger config normalization: Converts between different trigger configurations
- Actions normalization: Handles action list transformations
- Nested objects: Extracts IDs from nested objects

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.workflow_mapper import WorkflowMapper

    workflow_domain = WorkflowMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    workflow_domain = WorkflowMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = WorkflowMapper.to_create_dto(workflow_domain)

    # Python - Map domain to MCP output
    mcp_output = WorkflowMapper.to_workflow_result_output(workflow_domain)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from clickup_mcp.models.domain.workflow import Workflow
from clickup_mcp.models.dto.workflow import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.workflow import (
        WorkflowCreateInput,
        WorkflowUpdateInput,
    )

logger = logging.getLogger(__name__)


class WorkflowMapper:
    """
    Static mapper for converting between Workflow DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Workflow data:

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
        # Python - Create a workflow from MCP input
        from clickup_mcp.models.mapping.workflow_mapper import WorkflowMapper
        from clickup_mcp.mcp_server.models.inputs.workflow import WorkflowCreateInput

        mcp_input = WorkflowCreateInput(
            team_id="team_123",
            name="Auto-assign on create",
            trigger_type="task_created",
            trigger_config={"list_id": "456"},
            actions=[{"type": "assign", "user_id": "789"}]
        )
        workflow_domain = WorkflowMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        workflow_domain = WorkflowMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = WorkflowMapper.to_create_dto(workflow_domain)
    """

    @staticmethod
    def from_create_input(mcp_input: "WorkflowCreateInput") -> Workflow:
        """
        Convert MCP input model to Workflow domain entity.

        Args:
            mcp_input: MCP input model from workflow creation request

        Returns:
            Workflow: Domain entity with business logic

        Examples:
            WorkflowMapper.from_create_input(
                WorkflowCreateInput(team_id="team_123", name="Auto-assign", ...)
            )
        """
        return Workflow(
            id="temp",  # Temporary ID, will be replaced by API response
            team_id=mcp_input.team_id,
            name=mcp_input.name,
            description=mcp_input.description,
            trigger_type=mcp_input.trigger_type,
            trigger_config=mcp_input.trigger_config or {},
            actions=mcp_input.actions,
            is_active=mcp_input.is_active,
            priority=mcp_input.priority,
        )

    @staticmethod
    def from_update_input(mcp_input: "WorkflowUpdateInput") -> Workflow:
        """
        Convert MCP input model to Workflow domain entity for updates.

        Args:
            mcp_input: MCP input model from workflow update request

        Returns:
            Workflow: Domain entity with business logic

        Examples:
            WorkflowMapper.from_update_input(
                WorkflowUpdateInput(workflow_id="wf_123", name="Updated name", ...)
            )
        """
        return Workflow(
            id=mcp_input.workflow_id,
            team_id="temp",  # Not used in update
            name=mcp_input.name or "",
            description=mcp_input.description,
            trigger_type=mcp_input.trigger_type or "",
            trigger_config=mcp_input.trigger_config or {},
            actions=mcp_input.actions or [],
            is_active=mcp_input.is_active if mcp_input.is_active is not None else True,
            priority=mcp_input.priority,
        )

    @staticmethod
    def to_domain(response: WorkflowResponse) -> Workflow:
        """
        Convert API response DTO to Workflow domain entity.

        Args:
            response: API response DTO from ClickUp

        Returns:
            Workflow: Domain entity with business logic

        Examples:
            WorkflowMapper.to_domain(WorkflowResponse.deserialize(api_data))
        """
        return Workflow(
            id=response.id,
            team_id=response.team_id,
            name=response.name,
            description=response.description,
            trigger_type=response.trigger_type,
            trigger_config=response.trigger_config,
            actions=response.actions,
            is_active=response.is_active,
            priority=response.priority,
            date_created=response.date_created,
            date_updated=response.date_updated,
        )

    @staticmethod
    def to_create_dto(domain: Workflow) -> WorkflowCreate:
        """
        Convert Workflow domain entity to API create request DTO.

        Args:
            domain: Workflow domain entity

        Returns:
            WorkflowCreate: API request DTO for creating workflow

        Examples:
            WorkflowMapper.to_create_dto(workflow_domain)
        """
        return WorkflowCreate(
            name=domain.name,
            description=domain.description,
            trigger_type=domain.trigger_type,
            trigger_config=domain.trigger_config,
            actions=domain.actions,
            is_active=domain.is_active,
            priority=domain.priority,
        )

    @staticmethod
    def to_update_dto(domain: Workflow) -> WorkflowUpdate:
        """
        Convert Workflow domain entity to API update request DTO.

        Args:
            domain: Workflow domain entity

        Returns:
            WorkflowUpdate: API request DTO for updating workflow

        Examples:
            WorkflowMapper.to_update_dto(workflow_domain)
        """
        return WorkflowUpdate(
            name=domain.name if domain.name else None,
            description=domain.description,
            trigger_type=domain.trigger_type if domain.trigger_type else None,
            trigger_config=domain.trigger_config if domain.trigger_config else None,
            actions=domain.actions if domain.actions else None,
            is_active=domain.is_active,
            priority=domain.priority,
        )

    @staticmethod
    def to_workflow_result_output(domain: Workflow) -> dict[str, object]:
        """
        Convert Workflow domain entity to MCP result output format.

        Args:
            domain: Workflow domain entity

        Returns:
            dict[str, object]: MCP output format for workflow result

        Examples:
            WorkflowMapper.to_workflow_result_output(workflow_domain)
        """
        return {
            "id": domain.workflow_id,
            "team_id": domain.team_id,
            "name": domain.name,
            "description": domain.description,
            "trigger_type": domain.trigger_type,
            "trigger_config": domain.trigger_config,
            "actions": domain.actions,
            "is_active": domain.is_active,
            "priority": domain.priority,
            "date_created": domain.date_created,
            "date_updated": domain.date_updated,
        }

    @staticmethod
    def to_workflow_list_item_output(domain: Workflow) -> dict[str, object]:
        """
        Convert Workflow domain entity to MCP list item output format.

        Args:
            domain: Workflow domain entity

        Returns:
            dict[str, object]: MCP output format for workflow list item

        Examples:
            WorkflowMapper.to_workflow_list_item_output(workflow_domain)
        """
        return {
            "id": domain.workflow_id,
            "team_id": domain.team_id,
            "name": domain.name,
            "trigger_type": domain.trigger_type,
            "is_active": domain.is_active,
            "priority": domain.priority,
        }
