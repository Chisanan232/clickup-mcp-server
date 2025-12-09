"""
Task DTO ↔ Domain mappers.

This module implements the Anti-Corruption Layer (ACL) pattern for Task resources,
translating between transport DTOs (Data Transfer Objects) from the ClickUp API
and the vendor-agnostic ClickUpTask domain entity.

The mapper follows a unidirectional flow:
1. MCP Input → Domain Entity (from_create_input, from_update_input)
2. API Response DTO → Domain Entity (to_domain)
3. Domain Entity → API Request DTO (to_create_dto, to_update_dto)
4. Domain Entity → MCP Output (to_task_result_output, to_task_list_item_output)

Special Handling:
- Priority normalization: Converts between different priority representations
- Custom fields: Extracted from API response and stored as neutral {id, value} dicts
- Nested objects: Extracts IDs from nested objects (status, assignees, folder, list, space)
- Error handling: Logs priority mapping failures without breaking the mapping

Usage Examples:
    # Python - Map MCP input to domain
    from clickup_mcp.models.mapping.task_mapper import TaskMapper

    task_domain = TaskMapper.from_create_input(mcp_input)

    # Python - Map API response to domain
    task_domain = TaskMapper.to_domain(api_response_dto)

    # Python - Map domain to API request
    create_dto = TaskMapper.to_create_dto(task_domain)

    # Python - Map domain to MCP output
    mcp_output = TaskMapper.to_task_result_output(task_domain)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from clickup_mcp.models.domain.task import ClickUpTask
from clickup_mcp.models.dto.task import TaskCreate, TaskResp, TaskUpdate
from clickup_mcp.models.mapping.priority import (
    normalize_priority_input,
    parse_priority_obj,
)

if TYPE_CHECKING:  # type hints only; avoid importing mcp_server package at runtime
    from clickup_mcp.mcp_server.models.inputs.task import TaskCreateInput, TaskUpdateInput
    from clickup_mcp.mcp_server.models.outputs.task import TaskListItem, TaskResult

from clickup_mcp.models.domain.task_priority import (
    domain_priority_label,
    int_to_domain_priority,
)

logger = logging.getLogger(__name__)


class TaskMapper:
    """
    Static mapper for converting between Task DTOs and domain entity.

    This class implements the Anti-Corruption Layer (ACL) pattern, providing
    unidirectional mappings between different representations of Task data:

    1. **MCP Input → Domain**: Converts user-facing MCP input models to domain entities
    2. **API Response → Domain**: Converts ClickUp API responses to domain entities
    3. **Domain → API Request**: Converts domain entities to ClickUp API request DTOs
    4. **Domain → MCP Output**: Converts domain entities to user-facing MCP output models

    Key Design Principles:
    - **Separation of Concerns**: Domain logic is isolated from transport details
    - **Unidirectional Flow**: Data flows in one direction through the mapper
    - **Testability**: Each mapping can be tested independently
    - **Maintainability**: Changes to DTOs don't affect domain logic
    - **Priority Normalization**: Handles different priority representations
    - **Error Resilience**: Logs errors without breaking the mapping process

    Attributes:
        None - This is a static utility class with no instance state

    Usage Examples:
        # Python - Create a task from MCP input
        from clickup_mcp.models.mapping.task_mapper import TaskMapper
        from clickup_mcp.mcp_server.models.inputs.task import TaskCreateInput

        mcp_input = TaskCreateInput(
            name="Implement feature",
            status="Open",
            priority="high",
            assignees=["user_123"]
        )
        task_domain = TaskMapper.from_create_input(mcp_input)

        # Python - Convert API response to domain
        task_domain = TaskMapper.to_domain(api_response_dto)

        # Python - Prepare for API request
        create_dto = TaskMapper.to_create_dto(task_domain)
        response = await client.task.create(list_id="list_456", task_create=create_dto)

        # Python - Return to MCP client
        mcp_output = TaskMapper.to_task_result_output(task_domain, url="https://...")
    """

    @staticmethod
    def from_create_input(input: "TaskCreateInput") -> ClickUpTask:
        """
        Map MCP TaskCreateInput to Task domain entity.

        Converts user-facing MCP input (from tool calls) to a domain entity
        that represents the task in a vendor-agnostic way. The temporary ID
        is used as a placeholder until the actual task is created via API.

        Priority normalization is applied to convert from MCP priority format
        to the domain's integer priority (1-4).

        Args:
            input: TaskCreateInput from MCP tool call containing:
                - name: Task name (required)
                - status: Task status (optional)
                - priority: Priority in MCP format (optional, normalized)
                - assignees: List of user IDs (optional)
                - due_date: Due date in epoch ms (optional)
                - time_estimate: Time estimate in ms (optional)
                - parent: Parent task ID for subtasks (optional)

        Returns:
            ClickUpTask domain entity with:
                - id: Temporary placeholder "temp" (will be replaced after API creation)
                - name: From input
                - status: From input
                - priority: Normalized from input
                - assignee_ids: From input
                - due_date: From input
                - time_estimate: From input
                - parent_id: From input

        Usage Examples:
            # Python - Map MCP input to domain
            from clickup_mcp.models.mapping.task_mapper import TaskMapper

            mcp_input = TaskCreateInput(
                name="Implement authentication",
                status="Open",
                priority="high",
                assignees=["user_123"],
                due_date=1702080000000
            )
            task = TaskMapper.from_create_input(mcp_input)
            # task.id == "temp"
            # task.name == "Implement authentication"
            # task.priority == 1 (normalized from "high")
        """
        return ClickUpTask(
            id="temp",
            name=input.name,
            status=input.status,
            priority=normalize_priority_input(input.priority),
            assignee_ids=list(input.assignees),
            due_date=input.due_date,
            time_estimate=input.time_estimate,
            parent_id=input.parent,
        )

    @staticmethod
    def from_update_input(input: "TaskUpdateInput") -> ClickUpTask:
        """
        Map MCP TaskUpdateInput to Task domain entity.

        Converts user-facing MCP update input to a domain entity with the
        task ID and updated properties. Handles optional fields by providing
        sensible defaults.

        Priority normalization is applied to convert from MCP priority format
        to the domain's integer priority (1-4).

        Args:
            input: TaskUpdateInput from MCP tool call containing:
                - task_id: Task ID to update (required)
                - name: Updated task name (optional)
                - status: Updated status (optional)
                - priority: Updated priority in MCP format (optional, normalized)
                - assignees: Updated list of user IDs (optional)
                - due_date: Updated due date in epoch ms (optional)
                - time_estimate: Updated time estimate in ms (optional)

        Returns:
            ClickUpTask domain entity with:
                - id: From input.task_id
                - name: From input or empty string
                - status: From input
                - priority: Normalized from input
                - assignee_ids: From input or empty list
                - due_date: From input
                - time_estimate: From input

        Usage Examples:
            # Python - Map MCP update input to domain
            from clickup_mcp.models.mapping.task_mapper import TaskMapper

            mcp_input = TaskUpdateInput(
                task_id="task_123",
                name="Updated task name",
                status="In Progress",
                priority="urgent"
            )
            task = TaskMapper.from_update_input(mcp_input)
            # task.id == "task_123"
            # task.name == "Updated task name"
            # task.priority == 1 (normalized from "urgent")
        """
        return ClickUpTask(
            id=input.task_id,
            name=input.name or "",
            status=input.status,
            priority=normalize_priority_input(input.priority),
            assignee_ids=list(input.assignees) if input.assignees is not None else [],
            due_date=input.due_date,
            time_estimate=input.time_estimate,
        )

    @staticmethod
    def to_domain(resp: TaskResp) -> ClickUpTask:
        """
        Map ClickUp API response DTO to Task domain entity.

        Converts the ClickUp API response (TaskResp DTO) to a domain entity,
        extracting relevant fields and transforming nested structures. This
        is the primary entry point for API responses.

        Special handling:
        - Extracts status label from nested status object
        - Parses priority from priority object
        - Extracts IDs from nested objects (assignees, folder, list, space)
        - Transforms custom fields to neutral {id, value} format
        - Handles missing/null nested objects gracefully

        Args:
            resp: TaskResp DTO from ClickUp API containing:
                - id: Task ID
                - name: Task name
                - status: Status object with status label
                - priority: Priority object
                - assignees: List of assignee objects
                - folder: Folder object with ID
                - list: List object with ID
                - space: Space object with ID
                - parent: Parent task ID
                - due_date: Due date in epoch ms
                - time_estimate: Time estimate in ms
                - custom_fields: List of custom field objects

        Returns:
            ClickUpTask domain entity with:
                - id: From resp.id
                - name: From resp.name
                - status: Extracted from resp.status.status
                - priority: Parsed from resp.priority
                - list_id: Extracted from resp.list.id
                - folder_id: Extracted from resp.folder.id
                - space_id: Extracted from resp.space.id
                - parent_id: From resp.parent
                - assignee_ids: Extracted from resp.assignees[].id
                - due_date: From resp.due_date
                - time_estimate: From resp.time_estimate
                - custom_fields: Transformed to {id, value} format

        Usage Examples:
            # Python - Convert API response to domain
            from clickup_mcp.models.mapping.task_mapper import TaskMapper
            from clickup_mcp.models.dto.task import TaskResp

            api_response = TaskResp(
                id="task_123",
                name="Implement feature",
                status=StatusObj(status="In Progress"),
                priority=PriorityObj(priority=1),
                list=ListObj(id="list_456"),
                assignees=[UserObj(id="user_789")]
            )
            task = TaskMapper.to_domain(api_response)
            # task.id == "task_123"
            # task.name == "Implement feature"
            # task.list_id == "list_456"
        """
        status_label: str | None = None
        if resp.status and resp.status.status:
            status_label = resp.status.status

        prio_int: int | None = None
        if resp.priority is not None:
            prio_int = parse_priority_obj(resp.priority)

        # Direct property access for clarity; DTOs provide defaults
        assignees = [u.id for u in resp.assignees if u.id is not None]
        folder_id = resp.folder.id if resp.folder and resp.folder.id else None
        list_id = resp.list.id if resp.list and resp.list.id else None
        space_id = resp.space.id if resp.space and resp.space.id else None

        cf = [{"id": c.id, "value": c.value} for c in resp.custom_fields if c.id is not None]

        return ClickUpTask(
            id=resp.id,
            name=resp.name,
            status=status_label,
            priority=prio_int,
            list_id=list_id,
            folder_id=folder_id,
            space_id=space_id,
            parent_id=resp.parent,
            assignee_ids=assignees,
            due_date=resp.due_date,
            time_estimate=resp.time_estimate,
            custom_fields=cf,
        )

    @staticmethod
    def to_create_dto(task: ClickUpTask) -> TaskCreate:
        """
        Map Task domain entity to ClickUp API create request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for creating a new task. Includes all relevant fields including custom fields.

        Args:
            task: ClickUpTask domain entity containing task data

        Returns:
            TaskCreate DTO with:
                - name: From task.name
                - status: From task.status
                - priority: From task.priority
                - assignees: From task.assignee_ids
                - due_date: From task.due_date
                - time_estimate: From task.time_estimate
                - parent: From task.parent_id
                - custom_fields: From task.custom_fields (list of {id, value})

        Usage Examples:
            # Python - Prepare domain for API creation
            from clickup_mcp.models.mapping.task_mapper import TaskMapper

            task = ClickUpTask(
                id="temp",
                name="Implement feature",
                status="Open",
                priority=2,
                assignee_ids=["user_123"],
                due_date=1702080000000
            )
            create_dto = TaskMapper.to_create_dto(task)
            # create_dto.name == "Implement feature"
            # create_dto.priority == 2

            # Python - Use with API client
            response = await client.task.create(
                list_id="list_456",
                task_create=create_dto
            )
        """
        return TaskCreate(
            name=task.name,
            status=task.status,
            priority=task.priority,
            assignees=list(task.assignee_ids),
            due_date=task.due_date,
            time_estimate=task.time_estimate,
            parent=task.parent_id,
            custom_fields=list(task.custom_fields),  # list of {id,value}
        )

    @staticmethod
    def to_update_dto(task: ClickUpTask) -> TaskUpdate:
        """
        Map Task domain entity to ClickUp API update request DTO.

        Converts a domain entity to the DTO format expected by the ClickUp API
        for updating an existing task. Note that custom fields are not included
        in updates per the ClickUp API specification.

        Args:
            task: ClickUpTask domain entity with updated data

        Returns:
            TaskUpdate DTO with:
                - name: From task.name
                - status: From task.status
                - priority: From task.priority
                - assignees: From task.assignee_ids or None if empty
                - due_date: From task.due_date
                - time_estimate: From task.time_estimate

        Note:
            Custom fields are not included in TaskUpdate per ClickUp API specification.
            Parent task ID is not updatable after creation.

        Usage Examples:
            # Python - Prepare domain for API update
            from clickup_mcp.models.mapping.task_mapper import TaskMapper

            task = ClickUpTask(
                id="task_123",
                name="Updated task name",
                status="In Progress",
                priority=1,
                assignee_ids=["user_123", "user_456"]
            )
            update_dto = TaskMapper.to_update_dto(task)
            # update_dto.name == "Updated task name"
            # update_dto.priority == 1

            # Python - Use with API client
            response = await client.task.update(
                task_id="task_123",
                task_update=update_dto
            )
        """
        return TaskUpdate(
            name=task.name,
            status=task.status,
            priority=task.priority,
            assignees=list(task.assignee_ids) or None,
            due_date=task.due_date,
            time_estimate=task.time_estimate,
        )

    @staticmethod
    def to_task_result_output(task: ClickUpTask, url: str | None = None) -> "TaskResult":
        """
        Map Task domain entity to MCP TaskResult output.

        Converts a domain entity to the MCP output format for returning
        task details to the MCP client. This is used for single task
        responses (get, create, update operations).

        Special handling:
        - Converts priority integer to priority payload with label
        - Handles priority mapping errors gracefully with logging
        - Includes optional URL for task access

        Args:
            task: ClickUpTask domain entity to convert
            url: Optional URL to the task (e.g., ClickUp task URL)

        Returns:
            TaskResult MCP output model with:
                - id: From task.id
                - name: From task.name
                - status: From task.status
                - priority: Priority payload with value and label (or None)
                - list_id: From task.list_id
                - assignee_ids: From task.assignee_ids
                - due_date_ms: From task.due_date
                - url: From url parameter
                - parent_id: From task.parent_id

        Raises:
            ImportError: If TaskResult cannot be imported (should not occur in normal operation)

        Usage Examples:
            # Python - Convert domain to MCP output
            from clickup_mcp.models.mapping.task_mapper import TaskMapper

            task = ClickUpTask(
                id="task_123",
                name="Implement feature",
                status="In Progress",
                priority=2,
                list_id="list_456",
                assignee_ids=["user_789"]
            )
            mcp_output = TaskMapper.to_task_result_output(
                task,
                url="https://app.clickup.com/t/task_123"
            )
            # mcp_output.id == "task_123"
            # mcp_output.name == "Implement feature"
            # mcp_output.priority == {"value": 2, "label": "High"}

            # Python - Return from MCP tool
            return mcp_output
        """
        from clickup_mcp.mcp_server.models.outputs.task import TaskResult

        prio_payload = None
        if task.priority is not None:
            try:
                d = int_to_domain_priority(task.priority)
                prio_payload = {"value": task.priority, "label": domain_priority_label(d)}
            except Exception as e:
                logger.error(
                    "Failed to map priority to domain label",
                    extra={
                        "task_id": getattr(task, "id", None),
                        "priority": task.priority,
                        "error": str(e),
                    },
                )
                prio_payload = None

        return TaskResult(
            id=task.id,
            name=task.name,
            status=task.status,
            priority=prio_payload,
            list_id=task.list_id,
            assignee_ids=list(task.assignee_ids),
            due_date_ms=task.due_date,
            url=url,
            parent_id=task.parent_id,
        )

    @staticmethod
    def to_task_list_item_output(task: ClickUpTask, url: str | None = None) -> "TaskListItem":
        """
        Map Task domain entity to MCP TaskListItem output.

        Converts a domain entity to the MCP output format for list responses.
        This is a lightweight representation used when returning multiple tasks
        in a list (get_all operation).

        Args:
            task: ClickUpTask domain entity to convert
            url: Optional URL to the task (e.g., ClickUp task URL)

        Returns:
            TaskListItem MCP output model with:
                - id: From task.id
                - name: From task.name
                - status: From task.status
                - list_id: From task.list_id
                - url: From url parameter

        Raises:
            ImportError: If TaskListItem cannot be imported (should not occur in normal operation)

        Usage Examples:
            # Python - Convert domain to MCP list item
            from clickup_mcp.models.mapping.task_mapper import TaskMapper

            task = ClickUpTask(
                id="task_123",
                name="Implement feature",
                status="In Progress",
                list_id="list_456"
            )
            list_item = TaskMapper.to_task_list_item_output(
                task,
                url="https://app.clickup.com/t/task_123"
            )
            # list_item.id == "task_123"
            # list_item.name == "Implement feature"

            # Python - Return from MCP tool (in a list)
            tasks = [TaskMapper.to_task_list_item_output(t) for t in domain_tasks]
            return tasks
        """
        from clickup_mcp.mcp_server.models.outputs.task import TaskListItem

        return TaskListItem(
            id=task.id,
            name=task.name,
            status=task.status,
            list_id=task.list_id,
            url=url,
        )
