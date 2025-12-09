"""
List DTOs for ClickUp API requests and responses.

These DTOs provide serialization/deserialization helpers for List create, update,
and response shapes. Request DTOs inherit from `BaseRequestDTO` so `to_payload()`
excludes None values; response DTOs inherit from `BaseResponseDTO`.

Usage Examples:
    # Python - Create list payload
    from clickup_mcp.models.dto.list import ListCreate

    payload = ListCreate(name="Sprint Backlog", priority=2).serialize()
    # => {"name": "Sprint Backlog", "priority": 2}

    # Python - Update list payload
    from clickup_mcp.models.dto.list import ListUpdate

    update = ListUpdate(name="Sprint 14")
    # => {"name": "Sprint 14"}
"""

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "The name of the list"
PROPERTY_DUE_DATE_DESCRIPTION: str = "Due date in milliseconds"
PROPERTY_DUE_DATE_TIME_DESCRIPTION: str = "Whether due date includes time"
PROPERTY_STATUS_DESCRIPTION: str = "Status of the list"


class ListCreate(BaseRequestDTO):
    """
    DTO for creating a new list.

    API:
        POST /folder/{folder_id}/list
        Docs: https://developer.clickup.com/reference/createlist

    Attributes:
        name: List name
        content: Optional description
        due_date: Due date in epoch ms
        due_date_time: Whether due date includes time
        priority: Priority level (1-5)
        assignee: User ID to assign the list to
        status: Initial status label

    Examples:
        # Python
        ListCreate(name="Sprint Backlog", priority=2).to_payload()
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    content: str | None = Field(default=None, description="The description of the list")
    due_date: int | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignee: int | None = Field(default=None, description="User ID to assign the list to")
    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)


class ListUpdate(BaseRequestDTO):
    """
    DTO for updating an existing list.

    API:
        PUT /list/{list_id}

    Attributes:
        name: New list name
        content: New description
        due_date: New due date in epoch ms
        due_date_time: Whether due date includes time
        priority: New priority (1-5)
        assignee: New assignee user id
        status: New status label

    Examples:
        # Python
        ListUpdate(name="Sprint 14").to_payload()
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    content: str | None = Field(default=None, description="The description of the list")
    due_date: int | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignee: int | None = Field(default=None, description="User ID to assign the list to")
    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)


class ListResp(BaseResponseDTO):
    """
    DTO for list API responses.

    Represents a list returned from the ClickUp API with typed refs for user, folder, and space.

    Attributes:
        id: List ID
        name: List name
        orderindex: Order index
        status: Current status label
        priority: Priority level
        statuses: Effective statuses for this list (authoritative for task create/update)
        assignee: Assigned user
        task_count: Number of tasks in the list
        due_date: Due date in epoch ms
        due_date_time: Whether due date includes time
        start_date: Start date in epoch ms
        start_date_time: Whether start date includes time
        folder: Parent folder ref
        space: Parent space ref
        content: Description
        archived: Whether the list is archived

    Examples:
        # Python - Deserialize from API JSON
        ListResp.deserialize({"id": "lst_1", "name": "Sprint"})
    """

    id: str = Field(description="The unique identifier for the list")
    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    orderindex: int | None = Field(default=None, description="The order index of the list")
    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)
    priority: int | None = Field(default=None, description="Priority level")

    # Statuses defined for this list (authoritative for task create/update)
    class ListStatusDTO(BaseResponseDTO):
        name: str = Field(alias="status", description="Status name as configured on the list")
        type: str | None = Field(default=None, description="Status type (open/closed/active/done)")
        color: str | None = Field(default=None, description="UI color hex or token")
        orderindex: int | None = Field(default=None, description="Ordering index on the list")

    statuses: list[ListStatusDTO] | None = Field(
        default=None, description="List-level effective statuses. Present on GET /list/{list_id}."
    )

    # Lightweight typed refs
    class UserRef(BaseResponseDTO):
        id: int | str | None = Field(default=None)
        username: str | None = Field(default=None)

    class FolderRef(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)

    class SpaceRef(BaseResponseDTO):
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)

    assignee: UserRef | None = Field(default=None, description="Assigned user")
    task_count: int | None = Field(default=None, description="Number of tasks in the list")
    due_date: int | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    start_date: int | None = Field(default=None, description="Start date in milliseconds")
    start_date_time: bool | None = Field(default=None, description="Whether start date includes time")
    folder: FolderRef | None = Field(default=None, description="The folder this list belongs to")
    space: SpaceRef | None = Field(default=None, description="The space this list belongs to")
    content: str | None = Field(default=None, description="Description of the list")
    archived: bool = Field(default=False, description="Whether the list is archived")
