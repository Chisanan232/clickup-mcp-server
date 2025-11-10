"""
List DTOs for ClickUp API requests and responses.

These DTOs handle serialization/deserialization of List data
for API interactions.
"""

from typing import Any, List, Dict

from pydantic import Field

from .base import BaseRequestDTO, BaseResponseDTO


class ListCreate(BaseRequestDTO):
    """DTO for creating a new list.

    POST /folder/{folder_id}/list
    https://developer.clickup.com/reference/createlist
    """

    name: str = Field(description="The name of the list")
    content: str | None = Field(default=None, description="The description of the list")
    due_date: int | None = Field(default=None, description="Due date in milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignee: int | None = Field(default=None, description="User ID to assign the list to")
    status: str | None = Field(default=None, description="Status of the list")


class ListUpdate(BaseRequestDTO):
    """DTO for updating an existing list.

    PUT /list/{list_id}
    """

    name: str | None = Field(default=None, description="The name of the list")
    content: str | None = Field(default=None, description="The description of the list")
    due_date: int | None = Field(default=None, description="Due date in milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    priority: int | None = Field(default=None, description="Priority level (1-5)")
    assignee: int | None = Field(default=None, description="User ID to assign the list to")
    status: str | None = Field(default=None, description="Status of the list")


class ListResp(BaseResponseDTO):
    """DTO for list API responses.

    Represents a list returned from the ClickUp API.
    """

    id: str = Field(description="The unique identifier for the list")
    name: str = Field(description="The name of the list")
    orderindex: int | None = Field(default=None, description="The order index of the list")
    status: str | None = Field(default=None, description="Status of the list")
    priority: int | None = Field(default=None, description="Priority level")
    assignee: Dict[str, Any] | None = Field(default=None, description="Assigned user")
    task_count: int | None = Field(default=None, description="Number of tasks in the list")
    due_date: int | None = Field(default=None, description="Due date in milliseconds")
    due_date_time: bool | None = Field(default=None, description="Whether due date includes time")
    start_date: int | None = Field(default=None, description="Start date in milliseconds")
    start_date_time: bool | None = Field(default=None, description="Whether start date includes time")
    folder: Dict[str, Any] | None = Field(default=None, description="The folder this list belongs to")
    space: Dict[str, Any] | None = Field(default=None, description="The space this list belongs to")
    content: str | None = Field(default=None, description="Description of the list")
    archived: bool = Field(default=False, description="Whether the list is archived")
