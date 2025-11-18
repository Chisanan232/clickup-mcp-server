"""
List DTOs for ClickUp API requests and responses.

These DTOs handle serialization/deserialization of List data
for API interactions.
"""

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO

PROPERTY_NAME_DESCRIPTION: str = "The name of the list"
PROPERTY_DUE_DATE_DESCRIPTION: str = "Due date in milliseconds"
PROPERTY_DUE_DATE_TIME_DESCRIPTION: str = "Whether due date includes time"
PROPERTY_STATUS_DESCRIPTION: str = "Status of the list"


class ListCreate(BaseRequestDTO):
    """DTO for creating a new list.

    POST /folder/{folder_id}/list
    https://developer.clickup.com/reference/createlist
    """

    name: str = Field(description=PROPERTY_NAME_DESCRIPTION)
    content: str | None = Field(default=None, description="The description of the list")
    due_date: int | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignee: int | None = Field(default=None, description="User ID to assign the list to")
    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)


class ListUpdate(BaseRequestDTO):
    """DTO for updating an existing list.

    PUT /list/{list_id}
    """

    name: str | None = Field(default=None, description=PROPERTY_NAME_DESCRIPTION)
    content: str | None = Field(default=None, description="The description of the list")
    due_date: int | None = Field(default=None, description=PROPERTY_DUE_DATE_DESCRIPTION)
    due_date_time: bool | None = Field(default=None, description=PROPERTY_DUE_DATE_TIME_DESCRIPTION)
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignee: int | None = Field(default=None, description="User ID to assign the list to")
    status: str | None = Field(default=None, description=PROPERTY_STATUS_DESCRIPTION)


class ListResp(BaseResponseDTO):
    """DTO for list API responses.

    Represents a list returned from the ClickUp API.
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
