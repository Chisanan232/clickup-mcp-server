"""
List DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for List resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic ClickUpList domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_list_result_output, to_list_list_item_output)

Special Handling:
- Nested object extraction: Extracts IDs from folder, space, and assignee objects
- Status transformation: Converts status DTOs to domain ListStatus value objects
- Optional fields: Handles missing/null nested objects gracefully

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.list_mapper import ListMapper

    list_domain = ListMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    list_domain = ListMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = ListMapper.to_create_dto(list_domain)

    # Python - Map domain to MCP output
    mcp_output = ListMapper.to_list_result_output(list_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.list import ClickUpList, ListStatus
from clickup_mcp.models.dto.list import ListCreate, ListResp, ListUpdate

if TYPE_CHECKING:
    from clickup_mcp.mcp_server.models.inputs.list_ import (
        ListCreateInput,
        ListUpdateInput,
    )
    from clickup_mcp.mcp_server.models.outputs.list import ListListItem, ListResult


class ListMapper:
    """
    Static mapper for converting between List DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of List data:

    1. **MCP Input → Domain**: Converts user-facing MCP input models to domain entities
    2. **API Response → Domain**: Converts ClickUp API responses to domain entities
    3. **Domain → API Request**: Converts domain entities to ClickUp API request DTOs
    4. **Domain → MCP Output**: Converts domain entities to user-facing MCP output models

    Key Design Principles:
    - **Separation of Concerns**: Domain logic is isolated from transport details
    - **Unidirectional Flow**: Data flows in one direction through the mapper
    - **Testability**: Each mapping can be tested independently
    - **Maintainability**: Changes to DTOs don't affect domain logic
    - **Nested Object Extraction**: Handles nested objects gracefully

    Attributes:
        None - This is a static utility class with no instance state

    Usage Examples:
        # Python - Create a list from MCP input
        from clickup_mcp.models.mapping.list_mapper import ListMapper

        mcp_input = ListCreateInput(
            name="Q4 Tasks",
            folder_id="folder_123",
            content="Tasks for Q4"
        )
        list_domain = ListMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        list_domain = ListMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = ListMapper.to_create_dto(list_domain)
        response = await client.list.create(folder_id="folder_123", list_create=create_dto)

        # Python - Return to MCP client
        mcp_output = ListMapper.to_list_result_output(list_domain)
    """

    @staticmethod
    def from_create_input(input: "ListCreateInput") -> ClickUpList:
        """
        Map MCP ListCreateInput to List domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the list in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual list is created via API.

        Args:
            input: ListCreateInput from MCP tool call containing:
                - name: List name (required)
                - content: List description (optional)
                - folder_id: Folder ID (optional)
                - status: Status label (optional)
                - priority: Priority level (optional)
                - assignee: User ID to assign (optional)
                - due_date: Due date in epoch ms (optional)
                - due_date_time: Whether due date includes time (optional)

        Returns:
            ClickUpList domain entity with temporary "temp" ID

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            mcp_input = ListCreateInput(
                name="Q4 Tasks",
                folder_id="folder_123",
                content="Tasks for Q4 planning"
            )
            lst = ListMapper.from_create_input(mcp_input)
            # lst.id == "temp"
            # lst.name == "Q4 Tasks"
        """
        return ClickUpList(
            id="temp",
            name=input.name,
            content=input.content,
            folder_id=input.folder_id,
            status=input.status,
            priority=input.priority,
            assignee_id=input.assignee,
            due_date=input.due_date,
            due_date_time=input.due_date_time,
        )

    @staticmethod
    def from_update_input(input: "ListUpdateInput") -> ClickUpList:
        """
        Map MCP ListUpdateInput to List domain entity.

        Converts user-facing MCP update input to a domain entity with the
        list ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Args:
            input: ListUpdateInput from MCP tool call containing:
                - list_id: List ID to update (required)
                - name: Updated list name (optional)
                - content: Updated description (optional)
                - status: Updated status (optional)
                - priority: Updated priority (optional)
                - assignee: Updated assignee (optional)
                - due_date: Updated due date (optional)
                - due_date_time: Whether due date includes time (optional)

        Returns:
            ClickUpList domain entity with list ID and updated fields

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            mcp_input = ListUpdateInput(
                list_id="list_123",
                name="Updated List Name",
                priority=2
            )
            lst = ListMapper.from_update_input(mcp_input)
            # lst.id == "list_123"
            # lst.name == "Updated List Name"
        """
        return ClickUpList(
            id=input.list_id,
            name=input.name or "",
            content=input.content,
            status=input.status,
            priority=input.priority,
            assignee_id=input.assignee,
            due_date=input.due_date,
            due_date_time=input.due_date_time,
        )

    @staticmethod
    def to_domain(resp: ListResp) -> ClickUpList:
        """
        Map ClickUp API response DTO to List domain entity.

        Converts the ClickUp API response (ListResp DTO) to a domain entity,
        extracting relevant fields and transforming nested structures. This
        is the primary entry point for API responses.

        Special handling:
        - Extracts IDs from nested folder, space, and assignee objects
        - Transforms status DTOs to domain ListStatus value objects
        - Handles missing/null nested objects gracefully

        Args:
            resp: ListResp DTO from ClickUp API containing:
                - id: List ID
                - name: List name
                - content: List description
                - folder: Folder object with ID
                - space: Space object with ID
                - assignee: Assignee object with ID
                - status: Status label
                - priority: Priority level
                - due_date: Due date in epoch ms
                - due_date_time: Whether due date includes time
                - statuses: List of status definitions

        Returns:
            ClickUpList domain entity with all fields populated

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            api_response = ListResp(
                id="list_123",
                name="Q4 Tasks",
                folder=FolderObj(id="folder_456"),
                space=SpaceObj(id="space_789"),
                statuses=[StatusObj(name="Open", type="open")]
            )
            lst = ListMapper.to_domain(api_response)
            # lst.id == "list_123"
            # lst.folder_id == "folder_456"
        """
        folder_id = resp.folder.id if resp.folder and resp.folder.id else None
        space_id = resp.space.id if resp.space and resp.space.id else None
        assignee_id = resp.assignee.id if resp.assignee and resp.assignee.id is not None else None
        statuses: list[ListStatus] | None = None
        if resp.statuses:
            statuses = [
                ListStatus(name=s.name, type=s.type, color=s.color, orderindex=s.orderindex) for s in resp.statuses
            ]
        return ClickUpList(
            id=resp.id,
            name=resp.name,
            content=resp.content,
            folder_id=folder_id,
            space_id=space_id,
            status=resp.status,
            priority=resp.priority,
            assignee_id=assignee_id,
            due_date=resp.due_date,
            due_date_time=resp.due_date_time,
            statuses=statuses,
        )

    @staticmethod
    def to_create_dto(lst: ClickUpList) -> ListCreate:
        """
        Map List domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new list.

        Args:
            lst: ClickUpList domain entity containing list data

        Returns:
            ListCreate DTO with list creation fields

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            lst = ClickUpList(
                id="temp",
                name="Q4 Tasks",
                folder_id="folder_123",
                priority=2
            )
            create_dto = ListMapper.to_create_dto(lst)
            # create_dto.name == "Q4 Tasks"
        """
        return ListCreate(
            name=lst.name,
            content=lst.content,
            due_date=lst.due_date,
            due_date_time=lst.due_date_time,
            priority=lst.priority,
            assignee=lst.assignee_id if isinstance(lst.assignee_id, int) else None,
            status=lst.status,
        )

    @staticmethod
    def to_update_dto(lst: ClickUpList) -> ListUpdate:
        """
        Map List domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing list.

        Args:
            lst: ClickUpList domain entity with updated data

        Returns:
            ListUpdate DTO with list update fields

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            lst = ClickUpList(
                id="list_123",
                name="Updated List Name",
                priority=1
            )
            update_dto = ListMapper.to_update_dto(lst)
            # update_dto.name == "Updated List Name"
        """
        return ListUpdate(
            name=lst.name,
            content=lst.content,
            due_date=lst.due_date,
            due_date_time=lst.due_date_time,
            priority=lst.priority,
            assignee=lst.assignee_id if isinstance(lst.assignee_id, int) else None,
            status=lst.status,
        )

    @staticmethod
    def to_list_result_output(lst: ClickUpList) -> "ListResult":
        """
        Map List domain entity to MCP ListResult output.

        Converts a domain entity to the MCP output format for returning
        list details to the MCP client. This is used for single list
        responses (get, create, update operations).

        Args:
            lst: ClickUpList domain entity to convert

        Returns:
            ListResult MCP output model with list details and statuses

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            lst = ClickUpList(
                id="list_123",
                name="Q4 Tasks",
                folder_id="folder_456",
                statuses=[ListStatus(name="Open", type="open")]
            )
            mcp_output = ListMapper.to_list_result_output(lst)
            # mcp_output.id == "list_123"
            # mcp_output.name == "Q4 Tasks"
        """
        from clickup_mcp.mcp_server.models.outputs.list import (
            ListResult,
            ListStatusOutput,
        )

        out = ListResult(
            id=lst.id,
            name=lst.name,
            status=lst.status,
            folder_id=lst.folder_id,
            space_id=lst.space_id,
        )
        if lst.statuses:
            out.statuses = [
                ListStatusOutput(
                    name=s.name,
                    type=s.type,
                    color=s.color,
                    orderindex=s.orderindex,
                )
                for s in lst.statuses
            ]
        return out

    @staticmethod
    def to_list_list_item_output(lst: ClickUpList) -> "ListListItem":
        """
        Map List domain entity to MCP ListListItem output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple lists
        in a list (get_all operation).

        Args:
            lst: ClickUpList domain entity to convert

        Returns:
            ListListItem MCP output model with id and name

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.list_mapper import ListMapper

            lst = ClickUpList(
                id="list_123",
                name="Q4 Tasks",
                folder_id="folder_456"
            )
            list_item = ListMapper.to_list_list_item_output(lst)
            # list_item.id == "list_123"
            # list_item.name == "Q4 Tasks"
        """
        from clickup_mcp.mcp_server.models.outputs.list import ListListItem

        return ListListItem(id=lst.id, name=lst.name)
