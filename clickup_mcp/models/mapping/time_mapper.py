"""
Time Entry DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Time Entry resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic TimeEntry domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_time_entry_result_output, to_time_entry_list_item_output)

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.time_mapper import TimeMapper

    time_domain = TimeMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    time_domain = TimeMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = TimeMapper.to_create_dto(time_domain)

    # Python - Map domain to MCP output
    mcp_output = TimeMapper.to_time_entry_result_output(time_domain)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from clickup_mcp.models.domain.time import TimeEntry
from clickup_mcp.models.dto.time import (
    TimeEntryCreate,
    TimeEntryResponse,
    TimeEntryUpdate,
)

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.time import (
        TimeEntryCreateInput,
        TimeEntryUpdateInput,
    )


class TimeMapper:
    """
    Static mapper for converting between Time Entry DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Time Entry data:

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
        # Python - Create a time entry from MCP input
        from clickup_mcp.models.mapping.time_mapper import TimeMapper

        mcp_input = TimeEntryCreateInput(
            task_id="task_123",
            description="Implementation work",
            duration=3600000
        )
        time_domain = TimeMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        time_domain = TimeMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = TimeMapper.to_create_dto(time_domain)

        # Python - Return to MCP client
        mcp_output = TimeMapper.to_time_entry_result_output(time_domain)
    """

    @staticmethod
    def from_create_input(input: "TimeEntryCreateInput") -> TimeEntry:
        """
        Map MCP TimeEntryCreateInput to TimeEntry domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the time entry in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual time entry is created via API.

        Args:
            input: TimeEntryCreateInput from MCP tool call containing:
                - task_id: Task ID to log time against (required)
                - description: Description of the time entry (optional)
                - start: Start time in epoch ms (optional)
                - end: End time in epoch ms (optional)
                - duration: Duration in milliseconds (optional)

        Returns:
            TimeEntry domain entity with:
                - entry_id: Temporary placeholder "temp" (will be replaced after API creation)
                - task_id: From input.task_id
                - user_id: Placeholder "temp" (will be replaced after API creation)
                - team_id: Placeholder "temp" (will be replaced after API creation)
                - description: From input.description
                - start: From input.start
                - end: From input.end
                - duration: From input.duration
                - billable: False (default)

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.time_mapper import TimeMapper

            mcp_input = TimeEntryCreateInput(
                task_id="task_123",
                description="Implementation work",
                duration=3600000
            )
            time_entry = TimeMapper.from_create_input(mcp_input)
            # time_entry.entry_id == "temp"
            # time_entry.task_id == "task_123"
            # time_entry.duration == 3600000
        """
        return TimeEntry(
            id="temp",
            task_id=input.task_id,
            user_id="temp",
            team_id="temp",
            description=input.description,
            start=input.start,
            end=input.end,
            duration=input.duration,
            billable=False,
        )

    @staticmethod
    def from_update_input(input: "TimeEntryUpdateInput") -> TimeEntry:
        """
        Map MCP TimeEntryUpdateInput to TimeEntry domain entity.

        Converts user-facing MCP update input to a domain entity with the
        time entry ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Args:
            input: TimeEntryUpdateInput from MCP tool call containing:
                - time_entry_id: Time entry ID to update (required)
                - description: Updated description (optional)
                - start: Updated start time in epoch ms (optional)
                - end: Updated end time in epoch ms (optional)
                - duration: Updated duration in milliseconds (optional)

        Returns:
            TimeEntry domain entity with:
                - entry_id: From input.time_entry_id
                - task_id: Placeholder "temp" (not needed for update)
                - user_id: Placeholder "temp" (not needed for update)
                - team_id: Placeholder "temp" (not needed for update)
                - description: From input.description
                - start: From input.start
                - end: From input.end
                - duration: From input.duration
                - billable: False (default)

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.time_mapper import TimeMapper

            mcp_input = TimeEntryUpdateInput(
                time_entry_id="entry_123",
                duration=7200000
            )
            time_entry = TimeMapper.from_update_input(mcp_input)
            # time_entry.entry_id == "entry_123"
            # time_entry.duration == 7200000
        """
        return TimeEntry(
            id=input.time_entry_id,
            task_id="temp",
            user_id="temp",
            team_id="temp",
            description=input.description,
            start=input.start,
            end=input.end,
            duration=input.duration,
            billable=False,
        )

    @staticmethod
    def to_domain(resp: TimeEntryResponse) -> TimeEntry:
        """
        Map ClickUp API response DTO to TimeEntry domain entity.

        Converts the ClickUp API response (TimeEntryResponse DTO) to a domain entity,
        extracting relevant fields. This is the primary entry point for API responses.

        Args:
            resp: TimeEntryResponse DTO from ClickUp API containing:
                - id: Time entry ID
                - task_id: Task ID this time entry belongs to
                - user_id: User ID who logged the time
                - team_id: Team/workspace ID
                - description: Description of the work done
                - start: Start time in epoch milliseconds
                - end: End time in epoch milliseconds
                - duration: Duration in milliseconds
                - billable: Whether the time entry is billable

        Returns:
            TimeEntry domain entity with:
                - entry_id: From resp.id
                - task_id: From resp.task_id
                - user_id: From resp.user_id
                - team_id: From resp.team_id
                - description: From resp.description
                - start: From resp.start
                - end: From resp.end
                - duration: From resp.duration
                - billable: From resp.billable

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.time_mapper import TimeMapper
            from clickup_mcp.models.dto.time import TimeEntryResponse

            api_response = TimeEntryResponse(
                id="entry_123",
                task_id="task_456",
                user_id=789,
                team_id="team_001",
                description="Implementation work",
                duration=3600000
            )
            time_entry = TimeMapper.to_domain(api_response)
            # time_entry.entry_id == "entry_123"
            # time_entry.task_id == "task_456"
            # time_entry.duration == 3600000
        """
        return TimeEntry(
            id=resp.id,
            task_id=resp.task_id,
            user_id=str(resp.user_id),
            team_id=resp.team_id,
            description=resp.description,
            start=resp.start,
            end=resp.end,
            duration=resp.duration,
            billable=resp.billable,
        )

    @staticmethod
    def to_create_dto(time_entry: TimeEntry) -> TimeEntryCreate:
        """
        Map TimeEntry domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new time entry.

        Args:
            time_entry: TimeEntry domain entity containing time entry data

        Returns:
            TimeEntryCreate DTO with:
                - task_id: From time_entry.task_id
                - description: From time_entry.description
                - start: From time_entry.start
                - end: From time_entry.end
                - duration: From time_entry.duration
                - billable: From time_entry.billable

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.time_mapper import TimeMapper

            time_entry = TimeEntry(
                id="temp",
                task_id="task_456",
                user_id="user_789",
                team_id="team_001",
                description="Implementation work",
                duration=3600000
            )
            create_dto = TimeMapper.to_create_dto(time_entry)
            # create_dto.task_id == "task_456"
            # create_dto.duration == 3600000

            # Python - Use with API client
            response = await client.time_entry.create(
                team_id="team_001",
                time_entry_create=create_dto
            )
        """
        return TimeEntryCreate(
            task_id=time_entry.task_id,
            description=time_entry.description,
            start=time_entry.start,
            end=time_entry.end,
            duration=time_entry.duration,
            billable=time_entry.billable,
        )

    @staticmethod
    def to_update_dto(time_entry: TimeEntry) -> TimeEntryUpdate:
        """
        Map TimeEntry domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing time entry.

        Args:
            time_entry: TimeEntry domain entity with updated data

        Returns:
            TimeEntryUpdate DTO with:
                - description: From time_entry.description
                - start: From time_entry.start
                - end: From time_entry.end
                - duration: From time_entry.duration
                - billable: From time_entry.billable

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.time_mapper import TimeMapper

            time_entry = TimeEntry(
                id="entry_123",
                task_id="task_456",
                user_id="user_789",
                team_id="team_001",
                duration=7200000
            )
            update_dto = TimeMapper.to_update_dto(time_entry)
            # update_dto.duration == 7200000

            # Python - Use with API client
            response = await client.time_entry.update(
                team_id="team_001",
                time_entry_id="entry_123",
                time_entry_update=update_dto
            )
        """
        return TimeEntryUpdate(
            description=time_entry.description,
            start=time_entry.start,
            end=time_entry.end,
            duration=time_entry.duration,
            billable=time_entry.billable,
        )

    @staticmethod
    def to_time_entry_result_output(time_entry: TimeEntry) -> dict:
        """
        Map TimeEntry domain entity to MCP time entry result output.

        Converts a domain entity to the MCP output format for returning
        time entry details to the MCP client. This is used for single time entry
        responses (get, create, update operations).

        Args:
            time_entry: TimeEntry domain entity to convert

        Returns:
            Dictionary with time entry data:
                - id: From time_entry.entry_id
                - task_id: From time_entry.task_id
                - user_id: From time_entry.user_id
                - team_id: From time_entry.team_id
                - description: From time_entry.description
                - start: From time_entry.start
                - end: From time_entry.end
                - duration: From time_entry.duration
                - billable: From time_entry.billable

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.time_mapper import TimeMapper

            time_entry = TimeEntry(
                id="entry_123",
                task_id="task_456",
                user_id="user_789",
                team_id="team_001",
                description="Implementation work",
                duration=3600000
            )
            mcp_output = TimeMapper.to_time_entry_result_output(time_entry)
            # mcp_output["id"] == "entry_123"
            # mcp_output["task_id"] == "task_456"

            # Python - Return from MCP tool
            return mcp_output
        """
        return {
            "id": time_entry.entry_id,
            "task_id": time_entry.task_id,
            "user_id": time_entry.user_id,
            "team_id": time_entry.team_id,
            "description": time_entry.description,
            "start": time_entry.start,
            "end": time_entry.end,
            "duration": time_entry.duration,
            "billable": time_entry.billable,
        }

    @staticmethod
    def to_time_entry_list_item_output(time_entry: TimeEntry) -> dict:
        """
        Map TimeEntry domain entity to MCP time entry list item output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple time entries
        in a list.

        Args:
            time_entry: TimeEntry domain entity to convert

        Returns:
            Dictionary with time entry list item data:
                - id: From time_entry.entry_id
                - task_id: From time_entry.task_id
                - description: From time_entry.description
                - duration: From time_entry.duration

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.time_mapper import TimeMapper

            time_entry = TimeEntry(
                id="entry_123",
                task_id="task_456",
                user_id="user_789",
                team_id="team_001",
                description="Implementation work",
                duration=3600000
            )
            list_item = TimeMapper.to_time_entry_list_item_output(time_entry)
            # list_item["id"] == "entry_123"
            # list_item["task_id"] == "task_456"

            # Python - Return from MCP tool (in a list)
            entries = [TimeMapper.to_time_entry_list_item_output(t) for t in domain_entries]
            return entries
        """
        return {
            "id": time_entry.entry_id,
            "task_id": time_entry.task_id,
            "description": time_entry.description,
            "duration": time_entry.duration,
        }
